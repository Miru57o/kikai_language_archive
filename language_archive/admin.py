# language_archive/admin.py

from django.contrib import admin
from .models import Village, Speaker, OnomatopoeiaType, LanguageRecord, GeographicRecord

admin.register(Village)
class VillageAdmin(admin.ModelAdmin):
    list_display = ['name', 'latitude', 'longitude']
    search_fields = ['name']
    list_per_page = 20


@admin.register(Speaker)
class SpeakerAdmin(admin.ModelAdmin):
    list_display = ['speaker_id', 'age_range', 'gender', 'village', 'consent_video']
    list_filter = ['gender', 'consent_video', 'village']
    search_fields = ['speaker_id', 'age_range']
    list_per_page = 20


@admin.register(OnomatopoeiaType)
class OnomatopoeiaTypeAdmin(admin.ModelAdmin):
    list_display = ['type_code', 'type_name']
    search_fields = ['type_code', 'type_name']
    list_per_page = 20


@admin.register(LanguageRecord)
class LanguageRecordAdmin(admin.ModelAdmin):
    list_display = ['onomatopoeia_text', 'file_type', 'speaker_village', 'speaker', 'language_frequency','recorded_date']
    list_filter = ['file_type', 'speaker__village', 'recorded_date', 'onomatopoeia_type','language_frequency']
    search_fields = ['onomatopoeia_text', 'meaning']
    date_hierarchy = 'recorded_date'
    list_per_page = 20
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('基本情報', {
            'fields': ('onomatopoeia_text', 'meaning', 'usage_example', 'phonetic_notation', 'language_frequency')
        }),
        ('ファイル情報', {
            'fields': ('file_type', 'file_path', 'thumbnail_path')
        }),
        ('関連情報', {
            'fields': ('speaker', 'onomatopoeia_type')
        }),
        ('メタデータ', {
            'fields': ('recorded_date', 'notes', 'created_at', 'updated_at')
        }),
    )

    def speaker_village(self, obj):
        return obj.speaker.village.name if obj.speaker and obj.speaker.village else '-'
    speaker_village.short_description = '集落'


@admin.register(GeographicRecord)
class GeographicRecordAdmin(admin.ModelAdmin):
    list_display = ['title', 'content_type', 'village', 'captured_date']
    list_filter = ['content_type', 'village', 'captured_date']
    search_fields = ['title', 'description']
    date_hierarchy = 'captured_date'
    list_per_page = 20
    readonly_fields = ['created_at']

# Register your models here.
