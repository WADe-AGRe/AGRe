from rest_framework import viewsets

from .models import Person, Course, Book, Organization, Publisher
from .serializers import PersonSerializer, CourseSerializer, BookSerializer, OrganizationSerializer, PublisherSerializer


class PersonViewSet(viewsets.ModelViewSet):
    model = Person
    queryset = Person.objects
    serializer_class = PersonSerializer


class CourseViewSet(viewsets.ModelViewSet):
    model = Course
    queryset = Course.objects
    serializer_class = CourseSerializer


class BookViewSet(viewsets.ModelViewSet):
    model = Book
    queryset = Book.objects
    serializer_class = BookSerializer


class OrganizationViewSet(viewsets.ModelViewSet):
    model = Organization
    queryset = Organization.objects
    serializer_class = OrganizationSerializer


class PublisherViewSet(viewsets.ModelViewSet):
    model = Publisher
    queryset = Publisher.objects
    serializer_class = PublisherSerializer
