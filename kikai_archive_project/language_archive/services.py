# language_archive/services.py

import os
from supabase import create_client
from pathlib import Path
import uuid

def get_supabase_client():
    """Supabaseクライアントを取得"""
    supabase_url = os.environ.get("SUPABASE_URL")
    supabase_key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or os.environ.get("SUPABASE_ANON_KEY")
    
    if not supabase_url or not supabase_key:
        raise Exception("Supabase環境変数が設定されていません")
    
    return create_client(supabase_url, supabase_key)


def upload_to_supabase(file, bucket_name, file_prefix=""):
    """
    Supabaseストレージへのファイルアップロード
    
    Args:
        file: アップロードするファイルオブジェクト
        bucket_name: バケット名
        file_prefix: ファイル名のプレフィックス
    
    Returns:
        公開URL
    """
    supabase = get_supabase_client()
    
    # ユニークなファイル名を生成
    extension = Path(file.name).suffix
    storage_file_name = f"{file_prefix}{uuid.uuid4()}{extension}"
    
    # ファイルをアップロード
    file_bytes = file.read()
    file_options = {"upsert": "true"}
    
    try:
        supabase.storage.from_(bucket_name).upload(
            storage_file_name, file_bytes, file_options
        )
        
        # 公開URLを取得
        public_url = supabase.storage.from_(bucket_name).get_public_url(storage_file_name)
        return public_url
    except Exception as e:
        print(f"アップロードエラー: {e}")
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


def create_map_with_villages(villages):
    """
    集落情報を含む地図HTMLを生成（Foliumを使用）
    
    Args:
        villages: Villageモデルのクエリセット
    
    Returns:
        地図のHTML文字列
    """
    import folium
    from folium.plugins import MarkerCluster
    
    # 喜界島の中心座標
    center = [28.3214, 129.9259]
    
    # 地図オブジェクトを作成
    m = folium.Map(
        location=center,
        zoom_start=12,
        tiles='https://cyberjapandata.gsi.go.jp/xyz/std/{z}/{x}/{y}.png',
        attr='<a href="https://maps.gsi.go.jp/" target="_blank">国土地理院</a>'
    )
    
    # マーカークラスタリングを追加
    marker_cluster = MarkerCluster().add_to(m)
    
    # 各集落にマーカーを追加
    for village in villages:
        popup_html = f"""
        <div style="min-width: 200px;">
            <h4>{village.name}</h4>
            <p>{village.description if village.description else ''}</p>
            <a href="/village/{village.id}/records/" class="btn btn-sm btn-primary">
                言語記録を見る
            </a>
        </div>
        """
        
        marker = folium.Marker(
            location=[village.latitude, village.longitude],
            popup=folium.Popup(popup_html, max_width=300),
            icon=folium.Icon(color='blue', icon='home', prefix='fa')
        )
        marker.add_to(marker_cluster)
    
    # 地図のHTML文字列を取得
    map_html = m._repr_html_()
    
    # 地図のdiv要素にIDを追加
    map_html = map_html.replace('<div class="folium-map"', '<div class="folium-map" id="map"')
    
    return map_html