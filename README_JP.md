
# 決済ゲートウェイ・シミュレーター

このプロジェクトは、**FastAPI** と **PostgreSQL** を使用して構築された  
**決済ゲートウェイのシミュレーター**です。

実際の決済サービス（Stripe、PayPal など）で使われている  
**設計・考え方・安全対策**を学ぶ目的で作成しました。

バックエンドエンジニア職（特に日本企業向け）の  
ポートフォリオとして使うことを想定しています。

---

## 主な機能

- マーチャント（加盟店）の作成
- APIキーによる認証
- 冪等性（Idempotency）対応の支払い作成
- 支払い・返金の管理
- Webhook（署名付き・再試行あり）
- 非同期処理（async / await）
- Docker を使ったローカル実行

---

## 使用技術

- Python 3.11
- FastAPI
- PostgreSQL
- SQLAlchemy（Async）
- Docker / Docker Compose

---

## 起動方法（ローカル）

```bash
docker compose up --build
```

起動後：

- API: http://localhost:8000
- Swagger UI: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

---

## 認証について

各マーチャントには **APIキー** が発行されます。  
リクエスト時に以下のヘッダーを送信します。

```
X-API-Key: sk_test_********
```

※ APIキーはデータベースに **ハッシュ化して保存**されます。

---

## 冪等性（Idempotency）

支払い作成には **Idempotency-Key** が必須です。

```
Idempotency-Key: payment-001
```

- 同じキー → 同じ支払い結果
- 重複決済を防止

---

## 支払い作成の例

```bash
curl -X POST http://localhost:8000/api/v1/payments   -H "Content-Type: application/json"   -H "X-API-Key: sk_test_XXXX"   -H "Idempotency-Key: payment-001"   -d '{
    "amount": 500,
    "currency": "JPY"
  }'
```

---

## このプロジェクトの目的

- 実務に近いバックエンド設計を学ぶ
- 決済システムの基本構造を理解する
- 日本企業向けの技術ポートフォリオを作成する

---

## ライセンス

MIT License
