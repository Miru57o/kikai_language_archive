# language_archive/services.py

import os
import requests
from pathlib import Path
import uuid
from django.urls import reverse
import mimetypes 
import re  # サニタイズのために追加

def sanitize_filename(filename):
    """
    ファイル名から危険な文字（パス トラバーサルなど）や
    URL/ファイルシステムで問題を起こす可能性のある文字を除去し、
    半角英数字、ハイフン、アンダースコア、ドットに制限する。
    スペースはアンダースコアに置換する。
    """
    # スペースをアンダースコアに置換
    filename = filename.replace(" ", "_")
    
    # 許可する文字以外を削除
    # \w は [a-zA-Z0-9_] に相当
    filename = re.sub(r'[^\w.-]', '', filename)
    
    # 連続するドットやアンダースコアを一つにまとめる
    filename = re.sub(r'[_.-]{2,}', '_', filename)
    
    # 先頭のドットやハイフンを削除（.ssh のような隠しファイル化を防ぐ）
    filename = filename.lstrip('._-')
    
    # ファイル名が空になった場合のフォールバック
    if not filename:
        return f"file_{uuid.uuid4()}" # 万が一空になったらUUIDを付与
    return filename

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
    
    # 元のファイル名を Path オブジェクトの .name 属性から取得
    original_filename = Path(file.name).name
    
    # ファイル名をサニタイズ
    safe_filename = sanitize_filename(original_filename)
    
    # Prefixと安全なファイル名を結合
    storage_file_name = f"{file_prefix}{safe_filename}"
    
    # ファイルをアップロード
    file_bytes = file.read()

    # file.content_typeがNoneの場合に備えて、mimetypesで推測
    content_type, _ = mimetypes.guess_type(file.name)
    if not file.content_type and content_type:
        file.content_type = content_type

    if not file.content_type:
        file.content_type = 'application/octet-stream'  # デフォルトのMIMEタイプ
    
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
        file_type: ファイルタイプ（audio, video, image, drone_video, drone_photo, other）
    
    Returns:
        バケット名
    """
    bucket_map = {
        'audio': 'audio-files',
        'video': 'video-files',
        'image': 'image-files',
        'drone_video': 'drone-video-files',
        'drone_photo': 'drone-photo-files',
        'other': 'other-geo-files',
        }
    return bucket_map.get(file_type, 'image-files')


def create_archive_map(geographic_records, speakers):
    """
    話者データ、地理環境データを含む地図HTMLを生成
    
    Args:
        geographic_records: GeographicRecordモデルのクエリセット
        speakers: Speakerモデルのクエリセット
    
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
    
    # --- 地理環境データをプロット ---
    for record in geographic_records:
        content_type_map = {'drone_video': 'ドローン映像', 'drone_photo': 'ドローン画像', 'other':'その他地理データ'}
        content_type_display = content_type_map.get(record.content_type, '地理データ')

        popup_html = f"""
        <div style="min-width: 200px;">
            <h5><i class="fas fa-camera" style="color: blue;"></i> {record.title}</h5>
            <p><strong>種類:</strong> {content_type_display}</p>
            <p><strong>説明:</strong> {record.description}</p>
            <hr style="margin: 5px 0;">
            <a href="{record.file_path}" target="_blank" class="btn btn-sm btn-info geographic-detail-btn" 
               onclick="event.stopPropagation(); return true;" 
               ontouchend="event.stopPropagation(); return true;">表示する</a>
        </div>
        """
        marker = folium.Marker(
            location=[record.latitude, record.longitude],
            popup=folium.Popup(popup_html, max_width=300),
            icon=folium.Icon(color='blue', icon='camera', prefix='fa')
        )
        marker.add_to(marker_cluster)

    # --- 話者をプロット ---
    for speaker in speakers:
        if speaker.village:
            detail_url = reverse('speaker_records', args=[speaker.id])
            
            popup_html = f"""
            <div style="min-width: 200px;">
                <h5><i class="fas fa-user" style="color: red;"></i> {speaker.speaker_id}</h5>
                <p><strong>年代:</strong> {speaker.age_range}</p>
                <hr style="margin: 5px 0;">
                <p style="margin-bottom: 10px;"><i class="fas fa-map-marker-alt"></i> {speaker.village.name}</p>
                
                <a href="{detail_url}" class="btn btn-sm btn-light speaker-detail-btn" target="_top" 
                   onclick="event.stopPropagation(); return true;" 
                   ontouchend="event.stopPropagation(); return true;">この話者の記録を見る</a>
            </div>
            """
            marker = folium.Marker(
                location=[speaker.village.latitude, speaker.village.longitude],
                popup=folium.Popup(popup_html, max_width=300),
                icon=folium.Icon(color='red', icon='user', prefix='fa')
            )
            marker.add_to(marker_cluster)

    map_html = m._repr_html_()
    map_html = map_html.replace('<div class="folium-map"', '<div class="folium-map" id="map"')
    
    return map_html