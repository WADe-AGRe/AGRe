from django.db import models


class SearchResult(models.Model):
    title = models.CharField(help_text="query for which the model was made", max_length=255, blank=False, unique=True)
    body = models.TextField(help_text="search model help_text", max_length=5000, blank=False)
    slug = models.SlugField(help_text="slug model help_text", unique=True, blank=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    author = models.ForeignKey('auth.User', related_name='searches', on_delete=models.CASCADE)
    search_type = models.PositiveSmallIntegerField(
        help_text="IntegerField declared on model with choices=(...) and exposed via ModelSerializer",
        choices=((1, "first"), (2, "second"), (3, "third"), (7, "seven"), (8, "eight")), null=True
    )

    cover = models.ImageField(upload_to='search/original/', blank=True)
