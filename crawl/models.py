from django.db import models
from djbase.models import FixedCharField, TrimmedCharField, BaseModel
from django.utils.translation import ugettext_lazy as _
from django.forms import model_to_dict
from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from .fields import JSONField


class ApiModel(object):
    def to_dict(self):
        '''
        Convert a model or a queryset into a dictionary or a list of dictionary
        :obj        : is a model or a queryset
        :returns    : dictionary
        '''
        if isinstance(self, BaseModel):
            return model_to_dict(self)
        else:
            return {}

    class Meta:
        abstract = True


class Country(BaseModel, ApiModel):

    code            = FixedCharField(max_length=2, primary_key=True)
    name            = TrimmedCharField(max_length=50)
    slug            = TrimmedCharField(max_length=50, unique=True, editable=False)

    class Meta:
        ordering = ['slug']
        verbose_name_plural = "Countries"

    def __unicode__(self):
        return self.name

class City(BaseModel, ApiModel):

    country             = models.ForeignKey(Country, on_delete=models.PROTECT, related_name="+", db_index=True)
    name                = TrimmedCharField(max_length=50)
    slug                = TrimmedCharField(max_length=50, unique=True, editable=False)

    def to_dict(self):
        d = super(City, self).to_dict()
        d['country'] = self.country.to_dict()
        d['slug'] = self.slug
        return d

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ['slug']
        verbose_name_plural = "Cities"


class CityWeatherMonth(BaseModel):

    MONTH_JANUARY       = 1
    MONTH_FEBRUARY      = 2
    MONTH_MARCH         = 3
    MONTH_APRIL         = 4
    MONTH_MAY           = 5
    MONTH_JUNE          = 6
    MONTH_JULY          = 7
    MONTH_AUGUST        = 8
    MONTH_SEPTEMBER     = 9
    MONTH_OCTOBER       = 10
    MONTH_NOVEMBER      = 11
    MONTH_DECEMBER      = 12

    MONTH_CHOICES = (
        (MONTH_JANUARY,     _("January")),
        (MONTH_FEBRUARY,    _("February")),
        (MONTH_MARCH,       _("March")),
        (MONTH_APRIL,       _("April")),
        (MONTH_MAY,         _("May")),
        (MONTH_JUNE,        _("June")),
        (MONTH_JULY,        _("July")),
        (MONTH_AUGUST,      _("August")),
        (MONTH_SEPTEMBER,   _("September")),
        (MONTH_OCTOBER,     _("October")),
        (MONTH_NOVEMBER,    _("November")),
        (MONTH_DECEMBER,    _("December")),
    )

    city                = models.ForeignKey("crawl.City", on_delete=models.PROTECT, db_index=False, related_name="+")
    month               = models.PositiveSmallIntegerField(choices=MONTH_CHOICES, validators=[MaxValueValidator(12),MinValueValidator(1)], default=1)
    sunlight            = models.PositiveSmallIntegerField(help_text="h/d")
    average_min         = models.PositiveSmallIntegerField(help_text="C")
    average_max         = models.PositiveSmallIntegerField(help_text="C")
    record_min          = models.PositiveSmallIntegerField(help_text="C")
    record_max          = models.PositiveSmallIntegerField(help_text="C")
    precipitations      = models.PositiveSmallIntegerField(help_text="mm")
    wet_days            = models.PositiveSmallIntegerField(validators=[MaxValueValidator(31),MinValueValidator(0)], default=0)
    sunrise_average     = models.PositiveSmallIntegerField(null=True, blank=True)
    sunset_average      = models.PositiveSmallIntegerField(null=True, blank=True)
    detail              = JSONField(null=True, blank=True)

    class Meta:
        unique_together = (
            ("city", "month"),
        )


class CrawlDetails(BaseModel):

    content_type    = models.ForeignKey(ContentType, on_delete=models.PROTECT, db_index=False, related_name="+", editable=False)
    object_id       = models.PositiveIntegerField(editable=False)
    data_type_name  = TrimmedCharField(max_length=50)
    source_url      = models.URLField(blank=True)
    content_object  = generic.GenericForeignKey('content_type', 'object_id')

    class Meta:
        unique_together = (
            ("object_id", "content_type", "data_type_name"),
        )