import uuid

from django.db import models

class Contactable(models.Model):
    name = models.CharField(help_text="The name of the item.",
                             max_length=255)
    telephone = models.CharField(help_text="The telephone number.",
                             max_length=255)
    email = models.EmailField(help_text="Email address.")

    about = models.TextField(help_text="The subject matter of the content.", max_length=5000,
                            blank=False)

# https://schema.org/Organization
class Organization(Contactable):
    address = models.CharField(help_text="Physical address of the item.",
                             max_length=255)

# https://schema.org/Person
class Person(Contactable):
    jobTitle = models.CharField(help_text="The job title of the person (for example, Financial Manager).",
                             max_length=255)

# https://schema.org/CreativeWork
class CreativeWork(models.Model):
    name = models.CharField(help_text="The name of the item.",
                             max_length=255)
    about = models.TextField(help_text="The subject matter of the content.", max_length=5000,
                            blank=False)
    author = models.ForeignKey('Person', related_name='author',
                               on_delete=models.CASCADE, blank=True)
    keywords = models.TextField(help_text="Keywords or tags used to describe this content", max_length=5000)
    datePublished = models.DateTimeField(help_text="Date of first broadcast/publication.")
    image = models.ImageField(help_text="An image of the item")

# https://schema.org/Book
class Book(CreativeWork):
    bookFormat = models.CharField(help_text="https://schema.org/BookFormatType",
                             max_length=255)

# https://schema.org/CourseInstance
class CourseInstance(models.Model):
    courseMode = models.CharField(help_text='''The medium or means of delivery of the course instance or the mode of study, either as ''' +
    '''a text label (e.g. "online", "onsite" or "blended"; "synchronous" or "asynchronous"; "full-time" or "part-time")''',
                             max_length=255)
    instructor = models.ForeignKey('Person', related_name='instructor',
                               on_delete=models.CASCADE, blank=True)
    duration = models.CharField(help_text="	The duration of the item (movie, audio recording, event, etc.) .", max_length=255)
    location = models.CharField(help_text="The location of for example where the event is happening, an organization is located, or where an action takes place.", max_length=255)
    cost = models.CharField(help_text="Cost of taking the course, can be free", max_length=255)

# https://schema.org/Course
class Course(CreativeWork):
    courseCode = models.CharField(help_text="The identifier for the Course used by the course provider",
                             max_length=255)
    coursePrerequisites = models.TextField(help_text="Requirements for taking the Course.", max_length=5000)
    educationalCredentialAwarded = models.TextField(help_text="A description of the qualification, award, certificate, diploma or other educational credential " +
                                                              "awarded as a consequence of successful completion of this course.", max_length=5000)
    hasCourseInstance = models.ForeignKey('CourseInstance', related_name='CourseInstance',
                               on_delete=models.CASCADE)

# https://schema.org/WebPage
class WebPage(CreativeWork):
    significantLink = models.CharField(help_text="One of the more significant URLs on the page. Typically, these are the non-navigation links that are clicked " +
                                                 "on the most. Supersedes significantLinks.",
                             max_length=255)

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


