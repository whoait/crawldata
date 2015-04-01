from django import forms
from django.contrib.contenttypes import generic
from models import Country, City, CityWeatherMonth, CrawlDetail
from django.contrib import admin, messages
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext_lazy as _


class CountryAdmin(admin.ModelAdmin):
    search_fields = ['name']
    list_display = ['name', 'code',]
    fieldsets = [
        ('General information', {
            'fields': ['code', 'name'],
            'classes': ('suit-tab suit-tab-general'),
        })
    ]

    suit_form_tabs = (
        ('general', 'General'),
    )

    class Meta:
        model = Country


class CityAdmin(admin.ModelAdmin):

    search_fields = ['name']
    list_display = ['name', 'country',]
    fieldsets = [
        ('General information', {
            'fields': ['name', 'country'],
            'classes': ('suit-tab suit-tab-general'),
        })
    ]

    suit_form_tabs = (
        ('general', 'General'),
    )

    class Meta:
        model = City


class CityWeatherMonthAdmin(admin.ModelAdmin):

    search_fields = ['city']
    list_display = ['city', 'month', 'sunlight', 'average_min', 'average_max',
                    'record_min', 'record_max', 'precipitations', 'wet_days',
                    'sunrise_average', 'sunset_average', 'detail']
    fieldsets = [
        ('General information', {
            'fields': ['city', 'month', 'sunlight', 'average_min', 'average_max',
                    'record_min', 'record_max', 'precipitations', 'wet_days'],
            'classes': ('suit-tab suit-tab-general'),
        }),
        ('Almanac', {
            'fields': ['sunrise_average', 'sunset_average', 'detail'],
            'classes': ('suit-tab suit-tab-detail',),
        }),
    ]

    suit_form_tabs = (
        ('general', 'General'),
        ('almanac', 'Almanac'),
    )

    class Meta:
        model = CityWeatherMonth


class CrawlDetailForm(forms.ModelForm):

    content_type    = forms.ModelChoiceField(queryset=ContentType.objects.all())
    object_id       = forms.CharField(max_length=20)

    def clean(self):
        cleaned_data    = super(CrawlDetailForm, self).clean()
        content_type    = cleaned_data.get('content_type')
        object_id       = cleaned_data.get('object_id')

        print content_type
        print object_id
        if content_type and object_id:
            if content_type.model == 'city':
                is_city = City.objects.filter(id=int(object_id)).count()
                if is_city == 0:
                    raise forms.ValidationError(_("City id does not exists."))

            if content_type.model == 'country':
                is_country = Country.objects.filter(code=str(object_id)).count()
                if is_country == 0:
                    raise forms.ValidationError(_("Country id does not exists."))

        return cleaned_data

    class Meta:
        model = CrawlDetail


class CrawlDetailAdmin(admin.ModelAdmin):

    search_fields   = ['content_type', 'data_type_name', 'source_url']
    list_display    = ['content_type', 'object_id', 'data_type_name', 'source_url']

    form = CrawlDetailForm

    fieldsets = [
        ('Detail', {
            'fields': ['content_type', 'object_id', 'data_type_name', 'source_url'],
            'classes': ('suit-tab suit-tab-general',),
        })
    ]

    suit_form_tabs = (
        ('general', 'General'),
    )

    class Meta:
        model = CrawlDetail


admin.site.register(Country, CountryAdmin)
admin.site.register(City, CityAdmin)
admin.site.register(CityWeatherMonth, CityWeatherMonthAdmin)
admin.site.register(CrawlDetail, CrawlDetailAdmin)