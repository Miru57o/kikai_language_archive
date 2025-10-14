# language_archive/services.py

import os
import requests
from pathlib import Path
import uuid
from django.urls import reverse
import folium
from folium.plugins import MarkerCluster

def upload_to_supabase(file, bucket_name, file_prefix=""):
    """
    Supabaseストレージへのファイルアップロード（requests使用）
    """
    supabase_url = os.environ.get("SUPABASE_URL")
    supabase_key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or os.environ.get("SUPABASE_ANON_KEY")
    
    if not supabase_url or not supabase_key:
        raise Exception("Supabase環境変数が設定されていません")
    
    extension = Path(file.name).suffix
    storage_file_name = f"{file_prefix}{uuid.uuid4()}{extension}"
    
    file_bytes = file.read()
    
    upload_url = f"{supabase_url}/storage/v1/object/{bucket_name}/{storage_file_name}"
    
    headers = {
        "Authorization": f"Bearer {supabase_key}",
        "Content-Type": file.content_type,
    }
    
    try:
        response = requests.post(upload_url, data=file_bytes, headers=headers)
        response.raise_for_status()
        
        public_url = f"{supabase_url}/storage/v1/object/public/{bucket_name}/{storage_file_name}"
        return public_url
    except Exception as e:
        print(f"アップロードエラー: {e}")
        print(f"レスポンス: {response.text if 'response' in locals() else 'No response'}")
        raise


def get_bucket_name(file_type):
    """
    ファイルタイプに応じたバケット名を返す
    """
    bucket_map = {
        'audio': 'audio-files',
        'video': 'video-files',
        'image': 'image-files',
        'drone': 'drone-footage',
        'photo': 'image-files',
        'panorama': 'image-files',
    }
    return bucket_map.get(file_type, 'image-files')


def create_archive_map(speakers, geographic_records):
    """
    話者と地理環境データを含む地図HTMLを生成
    """
    center = [28.3214, 129.9259]
    m = folium.Map(
        location=center,
        zoom_start=12,
        tiles='https://cyberjapandata.gsi.go.jp/xyz/std/{z}/{x}/{y}.png',
        attr='<a href="https://maps.gsi.go.jp/" target="_blank">国土地理院</a>'
    )
    
    marker_cluster = MarkerCluster().add_to(m)

    # --- 話者をプロット ---
    for speaker in speakers:
        if speaker.village:
            detail_url = reverse('speaker_records', args=[speaker.id])
            
            popup_html = f"""
            <div style="min-width: 200px;">
                <h5><i class="fas fa-user" style="color: green;"></i> {speaker.speaker_id}</h5>
                <p><strong>年代:</strong> {speaker.age_range}</p>
                <p><strong>性別:</strong> {speaker.get_gender_display()}</p>
                <hr style="margin: 5px 0;">
                <p style="margin-bottom: 10px;"><i class="fas fa-map-marker-alt"></i> {speaker.village.name}</p>
                <a href="{detail_url}" class="btn btn-sm btn-light" target="_top">この話者の記録を見る</a>
            </div>
            """
            marker = folium.Marker(
                location=[speaker.village.latitude, speaker.village.longitude],
                popup=folium.Popup(popup_html, max_width=300),
                icon=folium.Icon(color='green', icon='user', prefix='fa')
            )
            marker.add_to(marker_cluster)

    # --- 地理環境データをプロット ---
    for record in geographic_records:
        content_type_map = {'drone': 'ドローン映像', 'photo': '写真', 'panorama': 'パノラマ'}
        content_type_display = content_type_map.get(record.content_type, '地理データ')

        popup_html = f"""
        <div style="min-width: 200px;">
            <h5><i class="fas fa-camera" style="color: blue;"></i> {record.title}</h5>
            <p><strong>種類:</strong> {content_type_display}</p>
            <p><strong>説明:</strong> {record.description}</p>
            <hr style="margin: 5px 0;">
            <a href="{record.file_path}" target="_top" class="btn btn-sm btn-info">表示する</a>
        </div>
        """
        marker = folium.Marker(
            location=[record.latitude, record.longitude],
            popup=folium.Popup(popup_html, max_width=300),
            icon=folium.Icon(color='blue', icon='camera', prefix='fa')
        )
        marker.add_to(marker_cluster)

    map_html = m._repr_html_()
    map_html = map_html.replace('<div class="folium-map"', '<div class="folium-map" id="map"')
    
    return map_html