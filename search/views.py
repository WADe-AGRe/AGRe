from search import rdf_utils

from django.shortcuts import render
from django.http import HttpResponse

from django import forms

class NameForm(forms.Form):
    your_name = forms.CharField(label='Your name', max_length=100)

PAGE_SIZE = 12

def parse_req_for_pag(request, context=None):
    if context is None:
        context = dict()
    if 'size' in request.GET:
        size = int(request.GET['size'])
    else:
        size = PAGE_SIZE

    if 'page' in request.GET:
        page = int(request.GET['page'])
    else:
        page = 1

    start_page_list = max(page - 2, 1)
    display_pages = list(range(start_page_list, start_page_list+5))
    context['display_pages'] = display_pages

    offset = size * page
    return context, size, page, offset

# Create your views here.
def main(request):
    context, size, page, offset = parse_req_for_pag(request)

    if 'q' in request.GET:
        context['q'] = request.GET['q']
        query = request.GET['q']
    else:
        query = ''

    course_results  = rdf_utils.find_courses(query, limit=size//3, offset=offset )
    article_results = rdf_utils.find_articles(query, limit=size//3, offset=offset )
    book_results    = rdf_utils.find_books(query, limit=size-(2*(size//3)), offset=offset )
    search_results = course_results + article_results + book_results
    search_results.sort(key=lambda res: res.name)

    context['search_results'] = search_results
    return render(request, 'search/index.html', context)

def course(request):
    context, size, page, offset = parse_req_for_pag(request)

    if 'q' in request.GET:
        context['q'] = request.GET['q']
        search_results = rdf_utils.find_courses(request.GET['q'], limit=size, offset=offset )
    else:
        search_results = rdf_utils.find_courses(limit=size, offset=offset)

    context['search_results'] = search_results
    return render(request, 'search/index.html', context)

def book(request):
    context, size, page, offset = parse_req_for_pag(request)

    if 'q' in request.GET:
        context['q'] = request.GET['q']
        search_results = rdf_utils.find_books(request.GET['q'], limit=size, offset=offset )
    else:
        search_results = rdf_utils.find_books(limit=size, offset=offset)

    context['search_results'] = search_results
    return render(request, 'search/index.html', context)

def article(request):
    context, size, page, offset = parse_req_for_pag(request)

    if 'q' in request.GET:
        context['q'] = request.GET['q']
        search_results = rdf_utils.find_articles(request.GET['q'], limit=size, offset=offset )
    else:
        search_results = rdf_utils.find_articles(limit=size, offset=offset)

    context['search_results'] = search_results
    return render(request, 'search/index.html', context)