from django.conf.urls import include, url
from rest_framework.routers import SimpleRouter

from search import views

router = SimpleRouter()
router.register('', views.SearchResultViewSet, views.PersonViewSet)

urlpatterns = [
    url(r'^', include(router.urls)),
]
