from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers

from search.models import SearchResult


class SearchResultSerializer(serializers.ModelSerializer):
    references = serializers.DictField(
        help_text=_("this is a really bad example"),
        child=serializers.URLField(help_text="but i needed to test these 2 fields somehow"),
        read_only=True,
    )
    uuid = serializers.UUIDField(help_text="should searches have UUIDs?", read_only=True)
    cover_name = serializers.FileField(use_url=False, source='cover', required=True)

    class Meta:
        model = SearchResult
        fields = ('title', 'author', 'body', 'slug', 'date_created', 'date_modified',
                  'references', 'uuid', 'cover', 'cover_name', 'search_type', )
        read_only_fields = ('date_created', 'date_modified',
                            'references', 'uuid', 'cover_name')
        lookup_field = 'slug'
        extra_kwargs = {
            'body': {'help_text': 'body serializer help_text'},
            'author': {
                'default': serializers.CurrentUserDefault(),
                'help_text': _("The ID of the user that created this search; if none is provided, "
                               "defaults to the currently logged in user.")
            },
        }

