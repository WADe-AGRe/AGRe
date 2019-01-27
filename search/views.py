from django.shortcuts import render
from django.http import HttpResponse

from django import forms

class NameForm(forms.Form):
    your_name = forms.CharField(label='Your name', max_length=100)

# Create your views here.
def index(request):
    return render(request, 'search/index.html')