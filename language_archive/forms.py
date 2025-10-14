# language_archive/forms.py

from django import forms
from .models import LanguageRecord, GeographicRecord, Speaker, Village

class LanguageRecordForm(forms.ModelForm):
    """言語記録アップロードフォーム"""
    file = forms.FileField(label="ファイル", required=True)
    
    class Meta:
        model = LanguageRecord
        fields = [
            'title', 'onomatopoeia_text', 'meaning', 'usage_example',
            'phonetic_notation', 'language_frequency','file_type', 'speaker', 'village',
            'onomatopoeia_type', 'recorded_date', 'notes', 'latitude', 'longitude'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'タイトルを入力'
            }),
            'onomatopoeia_text': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'オノマトペを入力'
            }),
            'meaning': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': '意味を入力'
            }),
            'usage_example': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': '用例を入力'
            }),
            'phonetic_notation': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': '音声記号を入力（オプション）'
            }),
            'language_frequency': forms.Select(attrs={'class': 'form-control'}),
            'file_type': forms.Select(attrs={'class': 'form-control'}),
            'speaker': forms.Select(attrs={'class': 'form-control'}),
            'village': forms.Select(attrs={'class': 'form-control'}),
            'onomatopoeia_type': forms.Select(attrs={'class': 'form-control'}),
            'recorded_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': '備考（オプション）'
            }),
            'latitude': forms.HiddenInput(),
            'longitude': forms.HiddenInput(),
        }


class GeographicRecordForm(forms.ModelForm):
    """地理環境データアップロードフォーム"""
    file = forms.FileField(label="ファイル", required=True)
    
    class Meta:
        model = GeographicRecord
        fields = [
            'title', 'content_type', 'description', 'village',
            'latitude', 'longitude', 'captured_date'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'タイトルを入力'
            }),
            'content_type': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': '説明を入力'
            }),
            'village': forms.Select(attrs={'class': 'form-control'}),
            'captured_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'latitude': forms.HiddenInput(),
            'longitude': forms.HiddenInput(),
        }


class SpeakerForm(forms.ModelForm):
    """話者登録フォーム"""
    
    class Meta:
        model = Speaker
        fields = [
            'speaker_id', 'age_range', 'gender', 'village',
            'consent_video', 'notes'
        ]
        widgets = {
            'speaker_id': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '話者IDを入力（例: SPK001）'
            }),
            'age_range': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '年代を入力（例: 70代）'
            }),
            'gender': forms.Select(attrs={'class': 'form-control'}),
            'village': forms.Select(attrs={'class': 'form-control'}),
            'consent_video': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': '備考（オプション）'
            }),
        }