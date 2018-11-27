from rest_framework import viewsets, mixins

from .models import Person, Course, Book, Organization, Publisher
from .serializers import PersonSerializer, CourseSerializer, BookSerializer, OrganizationSerializer, PublisherSerializer


class PersonViewSet(mixins.CreateModelMixin,
                    mixins.RetrieveModelMixin,
                    mixins.UpdateModelMixin,
                    mixins.DestroyModelMixin,
                    viewsets.GenericViewSet):
    model = Person
    queryset = Person.objects
    serializer_class = PersonSerializer


class CourseViewSet(mixins.CreateModelMixin,
                    mixins.RetrieveModelMixin,
                    mixins.UpdateModelMixin,
                    mixins.DestroyModelMixin,
                    viewsets.GenericViewSet):
    model = Course
    queryset = Course.objects
    serializer_class = CourseSerializer


class BookViewSet(mixins.CreateModelMixin,
                  mixins.RetrieveModelMixin,
                  mixins.UpdateModelMixin,
                  mixins.DestroyModelMixin,
                  viewsets.GenericViewSet):
    model = Book
    queryset = Book.objects
    serializer_class = BookSerializer


class OrganizationViewSet(mixins.CreateModelMixin,
                          mixins.RetrieveModelMixin,
                          mixins.UpdateModelMixin,
                          mixins.DestroyModelMixin,
                          viewsets.GenericViewSet):
    model = Organization
    queryset = Organization.objects
    serializer_class = OrganizationSerializer


class PublisherViewSet(mixins.CreateModelMixin,
                       mixins.RetrieveModelMixin,
                       mixins.UpdateModelMixin,
                       mixins.DestroyModelMixin,
                       viewsets.GenericViewSet):
    model = Publisher
    queryset = Publisher.objects
    serializer_class = PublisherSerializer
