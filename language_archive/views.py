# language_archive/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse, StreamingHttpResponse
from django.contrib import messages
from django.db.models.functions import TruncYear
from django.db.models import Count, Q
from .models import LanguageRecord, GeographicRecord, Village, OnomatopoeiaType, Speaker
from .forms import LanguageRecordForm, GeographicRecordForm
from .services import upload_to_supabase, get_bucket_name, create_archive_map
from .utils import reverse_geocode, format_record_for_api
import requests
import urllib.parse
import os
import datetime

def index(request):
    """トップページ"""
    # 統計情報を取得
    total_records = LanguageRecord.objects.count()
    total_villages = LanguageRecord.objects.filter(speaker__village__isnull=False).values('speaker__village').distinct().count()
    total_speakers = Speaker.objects.count()
    
    # 最近の言語記録
    recent_records = LanguageRecord.objects.select_related(
        'speaker', 'onomatopoeia_type'
    ).order_by('-created_at')[:6]
    
    context = {
        'total_records': total_records,
        'total_villages': total_villages,
        'total_speakers': total_speakers,
        'recent_records': recent_records,
    }
    return render(request, 'language_archive/index.html', context)


def map_view(request):
    """地図ビュー"""
    geographic_records = GeographicRecord.objects.filter(latitude__isnull=False, longitude__isnull=False)
    speakers = Speaker.objects.select_related('village').filter(village__isnull=False)

    # データベースから存在する年をすべて取得
    lang_years = LanguageRecord.objects.annotate(year=TruncYear('recorded_date')).values_list('year', flat=True).distinct()
    geo_years = GeographicRecord.objects.annotate(year=TruncYear('captured_date')).values_list('year', flat=True).distinct()
    
    # setを使って重複をなくし、降順にソート
    all_years = sorted(list(set([y.year for y in lang_years if y] + [y.year for y in geo_years if y])), reverse=True)

    # フィルター処理
    selected_year = request.GET.get('year')
    if selected_year:
        geographic_records = geographic_records.filter(captured_date__year=selected_year)
        speakers_with_records_in_year = LanguageRecord.objects.filter(recorded_date__year=selected_year).values_list('speaker_id', flat=True)
        speakers = speakers.filter(id__in=speakers_with_records_in_year)

    map_html = create_archive_map(
        geographic_records=geographic_records,
        speakers=speakers
    )

    context = {
        'map_html': map_html,
        'all_years': all_years,
        'selected_year': int(selected_year) if selected_year else None,
    }
    return render(request, 'language_archive/map.html', context)

def upload_language_record(request):
    """言語記録のアップロード"""
    if request.method == 'POST':
        form = LanguageRecordForm(request.POST, request.FILES)
        
        if form.is_valid():
            file = request.FILES.get('file')
            
            if file:
                try:
                    record = form.save(commit=False)
                    
                    # Supabaseにアップロード
                    file_type = form.cleaned_data['file_type']
                    bucket_name = get_bucket_name(file_type)
                    public_url = upload_to_supabase(file, bucket_name, f"language/{file_type}/")
                    
                    record.file_path = public_url
                    record.save()
                    form.save_m2m() # ManyToManyフィールドがあれば保存
                    
                    messages.success(request, '言語記録をアップロードしました。')
                    return redirect('record_list')
                except Exception as e:
                    messages.error(request, f'アップロードエラー: {str(e)}')
            else:
                messages.error(request, 'ファイルを選択してください。')
    else:
        form = LanguageRecordForm()
    
    # テンプレートに集落情報を渡す
    villages = Village.objects.all().values('id', 'name', 'latitude', 'longitude')
    context = {'form' : form, 'villages_data': list(villages)}
    return render(request, 'language_archive/upload_language.html', context)


def upload_geographic_record(request):
    """地理環境データのアップロード"""
    if request.method == 'POST':
        form = GeographicRecordForm(request.POST, request.FILES)
        
        if form.is_valid():
            file = request.FILES.get('file')
            
            if file:
                try:
                    record = form.save(commit=False)
                    
                    # 位置情報処理を追加
                    lat = form.cleaned_data.get('latitude')
                    lon = form.cleaned_data.get('longitude')
                    village = form.cleaned_data.get('village')

                    if lat and lon:
                        record.latitude = lat
                        record.longitude = lon
                    elif village:
                        record.latitude = village.latitude
                        record.longitude = village.longitude

                    # Supabaseにアップロード
                    content_type = form.cleaned_data['content_type']
                    bucket_name = get_bucket_name(content_type)
                    public_url = upload_to_supabase(file, bucket_name, f"geographic/{content_type}/")
                    
                    record.file_path = public_url
                    record.save()
                    
                    messages.success(request, '地理環境データをアップロードしました。')
                    return redirect('geographic_list')
                except Exception as e:
                    messages.error(request, f'アップロードエラー: {str(e)}')
            else:
                messages.error(request, 'ファイルを選択してください。')
    else:
        form = GeographicRecordForm()
        
    # テンプレートに集落情報を渡す
    villages = Village.objects.all().values('id', 'name', 'latitude', 'longitude')
    context = {'form': form, 'villages_data': list(villages)}
    return render(request, 'language_archive/upload_geographic.html', context)


def record_list(request):
    """言語記録一覧"""
    records = LanguageRecord.objects.select_related(
        'speaker', 'onomatopoeia_type', 'village'
    ).all()
    
    # フィルタリング
    village_id = request.GET.get('village')
    file_type = request.GET.get('file_type')
    onomatopoeia_type_code = request.GET.get('onomatopoeia_type')
    
    if village_id:
        records = records.filter(speaker__village_id=village_id)
    if file_type:
        records = records.filter(file_type=file_type)
    if onomatopoeia_type_code:
        records = records.filter(onomatopoeia_type__type_code=onomatopoeia_type_code)
    
    village_ids_with_records = LanguageRecord.objects.filter(speaker__village__isnull=False).values_list('speaker__village_id', flat=True).distinct()
    villages = Village.objects.filter(id__in=village_ids_with_records).order_by('-name')

    onomatopoeia_types = OnomatopoeiaType.objects.all()
    
    context = {
        'records': records,
        'villages': villages,
        'onomatopoeia_types': onomatopoeia_types,
    }
    return render(request, 'language_archive/record_list.html', context)


def record_detail(request, record_id):
    """言語記録の詳細"""
    record = get_object_or_404(
        LanguageRecord.objects.select_related('speaker', 'onomatopoeia_type'),
        id=record_id
    )
    
    context = {'record': record}
    return render(request, 'language_archive/record_detail.html', context)


def geographic_list(request):
    """地理環境データ一覧"""
    geo_records = GeographicRecord.objects.select_related('village').all()
    
    # フィルタリング
    content_type = request.GET.get('content_type')
    village_id = request.GET.get('village')
    
    if content_type:
        geo_records = geo_records.filter(content_type=content_type)
    if village_id:
        geo_records = geo_records.filter(village_id=village_id)
    
    village_ids_with_records = LanguageRecord.objects.filter(village__isnull=False).values_list('village_id', flat=True).distinct()
    villages = Village.objects.filter(id__in=village_ids_with_records).order_by('-name')

    
    context = {
        'geo_records': geo_records,
        'villages': villages,
    }
    return render(request, 'language_archive/geographic_list.html', context)


def village_records(request, village_id):
    """特定集落の言語記録一覧"""
    village = get_object_or_404(Village, id=village_id)
    records = LanguageRecord.objects.filter(speaker__village=village).select_related(
        'speaker', 'onomatopoeia_type'
    )
    
    context = {
        'village': village,
        'records': records,
    }
    return render(request, 'language_archive/village_records.html', context)

def speaker_records(request, speaker_id):
    """特定話者の言語記録一覧"""
    speaker = get_object_or_404(Speaker, id=speaker_id)
    records = LanguageRecord.objects.filter(speaker=speaker).select_related(
        'onomatopoeia_type'
    )
    
    context = {
        'speaker': speaker,
        'records': records,
    }
    return render(request, 'language_archive/speaker_records.html', context)


def get_village_records_api(request, village_id):
    """集落の言語記録を取得するAPI"""
    records = LanguageRecord.objects.filter(speaker__village_id=village_id).select_related(
        'speaker', 'onomatopoeia_type'
    )
    
    data = [format_record_for_api(record) for record in records]
    return JsonResponse(data, safe=False)


def search_records(request):
    """言語記録の検索"""
    query = request.GET.get('q', '')
    records = LanguageRecord.objects.select_related(
        'speaker', 'village', 'onomatopoeia_type'
    )
    
    if query:
        records = records.filter(
            Q(onomatopoeia_text__icontains=query) |
            Q(meaning__icontains=query) |
            Q(title__icontains=query)
        )
    
    context = {
        'records': records,
        'query': query,
    }
    return render(request, 'language_archive/search_results.html', context)

