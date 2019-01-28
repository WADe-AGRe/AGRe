from django.conf.urls import url
from core import views as core_views

urlpatterns = [
    url(r'^accounts/signup/$', core_views.signup, name='signup'),
    url(r'^testDB/$', core_views.testGraphDb, name='testDB'),
    url(r'^accounts/interests/$', core_views.edit_interests, name='interests'),

    url(r'^resource/(?P<id>\w{1,50})/$', core_views.view_resource,name='resource_view' ),

]
