# language_archive/forms.py

from django import forms
from .models import LanguageRecord, GeographicRecord, Speaker, Village

class LanguageRecordForm(forms.ModelForm):
    """言語記録アップロードフォーム"""
    file = forms.FileField(label="ファイル", required=True)

# --- カスタム初期化メソッドで必須Selectフィールドの設定 ---
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # file_type (必須)
        file_type_choices = [("", "ファイル種類を選択")] + list(LanguageRecord.FILE_TYPE_CHOICES)
        self.fields['file_type'].choices = file_type_choices
        self.fields['file_type'].widget.attrs['required'] = True

        #language_frequency (必須)
        freq_choices = [("", "言語使用頻度を選択")] + list(LanguageRecord.FREQUENCY_CHOICES)
        self.fields['language_frequency'].choices = freq_choices
        self.fields['language_frequency'].widget.attrs['required'] = True

        # speaker (モデルでは任意だが、フォームでは必須)
        self.fields['speaker'].required = True
        self.fields['speaker'].empty_label = "話者を選択"
        self.fields['speaker'].widget.attrs['required'] = True

        # onomatopoeia_type (モデルでは任意だが、フォームでは必須)
        self.fields['onomatopoeia_type'].required = True
        self.fields['onomatopoeia_type'].empty_label = "オノマトペ型を選択"
        self.fields['onomatopoeia_type'].widget.attrs['required'] = True

#サーバーサイドでのバリテーション
    def clean_file(self):
        data = self.cleaned_data.get('file_type')
        if not data:
            raise forms.ValidationError("ファイルを選択してください。")
        return data

    def clean_language_frequency(self):
        data = self.cleaned_data.get('language_frequency')
        if not data:
            raise forms.ValidationError("言語使用頻度を選択してください。")
        return data

    class Meta:
        model = LanguageRecord
        fields = [
            'onomatopoeia_text', 'meaning', 'usage_example',
            'phonetic_notation', 'language_frequency','file_type', 'speaker',
            'onomatopoeia_type', 'recorded_date', 'notes'
        ]
        widgets = {
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
        }


class GeographicRecordForm(forms.ModelForm):
    """地理環境データアップロードフォーム"""
    file = forms.FileField(label="ファイル", required=True)

    # --- カスタム初期化メソッドで必須Selectフィールドの設定 ---
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # content_type (必須)
        content_type_choices = [("", "コンテンツ種類を選択")] + list(GeographicRecord.CONTENT_TYPE_CHOICES)
        self.fields['content_type'].choices = content_type_choices
        self.fields['content_type'].widget.attrs['required'] = True

        # village (モデルでは任意だが、フォームでは必須)
        self.fields['village'].required = True 
        self.fields['village'].empty_label = "集落を選択"
        self.fields['village'].widget.attrs['required'] = True

    #サーバーサイドでのバリテーション
    def clean_content_type(self):
        data = self.cleaned_data.get('content_type')
        if not data:
            raise forms.ValidationError("コンテンツ種類を選択してください。")
        return data
    
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