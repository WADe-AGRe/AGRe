# Create your views here.
import json
import logging
import random

from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db import close_old_connections
from django.http import HttpResponse
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from core.forms import ReviewForm
from core.models import Interest, Resource, Review, Course
from core.ontology import ArticleONT, USER_NS, LIKES_URI, DISLIKES_URI, TAGS_NS
from core.queries import RESOURCE_DETAILS_QUERY, query_graph, insert_graph, INSERT_QUERY, DELETE_REVIEW_QUERY
from .forms import SignUpForm


def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.refresh_from_db()
            user.profile.is_professor = form.cleaned_data.get('is_professor')
            user.profile.is_student = form.cleaned_data.get('is_student')
            user.save()
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=user.username, password=raw_password)
            login(request, user)

            return redirect('profile')
    else:
        form = SignUpForm()
    return render(request, 'registration/signup.html', {'form': form})


@login_required
def signup_extended(request):
    if request.method == 'POST':
        user = request.user

        data = json.loads(request.body)
        courses = data.get('ids', [])
        bio = data.get('bio', '')
        year = data.get('year', '')

        user.profile.year = year
        user.profile.bio = bio
        for id in courses:
            course = Course.objects.get(pk=id)
            user.profile.courses.add(course)
            interests = course.tags.all()
            for tag in interests:
                user.profile.interests.add(tag)

        user.save()
        return JsonResponse({'error': 'none'})
    else:
        data = dict()
        data['username'] = request.user.username
        data['courses'] = Course.objects.all()
        data['is_student'] = request.user.profile.is_student

    return render(request, 'profile.html', {'data': data})


@login_required
def edit_interests(request):
    logging.basicConfig(filename='mylog.log', level=logging.DEBUG)
    if request.method == 'GET':
        user = request.user
        interests = Interest.objects.all()
        user_interests = user.profile.interests.all()

        for i in user_interests:
            [o for o in interests if o.id == i.id][0].selected = True

        return render(request, 'interests.html', {'interests': interests})

    elif request.method == 'POST':
        user = request.user
        data = json.loads(request.body).get('ids', [])

        user.profile.interests.clear()

        for id in data:
            try:
                user.profile.interests.add(Interest.objects.get(pk=id))
            except Exception as ex:
                pass

        user.save()
        return JsonResponse({'error': 'none'})


class ResourceView(View):

    def get_binding_name(self, binding, key1, key2):
        if binding[key1].type == 'uri':
            return binding[key2].value
        return binding[key1].value

    def get_resource_info(self, resource):

        subjects = []
        authors = []
        resource_details = {'subjects': subjects, 'authors': authors}

        query_graph.setQuery(RESOURCE_DETAILS_QUERY.format(uri=resource.uri))
        query_graph.setMethod('GET')

        ret = query_graph.queryAndConvert()
        print(ret.variables)
        for binding in ret.bindings:
            prop = binding['prop'].value
            if prop == ArticleONT.NAME.toPython():
                resource_details['name'] = self.get_binding_name(binding, "subj", "name")
            elif prop == ArticleONT.TAGS.toPython():
                subjects.append(self.get_binding_name(binding, "subj", "name").replace('+', ' '))
            elif prop == ArticleONT.ISSN.toPython():
                resource_details['issn'] = self.get_binding_name(binding, "subj", "name")
            elif prop == ArticleONT.PUBLISHER.toPython():
                resource_details['publisher'] = self.get_binding_name(binding, "subj", "name")
            elif prop == ArticleONT.URL.toPython():
                resource_details['url'] = self.get_binding_name(binding, "subj", "name")
            elif prop == ArticleONT.AUTHOR.toPython():
                authors.append(self.get_binding_name(binding, "subj", "name"))
            elif prop == ArticleONT.PUBLICATION.toPython():
                resource_details['publication'] = self.get_binding_name(binding, "subj", "name")
            elif prop == ArticleONT.DESCRIPTION.toPython():
                resource_details['description'] = self.get_binding_name(binding, "subj", "name")

        rating = resource.rating
        resource_details['stars'] = int(rating) * '*'
        resource_details['half_star'] = True if rating - int(rating) >= 0.25 else False
        resource_details['empty_stars'] = (5 - int(rating) - int(resource_details['half_star'])) * '*'
        resource_details['type'] = resource.get_type_display().lower()
        return resource_details

    def get_resource_reviews(self, resource):
        reviews = Review.objects.filter(item=resource).order_by('-insert_date')
        return reviews

    def get(self, request):
        close_old_connections()
        id = request.GET.get('id', 0)
        logging.basicConfig(filename='mylog.log', level=logging.DEBUG)
        try:
            resource = Resource.objects.get(id=id)
        except Resource.DoesNotExist:
            return HttpResponse(status=404)

        resource_details = self.get_resource_info(resource)
        resource_reviews = self.get_resource_reviews(resource)
        print(resource_reviews)
        return render(request, 'itempage.html', {'resource': resource_details, 'reviews': resource_reviews})


@login_required
@require_POST
@csrf_exempt
def send_review(request):
    def add_review_graph(rating):
        if rating > 2:
            predicate = LIKES_URI
        else:
            predicate = DISLIKES_URI

        query = INSERT_QUERY.format(graph='reviews', subject=USER_NS[request.user.username], predicate=predicate,
                                    object=review.item.uri)
        insert_graph.setQuery(query)
        insert_graph.setMethod('POST')
        insert_graph.query()

        # update_query = UPDATE_REVIEW_QUERY.format(graph='reviews', subject=review.item.uri, predicate=RATING_URI,
        #                                           value=int(review.item.rating))
        # print(update_query)
        # insert_graph.setQuery(update_query)
        # insert_graph.setMethod('POST')
        # insert_graph.query()

    def delete_review_graph():
        insert_graph.setQuery(DELETE_REVIEW_QUERY.format(user=USER_NS[request.user.username], resource=review.item.uri))
        insert_graph.setMethod('POST')
        insert_graph.query()

    logging.basicConfig(filename='mylog.log', level=logging.DEBUG)

    form = ReviewForm(request.POST)

    if form.is_valid():
        review = Review.objects.filter(item=form.cleaned_data.get('item'), reviewer=request.user.id).first()

        if review is None:
            review = form.save(commit=False)
            review.reviewer = request.user
            review.item = form.cleaned_data.get('item')
            review.save()
            add_review_graph(review.rating)
        else:
            review.comment = form.cleaned_data.get('comment')
            review.is_anonymous = form.cleaned_data.get('is_anonymous')
            review.rating = form.cleaned_data.get('rating')
            review.save()

            delete_review_graph()
            add_review_graph(review.rating)

        return HttpResponseRedirect('/resource?id={0}'.format(form.cleaned_data.get('item').id))
    else:
        return render(request, '/resources', {'form': form})


def get_ontology(request):
    good_url = request.build_absolute_uri().replace('http://localhost:8000/', 'https://agre.herokuapp.com/')
    SUBJECT_QUERY = """
        select ?p ?o WHERE {{
            <{subject}> ?p ?o.
        }} limit 100 
    """
    OBJECT_QUERY = """
        select ?s ?p WHERE {{
            ?s ?p <{object}>.
        }} limit 100 
    """
    query_graph.setQuery(SUBJECT_QUERY.format(subject=good_url))
    ret = query_graph.query()
    values = []
    for binding in ret.bindings:
        p_is_uri = True if binding['p'].type == 'uri' else False
        o_is_uri = True if binding['o'].type == 'uri' else False
        values.append((binding['p'].value, p_is_uri, binding['o'].value, o_is_uri,))

    query_graph.setQuery(OBJECT_QUERY.format(object=good_url))
    ret = query_graph.query()
    subjects = []
    for binding in ret.bindings:
        p_is_uri = True if binding['s'].type == 'uri' else False
        o_is_uri = True if binding['p'].type == 'uri' else False
        subjects.append((binding['s'].value, p_is_uri, binding['p'].value, o_is_uri,))

    return render(request, 'ontology.html', {'values': values, 'subjects': subjects})


class HomepageView(LoginRequiredMixin, View):
    TAGS_QUERY = """PREFIX sch: <https://schema.org/>

        select distinct ?other ?name ?author_name ?description ?url  where {{
            
            ?other sch:name ?name .
            ?other sch:author ?author .
            ?author sch:name ?author_name.
            OPTIONAL {{
                    ?other sch:description ?description .
                }}
            ?other sch:url ?url .
                ?other sch:keywords ?tag .
            FILTER (?tag IN ({tag_set}))
        }}
        limit 30 
    """

    CF_QUERY = """PREFIX sch: <https://schema.org/>
        select distinct ?other_user ?other ?name ?author_name ?description ?url  where {{ 
            ?user sch:likes ?first .
            ?user sch:dislikes ?bad .
            ?other_user sch:likes ?first .
            ?other_user sch:dislikes ?bad .
            
            ?other sch:name ?name .
            ?other sch:author ?author .
            ?author sch:name ?author_name.
            OPTIONAL {{
                ?other sch:description ?description .
            }}
            ?other sch:url ?url .
            ?other_user sch:likes ?other .
            MINUS {{
                ?user ?prop ?other .
            }}
         Filter(?user=<{username}>)
}} limit 30"""

    def get_tag_resource(self, username):
        profile = User.objects.get(username=username).profile
        skills = profile.interests.values_list('name', flat=True)
        skill_set = ', '.join(map(lambda x: '<{}>'.format(TAGS_NS[x]), skills))
        query = self.TAGS_QUERY.format(tag_set=skill_set)
        print(query)
        query_graph.setQuery(query)
        query_graph.setMethod('GET')
        ret = query_graph.query()

        recommended_articles = []
        for binding in ret.bindings:
            resource = Resource.objects.get(uri=binding['other'].value)
            article_data = {
                'name': binding['name'].value,
                'author': binding['author_name'].value,
                'description': binding.get('description').value if binding.get(
                    'description') is not None else 'No description provided',
                'url': binding['url'].value,
                'rating': resource.rating,
                'reviewcomment': resource.reviews.first().comment if resource.reviews.first() is not None else 'No reviews',
                'type': resource.get_type_display().lower(),
                'id': resource.id
            }
            recommended_articles.append(article_data)
        return recommended_articles

    def get_resources(self, username):
        recommended_articles = self.get_tag_resource(username)
        query = self.CF_QUERY.format(username=USER_NS[username])
        query_graph.setQuery(query)
        query_graph.setMethod('GET')
        ret = query_graph.query()

        similar_users = []
        user_set = set()
        for binding in ret.bindings:
            username = binding['other_user'].value.split('/')[-1]
            user_set.add(username)
            resource = Resource.objects.get(uri=binding['other'].value)
            article_data = {
                'name': binding['name'].value,
                'author': binding['author_name'].value,
                'description': binding.get('description').value if binding.get(
                    'description') is not None else 'No description provided',
                'url': binding['url'].value,
                'rating': resource.rating,
                'reviewcomment': resource.reviews.first().comment,
                'type': resource.get_type_display().lower(),
                'id': resource.id
            }
            recommended_articles.append(article_data)
        print(user_set)
        for username in user_set:
            profile = User.objects.get(username=username).profile
            user_data = {
                'name': profile.get_full_name,
                'email': profile.user.email,
                'skills': list(profile.interests.values_list('name', flat=True)),
                'bio': profile.bio,
                'is_professor': profile.is_professor,
                'username': username
            }
            similar_users.append(user_data)

        return similar_users, sorted(recommended_articles, key=lambda x: x['rating'], reverse=True)

    def get(self, request):

        page = request.GET.get('page', 1)
        if page == 1:
            similar_users, recommended_resources = self.get_resources(request.user.username)
            request.session['similar_users'] = similar_users
            request.session['recommended_resources'] = recommended_resources
        else:
            similar_users = request.session['similar_users']
            recommended_resources = request.session['recommended_resources']

        random.shuffle(similar_users)
        print(similar_users)
        paginator = Paginator(recommended_resources, 4)
        try:
            page_resources = paginator.page(page)
        except PageNotAnInteger:
            page_resources = paginator.page(1)
        except EmptyPage:
            page_resources = paginator.page(paginator.num_pages)

        return render(request, "home.html", {'users': similar_users[:4], 'resources': page_resources})
