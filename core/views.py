# Create your views here.
from SPARQLWrapper import SPARQLWrapper, JSON
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views.decorators.http import require_GET
from AGRe.settings import GRAPHDB_APIKEY, GRAPHDB_SECRET

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'signup.html', {'form': form})


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
