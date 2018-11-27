from django.db import models
from django.db.models.fields.related import ForeignKey
from isbn_field.fields import ISBNField
from phonenumber_field.modelfields import PhoneNumberField
from schemaorgschemas.Thing import Action
from schemaorgschemas.Thing import CreativeWork
from schemaorgschemas.Thing import Organization as SOrganization
from schemaorgschemas.Thing import Person as SPerson
from schemaorgschemas.Thing.CreativeWork import Book as SBook
from schemaorgschemas.Thing.Intangible.Enumeration import BookFormatType


class BaseModel(models.Model):
    RESOURCE_NAME = 'baseModel'

    def get_absolute_url(self):
        return "/resource/%s/%s" % (self.RESOURCE_NAME, self.pk)


class Organization(BaseModel, SOrganization.OrganizationSchema):
    RESOURCE_NAME = 'organization'
    address = models.CharField(max_length=50)
    name = models.TextField()
    url = models.URLField(max_length=2000)
    telephone = PhoneNumberField(null=True, blank=True, unique=True)

    def __unicode__(self):
        return self.name

    class SchemaFields:
        name = SOrganization.nameProp
        address = SOrganization.addressProp
        url = SOrganization.urlProp
        telephone = SOrganization.telephoneProp


class Person(BaseModel, SPerson.PersonSchema):
    RESOURCE_NAME = 'person'
    first_name = models.CharField(max_length=40)
    last_name = models.CharField(max_length=40)
    email = models.EmailField()
    about = models.CharField(max_length=400)
    telephone = PhoneNumberField(null=True, blank=True, unique=True)
    affiliation = models.ForeignKey('Organization', on_delete=models.SET_NULL, blank=True, null=True,
                                    related_name='people')

    def __unicode__(self):
        return self.first_name + ' ' + self.last_name

    class SchemaFields:
        first_name = SPerson.givenNameProp()
        last_name = SPerson.familyNameProp()
        email = SPerson.emailProp()
        telephone = SPerson.telephoneProp()
        affiliation = SPerson.affiliationProp()


class Publisher(BaseModel, SOrganization.OrganizationSchema):
    RESOURCE_NAME = 'publisher'
    name = models.CharField(max_length=30)
    website = models.URLField()
    suddenly_stopped = models.DateTimeField(blank=True, null=True)

    def __unicode__(self):
        return self.name

    class SchemaFields():
        name = SOrganization.nameProp()
        website = SOrganization.urlProp()
        # a testing hack, there aren't any relevant publisher related datetime properties
        suddenly_stopped = Action.endTimeProp()


class Book(BaseModel, SBook.BookSchema):
    RESOURCE_NAME = 'book'
    isbn = ISBNField()
    title = models.CharField(max_length=100)
    authors = models.ManyToManyField('Person')
    book_format = models.TextField(choices=BookFormatType.BOOKFORMAT_CHOICES)
    publisher_field = ForeignKey('Publisher', on_delete=models.PROTECT, related_name='books')  # weird name due to clash
    publication_date = models.DateField(blank=True)
    family_friendly = models.BooleanField()
    copyright_year = models.IntegerField()

    def __unicode__(self):
        return self.title

    class SchemaFields:
        isbn = SBook.isbnProp
        authors = SBook.authorProp()
        title = SBook.headlineProp()
        book_format = BookFormatType.bookFormatProp()
        publisher_fk = SBook.publisherProp()
        publication_date = SBook.datePublishedProp()
        family_friendly = CreativeWork.isFamilyFriendlyProp()
        copyright_year = SBook.copyrightYearProp()


class Course(BaseModel, CreativeWork.CreativeWorkSchema):
    RESOURCE_NAME = 'course'
    course_code = models.CharField(max_length=20)
    about = models.CharField(max_length=50)
    name = models.CharField(max_length=50)

    def __unicode__(self):
        return "%s (%s)" % (self.name, self.course_code)

    class SchemaFields:
        about = CreativeWork.aboutProp
        name = CreativeWork.nameProp
