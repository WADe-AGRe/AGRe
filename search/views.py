from search import rdf_utils

from django.shortcuts import render
from django.http import HttpResponse

from django import forms

class NameForm(forms.Form):
    your_name = forms.CharField(label='Your name', max_length=100)

# Create your views here.
def main(request):
    search_results = rdf_utils.find_courses('data')
    return render(request, 'search/index.html', {'search_results':search_results})

def course(request):
    search_results = rdf_utils.find_courses()
    return render(request, 'search/index.html', {'search_results':search_results})