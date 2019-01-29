from AGRe import setup

setup()

from core.models import Resource

# Resource.objects.all().delete()


def add_resource(resource_uri, resource_type):
    Resource.objects.get_or_create(uri=resource_uri, type=resource_type)
