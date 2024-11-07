from django.contrib import admin

from .models import SiteSettings, FrequencyAskQuestion, HeaderSite, FooterLogo, FooterSocial, SliderImage


# Register your models here.

@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ['location']


@admin.register(HeaderSite)
class HeaderSiteAdmin(admin.ModelAdmin):
    list_display = ['header_title', "link", "created_at", "updated_at"]
    search_fields = ['header_title']
    list_filter = ['created_at', 'updated_at']


@admin.register(FrequencyAskQuestion)
class FrequencyAskQuestionAdmin(admin.ModelAdmin):
    list_display = ['question', "created_at", "updated_at"]
    search_fields = ['question']
    list_filter = ['created_at', 'updated_at']


@admin.register(FooterLogo)
class FooterLogoAdmin(admin.ModelAdmin):
    pass


@admin.register(FooterSocial)
class FooterSocialAdmin(admin.ModelAdmin):
    pass


@admin.register(SliderImage)
class SliderImageAdmin(admin.ModelAdmin):
    pass
