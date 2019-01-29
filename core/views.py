# Create your views here.
import json
import logging

from SPARQLWrapper import SPARQLWrapper, JSON
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views.decorators.http import require_GET

from AGRe.settings import GRAPHDB_APIKEY, GRAPHDB_SECRET
from core.models import Interest, Resource, Review, Profile
from core.forms import SignUpForm, ReviewForm
from core.queries import RESOURCE_DETAILS_QUERY, sparql
from core.ontology import ArticleONT, AffiliationONT
from django.views import View


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
            return redirect('home')
    else:
        form = SignUpForm()
    return render(request, 'registration/signup.html', {'form': form})


@require_GET
def testGraphDb(request):
    sparql = SPARQLWrapper("https://rdf.ontotext.com/4234582382/agre-graphdb/repositories/agre")
    sparql.setCredentials(GRAPHDB_APIKEY, GRAPHDB_SECRET)
    sparql.setQuery("""SELECT * WHERE { ?s ?p ?o } LIMIT 10""")
    sparql.setReturnFormat(JSON)
    response = sparql.query().convert()
    result = response["results"]["bindings"]
    html = '<html><body><ul>'
    print(result)
    for each in result:
        html += '<li>' + str(each) + '</li>'
    html += '</ul></body></html>'
    return HttpResponse(html)


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

        sparql.setQuery(RESOURCE_DETAILS_QUERY.format(uri=resource.uri))

        ret = sparql.queryAndConvert()
        print(ret.variables)
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
        resource_details['empty_stars'] = (5 - int(rating)) * '*'
        resource_details['half_star'] = True if rating - int(rating) >= 0.25 else False
        resource_details['type'] = resource.get_type_display().lower()
        return resource_details

    def get_resource_reviews(self, resource):
        reviews = Review.objects.filter(item=resource).order_by(desc(Review.i))

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

        return render(request, 'itempage.html', {'resource': resource_details, 'reviews': resource_reviews})

@login_required
@require_POST
def send_review(request):
    logging.basicConfig(filename='mylog.log', level=logging.DEBUG)

    form = ReviewForm(request.POST)

    if form.is_valid():
        review = Review.objects.filter(item=form.cleaned_data.get('item'), reviewer=request.user.id)

        if review is None or len(review) is 0:
            review = form.save(commit=False)
            review.reviewer = request.user
            review.item = form.cleaned_data.get('item')
            review.save()
        else:
            review.update(comment=form.cleaned_data.get('comment'), rating=form.cleaned_data.get('rating'))

        return HttpResponseRedirect('/resource?id={0}'.format(form.cleaned_data.get('item').id))
    else:
        return render(request, '/resources', {'form': form})
