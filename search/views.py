import datetime

from django.utils.decorators import method_decorator
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, mixins
# noinspection PyDeprecation
from rest_framework.decorators import detail_route, list_route
from rest_framework.filters import OrderingFilter
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response

from search import serializers
from search.models import SearchResult
from drf_yasg import openapi
from drf_yasg.app_settings import swagger_settings
from drf_yasg.inspectors import CoreAPICompatInspector, FieldInspector, NotHandled, SwaggerAutoSchema
from drf_yasg.utils import no_body, swagger_auto_schema


class DjangoFilterDescriptionInspector(CoreAPICompatInspector):
    def get_filter_parameters(self, filter_backend):
        if isinstance(filter_backend, DjangoFilterBackend):
            result = super(DjangoFilterDescriptionInspector, self).get_filter_parameters(filter_backend)
            for param in result:
                if not param.get('description', ''):
                    param.description = "Filter the returned list by {field_name}".format(field_name=param.name)

            return result

        return NotHandled


class NoSchemaTitleInspector(FieldInspector):
    def process_result(self, result, method_name, obj, **kwargs):
        # remove the `title` attribute of all Schema objects
        if isinstance(result, openapi.Schema.OR_REF):
            # traverse any references and alter the Schema object in place
            schema = openapi.resolve_ref(result, self.components)
            schema.pop('title', None)

            # no ``return schema`` here, because it would mean we always generate
            # an inline `object` instead of a definition reference

        # return back the same object that we got - i.e. a reference if we got a reference
        return result


class NoTitleAutoSchema(SwaggerAutoSchema):
    field_inspectors = [NoSchemaTitleInspector] + swagger_settings.DEFAULT_FIELD_INSPECTORS


class NoPagingAutoSchema(NoTitleAutoSchema):
    def should_page(self):
        return False


class ArticlePagination(LimitOffsetPagination):
    default_limit = 5
    max_limit = 25


@method_decorator(name='retrieve', decorator=swagger_auto_schema(
    operation_description="description from swagger_auto_schema via method_decorator",
    filter_inspectors=[DjangoFilterDescriptionInspector]
))
class SearchResultViewSet(mixins.RetrieveModelMixin,
                          viewsets.GenericViewSet):
    """
    ArticleViewSet class docstring

    retrieve:
    retrieve class docstring

    destroy:
    destroy class docstring

    partial_update:
    partial_update class docstring
    """
    queryset = SearchResult.objects.all()
    lookup_field = 'slug'
    lookup_value_regex = r'[a-z0-9]+(?:-[a-z0-9]+)'
    serializer_class = serializers.SearchResultSerializer

    pagination_class = ArticlePagination
    filter_backends = (DjangoFilterBackend, OrderingFilter)
    filter_fields = ('title',)
    ordering_fields = ('date_modified', 'date_created')
    ordering = ('date_created',)

    swagger_schema = NoTitleAutoSchema
