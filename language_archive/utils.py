# language_archive/utils.py

import requests

def geocode_address(address):
    """
    住所を緯度・経度に変換する（ジオコーディング）
    国土地理院APIを使用
    
    Args:
        address: 住所文字列
    
    Returns:
        (緯度, 経度) のタプル。失敗時は (None, None)
    """
    try:
        url = f"https://msearch.gsi.go.jp/address-search/AddressSearch?q={address}"
        response = requests.get(url, timeout=10)
        data = response.json()
        
        if data and len(data) > 0:
            # 最初の結果を使用
            coordinates = data[0]['geometry']['coordinates']
            # 地理院APIは[経度, 緯度]の順で返すので、順序を入れ替える
            return coordinates[1], coordinates[0]  # 緯度, 経度
        else:
            return None, None
    except Exception as e:
        print(f"ジオコーディングエラー: {e}")
        return None, None


def reverse_geocode(lat, lon):
    """
    緯度・経度を住所に変換する（逆ジオコーディング）
    国土地理院APIを使用
    
    Args:
        lat: 緯度
        lon: 経度
    
    Returns:
        住所文字列。失敗時は座標を文字列で返す
    """
    try:
        url = f"https://mreversegeocoder.gsi.go.jp/reverse-geocoder/LonLatToAddress"
        params = {'lat': lat, 'lon': lon}
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        if data and 'results' in data:
            result = data['results']
            
            # 住所情報を組み立て
            if 'muniCd' in result and 'lv01Nm' in result:
                address = result.get('lv01Nm', '')
                return address
            else:
                return f"緯度: {lat}, 経度: {lon}"
        else:
            return f"緯度: {lat}, 経度: {lon}"
    except Exception as e:
        print(f"逆ジオコーディングエラー: {e}")
        return f"緯度: {lat}, 経度: {lon}"


def format_speaker_info(speaker):
    """
    話者情報を整形して表示用の辞書を返す
    
    Args:
        speaker: Speakerモデルのインスタンス
    
    Returns:
        整形された話者情報の辞書
    """
    if not speaker:
        return None
    
    return {
        'speaker_id': speaker.speaker_id,
        'age_range': speaker.age_range,
        'gender': speaker.get_gender_display(),
        'village': speaker.village.name if speaker.village else '不明',
        'language_frequency': speaker.get_language_frequency_display(),
    }


def format_record_for_api(record):
    """
    言語記録データをAPI用に整形
    
    Args:
        record: LanguageRecordモデルのインスタンス
    
    Returns:
        API用に整形されたデータ辞書
    """
    return {
        'id': record.id,
        'title': record.title,
        'onomatopoeia': record.onomatopoeia_text,
        'meaning': record.meaning,
        'usage_example': record.usage_example,
        'phonetic_notation': record.phonetic_notation,
        'file_type': record.file_type,
        'file_path': record.file_path,
        'thumbnail_path': record.thumbnail_path,
        'speaker': format_speaker_info(record.speaker),
        'village': {
            'id': record.village.id if record.village else None,
            'name': record.village.name if record.village else '不明',
        },
        'type': {
            'code': record.onomatopoeia_type.type_code if record.onomatopoeia_type else None,
            'name': record.onomatopoeia_type.type_name if record.onomatopoeia_type else None,
            'description': record.onomatopoeia_type.description if record.onomatopoeia_type else None,
        },
        'recorded_date': record.recorded_date.strftime('%Y年%m月%d日'),
        'notes': record.notes,
    }