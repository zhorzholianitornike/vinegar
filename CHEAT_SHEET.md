# 📋 სწრაფი მითითებები / Quick Reference

**სოციალური მედიის მარკეტინგის აგენტი - Cheat Sheet**

---

## 🚀 სწრაფი დაწყება

### ლოკალურად გაშვება

```bash
# 1. Install
pip install -r requirements.txt

# 2. Configure .env
TELEGRAM_BOT_TOKEN=...
GOOGLE_GEMINI_API_KEY=...
GOOGLE_CLOUD_PROJECT=...
GOOGLE_APPLICATION_CREDENTIALS=/path/to/key.json

# 3. Run bot
python main.py

# 4. Run dashboard (new terminal)
streamlit run streamlit_dashboard.py
```

---

## 📱 Telegram ბრძანებები

```bash
/start              # დაწყება
/create [ძმრის ტიპი]  # ახალი პოსტი
/status             # დრაფტების სია
/help               # დახმარება
```

**მაგალითი:**
```
/create ბროწეულის ძმარი
/create კვირტის ძმარი
/create აკაციის ძმარი
```

---

## 🎛️ Inline ღილაკები

| ღილაკი | მოქმედება |
|--------|-----------|
| ✅ დადასტურება | Approve draft → status: 'approved' |
| ❌ უარყოფა | Reject draft → status: 'rejected' |
| 🔄 ტექსტის შეცვლა | Generate new text (Gemini) |
| 🎨 ფოტოს შეცვლა | Generate new image (Imagen) |
| ✏️ Dashboard | Open Streamlit for manual edit |

---

## ⚙️ Environment Variables

### Required (აუცილებელი)

```bash
TELEGRAM_BOT_TOKEN          # @BotFather-დან
GOOGLE_GEMINI_API_KEY       # ai.google.dev
GOOGLE_CLOUD_PROJECT        # GCP Project ID
```

### GCP Credentials (ერთ-ერთი)

```bash
# Local development
GOOGLE_APPLICATION_CREDENTIALS=/path/to/key.json

# Railway (method 1)
GOOGLE_APPLICATION_CREDENTIALS_JSON={"type":"service_account",...}

# Railway (method 2) - RECOMMENDED
GOOGLE_CREDENTIALS_BASE64=<base64 string>
```

### Optional

```bash
GCP_LOCATION=us-central1              # Default region
GEMINI_MODEL=gemini-1.5-flash         # or gemini-1.5-pro
DASHBOARD_URL=http://localhost:8501   # Dashboard URL
ADMIN_CHAT_ID=123456789               # Admin Telegram ID
```

---

## 🧩 პროექტის სტრუქტურა

```
CC/
├── main.py                    # 🚀 Main entry point
├── config.py                  # ⚙️ Config + credentials
├── text_generator.py          # 📝 Gemini text generation
├── image_generator.py         # 🎨 Imagen image generation
├── telegram_bot.py            # 🤖 Bot logic
├── streamlit_dashboard.py     # 🌐 Web dashboard
├── database.py                # 💾 SQLite database
├── requirements.txt           # 📦 Dependencies
├── Procfile                   # 🚂 Railway config
├── .env                       # 🔐 Local secrets (gitignored)
└── drafts.db                  # 📊 SQLite file (auto-created)
```

---

## 🔧 ფაილების მოდიფიკაცია

### ტექსტის სტილის შეცვლა

**`text_generator.py`:**
```python
# Line ~50
post_text = self.text_gen.generate_facebook_post(
    honey_type=honey_type,
    tone="enthusiastic",  # "friendly", "professional", "enthusiastic"
    include_emoji=True,
    max_length=400        # Default: 300
)
```

### სურათის ფორმატის შეცვლა

**`image_generator.py`:**
```python
# Line ~60
response = model.generate_images(
    prompt=prompt,
    negative_prompt=negative_prompt,
    number_of_images=1,
    aspect_ratio="16:9",  # "1:1", "4:3", "16:9", "9:16"
    safety_filter_level="block_few",  # "block_few", "block_some", "block_most"
)
```

### სურათის prompt-ის შეცვლა

**`image_generator.py`:**
```python
# Line ~90 - customize prompt
prompt = f"""
Your custom prompt here for {honey_type}
Example: rustic wooden table, warm lighting, golden honey...
"""
```

---

## 🗄️ Database Operations

### Python-ში გამოყენება

```python
from database import Database

db = Database()

# Create draft
draft_id = db.create_draft(
    honey_type="ბროწეულის ძმარი",
    post_text="ტექსტი აქ...",
    image_path="photo.png"
)

# Get draft
draft = db.get_draft(draft_id)

# Update text
db.update_draft_text(draft_id, "ახალი ტექსტი", edited_by="user")

# Update status
db.update_draft_status(draft_id, "approved")

# Get history
history = db.get_edit_history(draft_id)

# Get all drafts
all_drafts = db.get_all_drafts()
drafts_approved = db.get_all_drafts(status="approved")
```

---

## 🚂 Railway Deploy

### 1. Base64 Credentials

```bash
# Mac/Linux
cat service-account-key.json | base64 | tr -d '\n' > creds.txt

# Python
python -c "import base64; print(base64.b64encode(open('key.json','rb').read()).decode())"
```

### 2. Railway Variables

```bash
TELEGRAM_BOT_TOKEN=...
GOOGLE_GEMINI_API_KEY=...
GOOGLE_CLOUD_PROJECT=...
GOOGLE_CREDENTIALS_BASE64=<paste base64 here>
GCP_LOCATION=us-central1
DASHBOARD_URL=https://your-app.up.railway.app
```

### 3. Deploy

```bash
git add .
git commit -m "Deploy to Railway"
git push
```

Railway ავტომატურად გააკეთებს deploy-ს.

---

## 🐛 პრობლემების გადაჭრა

### Bot არ პასუხობს

```bash
# შეამოწმე token
curl https://api.telegram.org/bot<TOKEN>/getMe

# ნახე logs
python main.py  # Console output
```

### Imagen არ მუშაობს

```bash
# გააქტიურე API
gcloud services enable aiplatform.googleapis.com

# შეამოწმე credentials
echo $GOOGLE_APPLICATION_CREDENTIALS
cat $GOOGLE_APPLICATION_CREDENTIALS
```

### Database შეცდომა

```bash
# წაშალე და თავიდან შექმენი
rm drafts.db
python main.py  # Auto-creates new DB
```

### Railway Deploy ვერ ხერხდება

```bash
# ნახე build logs
# Railway Dashboard → Deployments → View Logs

# შეამოწმე requirements.txt
pip install -r requirements.txt  # Local test

# შეამოწმე Procfile syntax
cat Procfile
```

---

## 📊 API Limits & Costs

| Service | Free Tier | Cost |
|---------|-----------|------|
| **Gemini API** | 60 req/min | უფასო |
| **Vertex AI Imagen** | - | $0.02-0.04/image |
| **Telegram Bot** | ∞ | უფასო |
| **Railway** | $5/month credit | $0.000463/min |

---

## 🔑 სწრაფი რეფერენსი

### Google Cloud Console URLs

- **Project:** https://console.cloud.google.com/
- **Vertex AI:** https://console.cloud.google.com/vertex-ai
- **Service Accounts:** https://console.cloud.google.com/iam-admin/serviceaccounts
- **APIs:** https://console.cloud.google.com/apis/dashboard

### Gemini API

- **API Keys:** https://ai.google.dev/
- **Docs:** https://ai.google.dev/docs

### Telegram

- **BotFather:** https://t.me/BotFather
- **API Docs:** https://core.telegram.org/bots/api

### Railway

- **Dashboard:** https://railway.app/dashboard
- **Docs:** https://docs.railway.app/

---

## 📝 სწრაფი ტესტირება

```bash
# 1. Check environment
python config.py

# 2. Test text generation
python text_generator.py

# 3. Test image generation
python image_generator.py

# 4. Test database
python database.py

# 5. Run full app
python main.py

# 6. Test in Telegram
/create test ძმარი
```

---

## 📚 დოკუმენტაცია

| ფაილი | მიზანი |
|-------|--------|
| `README.md` | სრული დოკუმენტაცია |
| `QUICKSTART.md` | 5-წუთიანი დაწყება |
| `DEPLOY_RAILWAY.md` | Railway deploy გზამკვლევი |
| `PROJECT_OVERVIEW.md` | არქიტექტურის აღწერა |
| `CHEAT_SHEET.md` | ეს ფაილი |

---

## 🆘 დახმარების მოთხოვნა

1. შეამოწმე [README.md](README.md)
2. ნახე Railway Logs
3. ჩართე debug: `python main.py` და ნახე console output
4. შეამოწმე `.env` ფაილი

---

**🍯 იმედი მაქვს ეს დაგეხმარება! / Hope this helps!**
