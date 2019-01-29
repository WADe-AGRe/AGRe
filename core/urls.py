from django.conf.urls import url
from core import views as core_views

urlpatterns = [
    url(r'^accounts/signup/$', core_views.signup, name='signup'),
    url(r'^testDB/$', core_views.testGraphDb, name='testDB'),
    url(r'^accounts/interests/$', core_views.edit_interests, name='interests'),

    url(r'^resource/$', core_views.ResourceView.as_view(), name='resource_view'),

]
