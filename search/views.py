from search import rdf_utils

from django.shortcuts import render
from django.http import HttpResponse

from django import forms

class NameForm(forms.Form):
    your_name = forms.CharField(label='Your name', max_length=100)

# Create your views here.
def main(request):
    context = dict()
    if 'q' in request.GET:
        context['q'] = request.GET['q']
        search_results = rdf_utils.find_courses(request.GET['q'])
    else:
        search_results = rdf_utils.find_courses()
    context['search_results'] = search_results
    return render(request, 'search/index.html', context)

def course(request):
    context = dict()
    if 'q' in request.GET:
        context['q'] = request.GET['q']
        search_results = rdf_utils.find_courses(request.GET['q'])
    else:
        search_results = rdf_utils.find_courses()
    context['search_results'] = search_results
    return render(request, 'search/index.html', context)