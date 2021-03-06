from django.db import models
from djbase.models import FixedCharField, TrimmedCharField, BaseModel
from django.utils.translation import ugettext_lazy as _
from django.forms import model_to_dict
from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from .fields import JSONField, HTMLField


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
    sunlight            = models.PositiveSmallIntegerField(null=True, blank=True, help_text="h/d", verbose_name="Sunlight (h/d)")
    average_min         = models.PositiveSmallIntegerField(null=True, blank=True, help_text="*C", verbose_name="Average T min (*C)")
    average_max         = models.PositiveSmallIntegerField(null=True, blank=True, help_text="*C", verbose_name="Average T max (*C)")
    record_min          = models.PositiveSmallIntegerField(null=True, blank=True, help_text="*C", verbose_name="Record T min (*C)")
    record_max          = models.PositiveSmallIntegerField(null=True, blank=True, help_text="*C", verbose_name="Record T max (*C)")
    precipitations      = models.PositiveSmallIntegerField(null=True, blank=True, help_text="mm", verbose_name="Precipitations (mm)")
    wet_days            = models.PositiveSmallIntegerField(null=True, blank=True, validators=[MaxValueValidator(31),MinValueValidator(0)], default=0)
    sunrise_average     = TrimmedCharField(null=True, blank=True, max_length=10)
    sunset_average      = TrimmedCharField(null=True, blank=True, max_length=10)
    detail              = JSONField(null=True, blank=True)

    class Meta:
        unique_together = (
            ("city", "month"),
        )


class CrawlDetail(BaseModel):

    MONTH_WEATHER_INFO = 0
    MONTH_ALMANAC_INFO = 1

    CRAWL_CHOICES = (
        (MONTH_WEATHER_INFO,     _("Month weather info")),
        (MONTH_ALMANAC_INFO,     _("Month almanac info")),
    )

    content_type    = models.ForeignKey(ContentType, on_delete=models.PROTECT, db_index=False, related_name="+")
    object_id       = models.CharField(max_length=10)
    data_type_name  = models.PositiveSmallIntegerField(choices=CRAWL_CHOICES, default=MONTH_WEATHER_INFO)
    source_url      = models.URLField(blank=True)
    content_object  = generic.GenericForeignKey('content_type', 'object_id')

    class Meta:
        unique_together = (
            ("object_id", "content_type", "data_type_name"),
        )

class VisaCountry(BaseModel):

    name            = TrimmedCharField(max_length=50)
    slug            = TrimmedCharField(max_length=50, unique=True, editable=False)
    code            = FixedCharField(max_length=5)
    stop_at         = models.CharField(max_length=10, default=0)
    is_running      = models.BooleanField(default=False)
    total_completed = models.IntegerField(default=0)

    def calculate_percentage(self):
        num_total = VisaCountry.objects.all().count() - 1
        num_completed = VisaInformation.objects.filter(from_country_id=self.pk).count()

        self.total_completed = num_completed
        self.save(update_fields=['total_completed'])

        if num_total:
            return num_completed / num_total
        else:
            return 0.0

    def get_remained_to_country(self):
        to_country_list = VisaInformation.objects.filter(from_country_id=self.pk).values_list('to_country_id', flat=True)

        if not self.stop_at:
            self.stop_at = 0.0
        if to_country_list:
            remained_country = VisaCountry.objects.filter(id__gte=self.stop_at).exclude(id=self.pk, id__in=to_country_list)
        else:
            remained_country = VisaCountry.objects.filter(id__gte=self.stop_at).exclude(id=self.pk)
        return remained_country

    def refresh(self):
        self.calculate_percentage()

    def is_completed(self):
        num_total = VisaCountry.objects.all().count() - 1
        return self.total_completed >= num_total

    def save(self, *args, **kwargs):
        update_fields = kwargs.get('update_fields')
        # is_new = not save.id
        ins = super(VisaCountry, self).save(*args, **kwargs)

        if not update_fields or 'total_completed' not in update_fields:
            self.refresh()

        return ins

    class Meta:
        unique_together = (
            ("name", "slug", "code")
        )

    def __unicode__(self):
        return self.name

class VisaInformation(BaseModel):

    from_country        = models.ForeignKey(VisaCountry, on_delete=models.PROTECT, db_index=False, related_name="+")
    to_country          = models.ForeignKey(VisaCountry, on_delete=models.PROTECT, db_index=False, related_name="visa_free")
    tourist_visa        = models.BooleanField(default=False)
    business_visa       = models.BooleanField(default=False)
    details_tourist     = HTMLField(null=True, blank=True)
    details_business    = HTMLField(null=True, blank=True)

    class Meta:
        unique_together = (
            ("from_country", "to_country")
        )

    def __unicode__(self):
        return 'From %s to %s' % (self.from_country.name,  self.to_country.name)