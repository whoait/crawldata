from django.db import models
from djbase.models import FixedCharField, TrimmedCharField, BaseModel
from django.utils.translation import ugettext_lazy as _
from django.forms import model_to_dict


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