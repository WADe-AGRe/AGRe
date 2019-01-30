# Create your views here.
import json
import logging

from SPARQLWrapper import SPARQLWrapper, JSON
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.views.decorators.http import require_GET, require_POST

from AGRe.settings import GRAPHDB_APIKEY, GRAPHDB_SECRET
from core.models import Interest, Resource, Review, Profile, Course
from core.forms import SignUpForm, ReviewForm
from core.queries import RESOURCE_DETAILS_QUERY, query_graph, insert_graph, INSERT_QUERY, DELETE_REVIEW_QUERY
from core.ontology import ArticleONT, AffiliationONT, USER_NS, LIKES_URI, DISLIKES_URI
from django.views import View

from rdflib import URIRef


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

            return redirect('accounts/profile')
    else:
        form = SignUpForm()
    return render(request, 'registration/signup.html', {'form': form})


@login_required
def signup_extended(request):
    if request.method == 'POST':
        return redirect('home')
    else:
        data = dict()
        data['username'] = request.user.username
        data['courses'] = Course.objects.all()
        data['is_student'] = request.user.profile.is_student

        interests = Interest.objects.all()
        user_interests = request.user.profile.interests.all()

        for i in user_interests:
            [o for o in interests if o.id == i.id][0].selected = True

    return render(request, 'profile.html', {'data': data, 'interests': interests })


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
        return HttpResponse(status=200)


class ResourceView(View):

    def get_resource_info(self, resource):

        subjects = []
        authors = []
        resource_details = {'subjects': subjects, 'authors': authors}

        query_graph.setQuery(RESOURCE_DETAILS_QUERY.format(uri=resource.uri))
        query_graph.setMethod('GET')

        ret = query_graph.queryAndConvert()
        for binding in ret.bindings:
            prop = binding['prop'].value
            if prop == ArticleONT.NAME.toPython():
                resource_details['name'] = binding['subj'].value
            elif prop == ArticleONT.SUBJECT.toPython():
                subjects.append(binding['name'].value.replace('+', ' '))
            elif prop == ArticleONT.ISSN.toPython():
                resource_details['issn'] = binding['subj'].value
            elif prop == ArticleONT.AFFILIATION.toPython():
                resource_details['affiliation'] = binding['name'].value
            elif prop == ArticleONT.URL.toPython():
                resource_details['url'] = binding['subj'].value
            elif prop == ArticleONT.AUTHOR.toPython():
                authors.append(binding['name'].value)
            elif prop == ArticleONT.PUBLICATION.toPython():
                resource_details['publication'] = binding['subj'].value

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

        insert_graph.setQuery(
            INSERT_QUERY.format(graph='likes', subject=USER_NS[request.user.username], predicate=predicate,
                                object=review.item.uri))
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
