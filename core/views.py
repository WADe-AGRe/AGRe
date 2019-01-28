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
from core.models import Interest, Resource
from core.forms import SignUpForm
from core.queries import RESOURCE_DETAILS_QUERY, sparql
from core.ontology import ArticleONT, AffiliationONT


def signup(request):
    import logging
    logging.basicConfig(filename='mylog.log', level=logging.DEBUG)

    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            logging.debug('form=%s', form.cleaned_data)
            user = form.save()
            user.refresh_from_db()  # load the profile instance created by the signal
            print(form.cleaned_data)
            logging.debug('form=%s', form.cleaned_data)
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


@require_GET()
def view_resource(request, id):
    logging.basicConfig(filename='mylog.log', level=logging.DEBUG)
    try:
        resource = Resource.objects.get(id=id)
    except Resource.DoesNotExist:
        logging.debug('Not found' + id)
        return HttpResponse(status=404)

    resource_details = {}

    sparql.setQuery(RESOURCE_DETAILS_QUERY.format(uri=resource.uri))

    ret = sparql.queryAndConvert()
    print(ret.variables)
    for binding in ret.bindings:
        if binding['prop'].value == ArticleONT.NAME.toPython():
            resource_details['name'] = binding['subj'].value

    return render(request, 'itempage.html', {'data': resource_details})
