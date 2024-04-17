# 概要
- 数理最適化のハンズオン
- 数理最適化の簡単なアプリをStreamlit Cloudでデプロイする
- inputするdata定義は固定、サンプルcsvを参照

# 問題設定
- ECを営む企業において、DMを送付する際に以下の3種を送付する
  - クーポンなし
  - クーポンあり-1000円引き
  - クーポンあり-2000円引き
- その際に、ユーザーの属性ごとにDMの種類を最適化し、効果量を最適化する

# URI
https://dm-promotion-opt-api-na6rrnkbw7jejfhqugoyjf.streamlit.app/

## 使い方
1. サンプルdata/csvと同様のカラム構成で、ブラウザ上へアップロード
2. 最適化を実行を押下
3. 最適化結果をダウンロード



# ディレクトリ

```
.
├── README.md
├── .gitignore
├── .dockerignore
├── data
│   └── customers.csv
│   └── visit_probability.csv
├── src
│   └── app_fastapi.py
│   └── app_streamlit.py
│   └── optimizer.py
├── compose.yml
├── .python-version
├── requirements-dev.lock
├── requirements.lock
└── pyproject.toml

```
- data
  - customers.csv
    - 顧客情報
  - visit_probability.csv
    - セグメントごと、DMの違いによるサイト訪問率
- src
  - app_fastapi.py
    - FastAPI実装参考コード(デプロイなし)
  - app_streamlit.py
    - stremalit実装コード
  - optimizer.py
    - 最適化関数

