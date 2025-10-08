# language_archive/models.py

from django.db import models
from django.utils import timezone

class Village(models.Model):
    """集落情報テーブル"""
    name = models.CharField(max_length=100, verbose_name="集落名")
    latitude = models.FloatField(verbose_name="緯度")
    longitude = models.FloatField(verbose_name="経度")
    description = models.TextField(blank=True, verbose_name="説明")
    
    class Meta:
        verbose_name = "集落"
        verbose_name_plural = "集落"
    
    def __str__(self):
        return self.name


class Speaker(models.Model):
    """話者情報テーブル（匿名化）"""
    GENDER_CHOICES = [
        ('M', '男性'),
        ('F', '女性'),
        ('O', 'その他'),
    ]
    
    FREQUENCY_CHOICES = [
        ('daily', '日常的に使用'),
        ('often', 'よく使用'),
        ('sometimes', 'たまに使用'),
        ('rarely', 'ほとんど使用しない'),
    ]
    
    speaker_id = models.CharField(max_length=50, unique=True, verbose_name="話者ID")
    age_range = models.CharField(max_length=20, verbose_name="年代")
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, verbose_name="性別")
    village = models.ForeignKey(Village, on_delete=models.SET_NULL, null=True, verbose_name="集落")
    language_frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES, verbose_name="言語使用頻度")
    consent_video = models.BooleanField(default=False, verbose_name="映像公開同意")
    notes = models.TextField(blank=True, verbose_name="備考")
    
    class Meta:
        verbose_name = "話者"
        verbose_name_plural = "話者"
    
    def __str__(self):
        return f"{self.speaker_id} ({self.age_range}, {self.get_gender_display()})"


class OnomatopoeiaType(models.Model):
    """オノマトペ型マスタ"""
    type_code = models.CharField(max_length=10, unique=True, verbose_name="型コード")
    type_name = models.CharField(max_length=100, verbose_name="型名")
    description = models.TextField(verbose_name="説明")
    
    class Meta:
        verbose_name = "オノマトペ型"
        verbose_name_plural = "オノマトペ型"
    
    def __str__(self):
        return f"{self.type_code}: {self.type_name}"


class LanguageRecord(models.Model):
    """言語記録データテーブル"""
    FILE_TYPE_CHOICES = [
        ('audio', '音声'),
        ('video', '映像'),
        ('image', '画像'),
    ]
    
    # 基本情報
    title = models.CharField(max_length=200, verbose_name="タイトル")
    onomatopoeia_text = models.CharField(max_length=100, verbose_name="オノマトペ")
    meaning = models.TextField(verbose_name="意味")
    usage_example = models.TextField(verbose_name="用例")
    phonetic_notation = models.TextField(blank=True, verbose_name="音声記号")
    
    # ファイル情報
    file_type = models.CharField(max_length=10, choices=FILE_TYPE_CHOICES, verbose_name="ファイル種類")
    file_path = models.URLField(max_length=1024, verbose_name="ファイルURL")
    thumbnail_path = models.URLField(max_length=1024, blank=True, verbose_name="サムネイルURL")
    
    # 関連情報
    speaker = models.ForeignKey(Speaker, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="話者")
    village = models.ForeignKey(Village, on_delete=models.SET_NULL, null=True, verbose_name="集落")
    onomatopoeia_type = models.ForeignKey(OnomatopoeiaType, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="型")
    
    # メタデータ
    recorded_date = models.DateField(verbose_name="収録日")
    created_at = models.DateTimeField(default=timezone.now, verbose_name="登録日時")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新日時")
    notes = models.TextField(blank=True, verbose_name="備考")
    
    class Meta:
        verbose_name = "言語記録"
        verbose_name_plural = "言語記録"
        ordering = ['-recorded_date']
    
    def __str__(self):
        return f"{self.onomatopoeia_text} - {self.title}"


class GeographicRecord(models.Model):
    """地理・環境データテーブル"""
    CONTENT_TYPE_CHOICES = [
        ('drone', 'ドローン映像'),
        ('photo', '写真'),
        ('panorama', 'パノラマ'),
    ]
    
    title = models.CharField(max_length=200, verbose_name="タイトル")
    content_type = models.CharField(max_length=20, choices=CONTENT_TYPE_CHOICES, verbose_name="コンテンツ種類")
    file_path = models.URLField(max_length=1024, verbose_name="ファイルURL")
    thumbnail_path = models.URLField(max_length=1024, blank=True, verbose_name="サムネイルURL")
    
    description = models.TextField(verbose_name="説明")
    village = models.ForeignKey(Village, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="集落")
    latitude = models.FloatField(null=True, blank=True, verbose_name="緯度")
    longitude = models.FloatField(null=True, blank=True, verbose_name="経度")
    
    captured_date = models.DateField(verbose_name="撮影日")
    created_at = models.DateTimeField(default=timezone.now, verbose_name="登録日時")
    
    class Meta:
        verbose_name = "地理環境データ"
        verbose_name_plural = "地理環境データ"
        ordering = ['-captured_date']
    
    def __str__(self):
        return self.title


class ExternalLink(models.Model):
    """外部コンテンツリンクテーブル"""
    title = models.CharField(max_length=200, verbose_name="タイトル")
    url = models.URLField(verbose_name="URL")
    description = models.TextField(verbose_name="説明")
    thumbnail_url = models.URLField(blank=True, verbose_name="サムネイルURL")
    creator = models.CharField(max_length=100, verbose_name="制作者")
    created_at = models.DateTimeField(default=timezone.now, verbose_name="登録日時")
    
    class Meta:
        verbose_name = "外部リンク"
        verbose_name_plural = "外部リンク"
    
    def __str__(self):
        return self.title

# Create your models here.
