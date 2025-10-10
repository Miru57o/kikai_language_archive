# language_archive/admin.py

from django.contrib import admin
from .models import Village, Speaker, OnomatopoeiaType, LanguageRecord, GeographicRecord, ExternalLink

@admin.register(Village)
class VillageAdmin(admin.ModelAdmin):
    list_display = ['name', 'latitude', 'longitude']
    search_fields = ['name']
    list_per_page = 20


@admin.register(Speaker)
class SpeakerAdmin(admin.ModelAdmin):
    list_display = ['speaker_id', 'age_range', 'gender', 'village', 'language_frequency', 'consent_video']
    list_filter = ['gender', 'language_frequency', 'consent_video', 'village']
    search_fields = ['speaker_id', 'age_range']
    list_per_page = 20


@admin.register(OnomatopoeiaType)
class OnomatopoeiaTypeAdmin(admin.ModelAdmin):
    list_display = ['type_code', 'type_name']
    search_fields = ['type_code', 'type_name']
    list_per_page = 20


@admin.register(LanguageRecord)
class LanguageRecordAdmin(admin.ModelAdmin):
    list_display = ['title', 'onomatopoeia_text', 'file_type', 'village', 'speaker', 'recorded_date']
    list_filter = ['file_type', 'village', 'recorded_date', 'onomatopoeia_type']
    search_fields = ['title', 'onomatopoeia_text', 'meaning']
    date_hierarchy = 'recorded_date'
    list_per_page = 20
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('基本情報', {
            'fields': ('title', 'onomatopoeia_text', 'meaning', 'usage_example', 'phonetic_notation')
        }),
        ('ファイル情報', {
            'fields': ('file_type', 'file_path', 'thumbnail_path')
        }),
        ('関連情報', {
            'fields': ('speaker', 'village', 'onomatopoeia_type')
        }),
        ('メタデータ', {
            'fields': ('recorded_date', 'notes', 'created_at', 'updated_at')
        }),
    )


@admin.register(GeographicRecord)
class GeographicRecordAdmin(admin.ModelAdmin):
    list_display = ['title', 'content_type', 'village', 'captured_date']
    list_filter = ['content_type', 'village', 'captured_date']
    search_fields = ['title', 'description']
    date_hierarchy = 'captured_date'
    list_per_page = 20
    readonly_fields = ['created_at']


@admin.register(ExternalLink)
class ExternalLinkAdmin(admin.ModelAdmin):
    list_display = ['title', 'creator', 'url', 'created_at']
    search_fields = ['title', 'creator', 'description']
    list_per_page = 20
    readonly_fields = ['created_at']

# Register your models here.
