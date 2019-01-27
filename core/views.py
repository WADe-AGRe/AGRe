# Create your views here.
from SPARQLWrapper import SPARQLWrapper, JSON
from django.contrib.auth import login, authenticate
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views.decorators.http import require_GET

from AGRe.settings import GRAPHDB_APIKEY, GRAPHDB_SECRET
from .forms import SignUpForm


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
