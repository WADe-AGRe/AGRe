from django.conf.urls import url
from search import views as search_views

urlpatterns = [
    url(r'^$', search_views.main, name='main'),
    url(r'^course/$', search_views.course, name='course'),
]