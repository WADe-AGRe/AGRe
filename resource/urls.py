from django.conf.urls import include, url
from rest_framework.routers import SimpleRouter

from .views import BookViewSet, CourseViewSet, PublisherViewSet, PersonViewSet, OrganizationViewSet

router = SimpleRouter()
router.register('book', BookViewSet)
router.register('course', CourseViewSet)
router.register('publisher', PublisherViewSet)
router.register('person', PersonViewSet)
router.register('organization', OrganizationViewSet)

urlpatterns = [
    url(r'^', include(router.urls)),
]
