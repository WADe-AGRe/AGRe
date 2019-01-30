# Create your views here.
import json
import logging

from SPARQLWrapper import SPARQLWrapper, JSON
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.http import require_GET, require_POST

from AGRe.settings import GRAPHDB_APIKEY, GRAPHDB_SECRET, GRAPHDB_URL
from core.models import Interest, Resource, Review, Profile, Course
from core.forms import SignUpForm, ReviewForm
from core.queries import RESOURCE_DETAILS_QUERY, query_graph, insert_graph, INSERT_QUERY, DELETE_REVIEW_QUERY
from core.ontology import ArticleONT, PublisherONT, USER_NS, LIKES_URI, DISLIKES_URI
from django.views import View

from django.db import close_old_connections


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

            courses = Course.objects.all()
            return redirect('accounts/profile')
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
            try:
                print(id)
                course = Course.objects.get(pk=id)
                print(course)
                user.profile.courses.add(course)
                interests = course.tags
                print(interests)
                # for tag in interests:
                #     user.profile.interests.add(tag)
            except Exception as ex:
                print(ex)
                pass

        user.save()
        return JsonResponse({'error':'none'})
    else:
        data = dict()
        data['username'] = request.user.username
        data['courses'] = Course.objects.all()
        data['is_student'] = request.user.profile.is_student

    return render(request, 'profile.html', {'data': data })


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
        return JsonResponse({'error':'none'})

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
            print(binding)
            prop = binding['prop'].value
            if prop == ArticleONT.NAME.toPython():
                resource_details['name'] = self.get_binding_name(binding, "subj", "name")
            elif prop == ArticleONT.CATEGORY.toPython():
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
            logging.debug('Not found' + id)
            return HttpResponse(status=404)

        resource_details = self.get_resource_info(resource)
        resource_reviews = self.get_resource_reviews(resource)
        print(resource_reviews)
        return render(request, 'itempage.html', {'resource': resource_details, 'reviews': resource_reviews})


@login_required
@require_POST
def send_review(request):
    def add_review_graph(rating):
        if rating > 2:
            predicate = LIKES_URI
        else:
            predicate = DISLIKES_URI
        query = INSERT_QUERY.format(graph='likes', subject=USER_NS[request.user.username], predicate=predicate,
                                    object=review.item.uri)
        insert_graph.setQuery(query)
        insert_graph.setMethod('POST')
        insert_graph.query()

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
    SELECT_QUERY = """
        select ?p ?o WHERE {{
            <{subject}> ?p ?o.
        }} limit 100 
    """
    query_graph.setQuery(SELECT_QUERY.format(subject=good_url))
    ret = query_graph.query()
    data = []
    for binding in ret.bindings:
        p_is_uri = True if binding['p'].type == 'uri' else False
        o_is_uri = True if binding['o'].type == 'uri' else False
        data.append((binding['p'].value, p_is_uri, binding['o'].value, o_is_uri,))

    return render(request, 'ontology.html', {'data': data})
