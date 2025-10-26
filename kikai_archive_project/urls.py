"""
URL configuration for kikai_archive_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# kikai_archive_project/urls.py

from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from language_archive import views

urlpatterns = [
    # 管理画面
    path('admin/', admin.site.urls),
    
    # トップページ
    path('', views.index, name='index'),
    
    # 地図
    path('map/', views.map_view, name='map_view'),
    
    # 言語記録
    path('records/', views.record_list, name='record_list'),
    path('records/<int:record_id>/', views.record_detail, name='record_detail'),
    path('records/upload/', views.upload_language_record, name='upload_language_record'),
    path('records/search/', views.search_records, name='search_records'),
    
    # 地理環境データ
    path('geographic/', views.geographic_list, name='geographic_list'),
    path('geographic/upload/', views.upload_geographic_record, name='upload_geographic_record'),
    
    # 集落関連
    path('village/<int:village_id>/records/', views.village_records, name='village_records'),
    
    # 話者関連
    path('speaker/<int:speaker_id>/records/', views.speaker_records, name='speaker_records'),
    
    # API
    path('api/village/<int:village_id>/records/', views.get_village_records_api, name='api_village_records'),
]
# 開発環境でのメディアファイル配信
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)