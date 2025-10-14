# language_archive/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse, StreamingHttpResponse
from django.contrib import messages
from django.db.models import Count, Q
from .models import LanguageRecord, GeographicRecord, Village, Speaker
from .forms import LanguageRecordForm, GeographicRecordForm
from .services import upload_to_supabase, get_bucket_name, create_archive_map
from .utils import reverse_geocode, format_record_for_api
import requests
import urllib.parse
import os

def index(request):
    """トップページ"""
    # 統計情報を取得
    total_records = LanguageRecord.objects.count()
    total_villages = LanguageRecord.objects.values('village').distinct().count()
    total_speakers = Speaker.objects.count()
    
    # 最近の言語記録
    recent_records = LanguageRecord.objects.select_related(
        'village', 'speaker', 'onomatopoeia_type'
    ).order_by('-created_at')[:6]
    
    context = {
        'total_records': total_records,
        'total_villages': total_villages,
        'total_speakers': total_speakers,
        'recent_records': recent_records,
    }
    return render(request, 'language_archive/index.html', context)

def map_view(request):
    """地図ビュー - 話者と地理データをクラスタ化して表示"""
    # 1件以上の言語記録があり、かつ集落情報を持つ話者を取得
    speakers = Speaker.objects.annotate(
        record_count=Count('languagerecord')
    ).filter(record_count__gt=0, village__isnull=False).select_related('village')
    
    # 位置情報を持つ地理環境データを取得
    geographic_records = GeographicRecord.objects.filter(latitude__isnull=False, longitude__isnull=False)
    
    # speakers と geographic_records を渡して地図を生成
    map_html = create_archive_map(
        speakers=speakers, 
        geographic_records=geographic_records
    )
    
    context = {
        'map_html': map_html,
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
        'speaker', 'village', 'onomatopoeia_type'
    ).all()
    
    # フィルタリング
    village_id = request.GET.get('village')
    file_type = request.GET.get('file_type')
    
    if village_id:
        records = records.filter(village_id=village_id)
    if file_type:
        records = records.filter(file_type=file_type)
    
    villages = Village.objects.all()
    
    context = {
        'records': records,
        'villages': villages,
    }
    return render(request, 'language_archive/record_list.html', context)


def record_detail(request, record_id):
    """言語記録の詳細"""
    record = get_object_or_404(
        LanguageRecord.objects.select_related('speaker', 'village', 'onomatopoeia_type'),
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
    
    villages = Village.objects.all()
    
    context = {
        'geo_records': geo_records,
        'villages': villages,
    }
    return render(request, 'language_archive/geographic_list.html', context)


def village_records(request, village_id):
    """特定集落の言語記録一覧"""
    village = get_object_or_404(Village, id=village_id)
    records = LanguageRecord.objects.filter(village=village).select_related(
        'speaker', 'onomatopoeia_type'
    )
    
    context = {
        'village': village,
        'records': records,
    }
    return render(request, 'language_archive/village_records.html', context)

def speaker_records(request, speaker_id):
    """特定話者の言語記録一覧"""
    speaker = get_object_or_404(Speaker.objects.select_related('village'), id=speaker_id)
    records = LanguageRecord.objects.filter(speaker=speaker).select_related(
        'village', 'onomatopoeia_type'
    )
    
    context = {
        'speaker': speaker,
        'records': records,
    }
    return render(request, 'language_archive/speaker_records.html', context)


def get_village_records_api(request, village_id):
    """集落の言語記録を取得するAPI"""
    records = LanguageRecord.objects.filter(village_id=village_id).select_related(
        'speaker', 'village', 'onomatopoeia_type'
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


def download_file(request):
    """ファイルダウンロード"""
    file_url = request.GET.get('url')
    filename = request.GET.get('filename')
    
    if not file_url:
        return HttpResponse('URLが指定されていません', status=400)
    
    file_url = urllib.parse.unquote(file_url)
    if not filename:
        parsed_url = urllib.parse.urlparse(file_url)
        filename = os.path.basename(parsed_url.path)
    
    try:
        r = requests.get(file_url, stream=True)
        r.raise_for_status()
        
        response = StreamingHttpResponse(
            r.iter_content(chunk_size=8192),
            content_type=r.headers.get('Content-Type', 'application/octet-stream')
        )
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        if 'Content-Length' in r.headers:
            response['Content-Length'] = r.headers['Content-Length']
        
        return response
    except Exception as e:
        return HttpResponse(f'ダウンロードエラー: {e}', status=500)