# language_archive/services.py

import os
import requests
from pathlib import Path
import uuid
from django.urls import reverse

def upload_to_supabase(file, bucket_name, file_prefix=""):
    """
    Supabaseストレージへのファイルアップロード（requests使用）
    
    Args:
        file: アップロードするファイルオブジェクト
        bucket_name: バケット名
        file_prefix: ファイル名のプレフィックス
    
    Returns:
        公開URL
    """
    supabase_url = os.environ.get("SUPABASE_URL")
    supabase_key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or os.environ.get("SUPABASE_ANON_KEY")
    
    if not supabase_url or not supabase_key:
        raise Exception("Supabase環境変数が設定されていません")
    
    # ユニークなファイル名を生成
    extension = Path(file.name).suffix
    storage_file_name = f"{file_prefix}{uuid.uuid4()}{extension}"
    
    # ファイルをアップロード
    file_bytes = file.read()
    
    # Supabase Storage APIエンドポイント
    upload_url = f"{supabase_url}/storage/v1/object/{bucket_name}/{storage_file_name}"
    
    headers = {
        "Authorization": f"Bearer {supabase_key}",
        "Content-Type": file.content_type,
    }
    
    try:
        response = requests.post(upload_url, data=file_bytes, headers=headers)
        response.raise_for_status()
        
        # 公開URLを生成
        public_url = f"{supabase_url}/storage/v1/object/public/{bucket_name}/{storage_file_name}"
        return public_url
    except Exception as e:
        print(f"アップロードエラー: {e}")
        print(f"レスポンス: {response.text if 'response' in locals() else 'No response'}")
        raise


def get_bucket_name(file_type):
    """
    ファイルタイプに応じたバケット名を返す
    
    Args:
        file_type: ファイルタイプ（audio, video, image, drone, photo, panorama）
    
    Returns:
        バケット名
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


def create_archive_map(language_records, geographic_records):
    """
    言語記録と地理環境データを含む地図HTMLを生成
    
    Args:
        language_records: LanguageRecordモデルのクエリセット
        geographic_records: GeographicRecordモデルのクエリセット
    
    Returns:
        地図のHTML文字列
    """
    import folium
    from folium.plugins import MarkerCluster
    
    center = [28.3214, 129.9259]
    m = folium.Map(
        location=center,
        zoom_start=12,
        tiles='https://cyberjapandata.gsi.go.jp/xyz/std/{z}/{x}/{y}.png',
        attr='<a href="https://maps.gsi.go.jp/" target="_blank">国土地理院</a>'
    )
    
    marker_cluster = MarkerCluster().add_to(m)
    
def create_archive_map(language_records, geographic_records):
    """
    言語記録と地理環境データを含む地図HTMLを生成
    """
    import folium
    from folium.plugins import MarkerCluster
    
    center = [28.3214, 129.9259]
    m = folium.Map(
        location=center,
        zoom_start=12,
        tiles='https://cyberjapandata.gsi.go.jp/xyz/std/{z}/{x}/{y}.png',
        attr='<a href="https://maps.gsi.go.jp/" target="_blank">国土地理院</a>'
    )
    
    marker_cluster = MarkerCluster().add_to(m)
    
    # --- 1. 言語記録をプロット ---
    for record in language_records:
        if record.village:
            detail_url = reverse('record_detail', args=[record.id])
            
            popup_html = f"""
            <div style="min-width: 200px;">
                <h5><i class="fas fa-microphone" style="color: green;"></i> {record.onomatopoeia_text}</h5>
                <p><strong>意味:</strong> {record.meaning}</p>
                <hr style="margin: 5px 0;">
                <p style="margin-bottom: 10px;"><i class="fas fa-map-marker-alt"></i> {record.village.name}</p>
                
                <a href="{detail_url}" class="btn btn-sm btn-light" target="_top">詳細を見る</a>
            </div>
            """
            marker = folium.Marker(
                location=[record.village.latitude, record.village.longitude],
                popup=folium.Popup(popup_html, max_width=300),
                icon=folium.Icon(color='green', icon='microphone', prefix='fa')
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
            <a href="{record.file_path}" target="_blank" class="btn btn-sm btn-info">表示する</a>
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