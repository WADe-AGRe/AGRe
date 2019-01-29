from django.conf.urls import url
from core import views as core_views
from django.urls import path

urlpatterns = [
    url(r'^accounts/signup/$', core_views.signup, name='signup'),
    url(r'^testDB/$', core_views.testGraphDb, name='testDB'),
    url(r'^accounts/interests/$', core_views.edit_interests, name='interests'),

    url(r'^resource/$', core_views.ResourceView.as_view(), name='resource_view'),
    url(r'^review/$', core_views.send_review, name='review'),
    url(r'^ontology/', core_views.get_ontology, name='ontology'),
]
