# 喜界島オノマトペ・言語アーカイブ

## 概要

このプロジェクトは、鹿児島県喜界島で話されている消滅危機言語「喜界語」を記録・保存するためのデジタルアーカイブシステムです。特にオノマトペ（擬音語・擬態語）を中心に、話者の音声・映像、地理情報、話者属性を紐づけて記録し、未来へ継承することを目的としています。


## 主な機能

  * **言語記録の閲覧**: オノマトペ、意味、用例、音声・映像データなどを一覧・詳細表示で確認できます。
  * **地図からの検索**: 地図上の集落マーカーから、各地域に紐づく言語記録を直感的に探せます。
  * **データアップロード**: 新しい言語記録（音声、映像、画像）や、ドローン映像などの地理環境データを登録できます。
  * **詳細なフィルタリングと検索**: 集落、ファイルの種類、キーワードなどで柔軟にデータを絞り込めます。
  * **ファイルダウンロード**: 登録されているメディアファイルをダウンロードできます。

## 技術スタック

本プロジェクトは以下の技術を使用して構築されています。

  * **バックエンド**: Django
  * **フロントエンド**: HTML, CSS, JavaScript, Bootstrap
  * **地図**: Folium, Leaflet.js
  * **データベース**: PostgreSQL (Supabase)
  * **ファイルストレージ**: Supabase Storage
  * **その他**: gunicorn, whitenoise など

## セットアップ手順

### 1\. リポジトリのクローン

```bash
git clone https://github.com/miru57o/kikai_language_archive.git
cd kikai_language_archive
```

### 2\. 仮想環境の作成と有効化

```bash
python -m venv venv
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate  # Windows
```

### 3\. 依存関係のインストール

```bash
pip install -r requirements.txt
```

### 4\. 環境変数の設定

プロジェクトのルートディレクトリに `.env` ファイルを作成し、以下の内容を記述します。

```.env
SECRET_KEY='your-secret-key'
DEBUG=True
ALLOWED_HOSTS='127.0.0.1,localhost'

# Supabaseを使用する場合
DATABASE_URL='your-supabase-database-url'
SUPABASE_URL='your-supabase-project-url'
SUPABASE_SERVICE_ROLE_KEY='your-supabase-service-role-key'
```

**Note:** `SECRET_KEY` には任意の強力な文字列を設定してください。

### 5\. データベースのマイグレーション

```bash
python kikai_archive_project/manage.py migrate
```

### 6\. 開発サーバーの起動

```bash
python kikai_archive_project/manage.py runserver
```

ブラウザで `http://127.0.0.1:8000/` にアクセスすると、アプリケーションが表示されます。

## データモデル

本システムの主要なデータモデルは以下の通りです。

  * `LanguageRecord`: オノマトペ、意味、音声・映像ファイルなどの言語記録を格納。
  * `GeographicRecord`: ドローン映像や写真などの地理環境データを格納。
  * `Village`: 喜界島の集落情報を格納（緯度経度情報を含む）。
  * `Speaker`: 話し手の年代、性別などの匿名化された情報を格納。
  * `OnomatopoeiaType`: オノマトペの分類を管理。
  * `ExternalLink`: 関連する外部リンクを管理。
