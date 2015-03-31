from models import Country, City, CityWeatherMonth
from django.contrib import admin, messages


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
    list_display = ['name', 'country__name',]
    fieldsets = [
        ('General information', {
            'fields': ['name', 'country__name'],
            'classes': ('suit-tab suit-tab-general'),
        })
    ]

    suit_form_tabs = (
        ('general', 'General'),
    )

    class Meta:
        model = City

admin.site.register(Country, CountryAdmin)
admin.site.register(City, CityAdmin)