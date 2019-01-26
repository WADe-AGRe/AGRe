from django.conf.urls import url
from core import views as core_views

urlpatterns = [
    url(r'^signup/$', core_views.signup, name='signup'),
    url(r'^testDB/$', core_views.testGraphDb, name='testDB')
]