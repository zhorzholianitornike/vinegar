# 🚂 Railway.app Deployment Guide
# სრული ინსტრუქცია Railway-ზე Deploy-ისთვის

---

## 📋 სწრაფი დეპლოიმენტის გზამკვლევი

### ნაბიჯი 1: Google Cloud-ის მომზადება

#### 1.1 Service Account-ის შექმნა

```bash
# 1. შესვლა Google Cloud Console-ში
https://console.cloud.google.com/

# 2. პროექტის შექმნა (თუ არ გაქვს)
# Navigation Menu → IAM & Admin → Create a Project

# 3. Vertex AI API-ის გააქტიურება
gcloud services enable aiplatform.googleapis.com
```

#### 1.2 Service Account JSON-ის გადაქცევა Base64-ში (რეკომენდებული Railway-სთვის)

**Mac/Linux:**
```bash
cat service-account-key.json | base64 > credentials-base64.txt
```

**Windows (PowerShell):**
```powershell
[Convert]::ToBase64String([IO.File]::ReadAllBytes("service-account-key.json")) > credentials-base64.txt
```

**Python მეთოდი:**
```python
import base64

with open("service-account-key.json", "rb") as f:
    encoded = base64.b64encode(f.read()).decode('utf-8')
    print(encoded)
```

📋 **დააკოპირე** `credentials-base64.txt`-ის შიგთავსი - დაგჭირდება Railway-ზე!

---

### ნაბიჯი 2: Telegram Bot-ის შექმნა

1. Telegram-ში მოძებნე **@BotFather**
2. გაუგზავნე: `/newbot`
3. მიუთითე bot-ის სახელი და username
4. **დააკოპირე** მიღებული token (მაგ: `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`)

---

### ნაბიჯი 3: Google Gemini API Key-ის მიღება

1. გადადი [Google AI Studio](https://ai.google.dev/)
2. Sign In with Google Account
3. **Get API Key** → **Create API Key**
4. **დააკოპირე** API key

---

### ნაბიჯი 4: Railway პროექტის შექმნა

#### 4.1 GitHub-ზე Code-ის ატვირთვა

```bash
# Git ინიციალიზაცია
git init

# ყველა ფაილის დამატება
git add .

# პირველი commit
git commit -m "Initial commit: Social Media Marketing Agent"

# GitHub repository-ს შექმნა და push
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git branch -M main
git push -u origin main
```

#### 4.2 Railway-ზე Deploy

1. გადადი [Railway.app](https://railway.app/)
2. **Login with GitHub**
3. **New Project** → **Deploy from GitHub repo**
4. აირჩიე შენი repository
5. Railway ავტომატურად დაიწყებს deploy-ს

---

### ნაბიჯი 5: Railway Environment Variables-ის კონფიგურაცია

Railway Dashboard → Your Project → **Variables** → **+ New Variable**

დაამატე შემდეგი ცვლადები:

```bash
# ========== REQUIRED ==========

# 1. Telegram Bot Token
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz

# 2. Google Gemini API Key
GOOGLE_GEMINI_API_KEY=AIzaSyXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

# 3. Google Cloud Project ID
GOOGLE_CLOUD_PROJECT=your-gcp-project-id

# 4. Google Credentials (Base64 encoded) - CRITICAL!
GOOGLE_CREDENTIALS_BASE64=<paste the entire base64 string from credentials-base64.txt>

# ========== OPTIONAL ==========

# 5. GCP Location (default: us-central1)
GCP_LOCATION=us-central1

# 6. Gemini Model
GEMINI_MODEL=gemini-1.5-flash

# 7. Dashboard URL (Railway-ს მიერ გენერირებული URL)
DASHBOARD_URL=https://your-app.up.railway.app
```

**💡 მნიშვნელოვანი:** `GOOGLE_CREDENTIALS_BASE64` უნდა იყოს **ერთი გრძელი string**, ხაზის გადატანების გარეშე!

---

### ნაბიჯი 6: Railway Procfile-ის გააქტიურება

Railway ავტომატურად იყენებს Procfile-ს, რომელიც უკვე შექმნილია:

```procfile
# Telegram bot process
bot: python main.py

# Streamlit dashboard web interface
web: streamlit run streamlit_dashboard.py --server.port=$PORT --server.address=0.0.0.0
```

Railway გაუშვებს **ორივე** პროცესს ერთდროულად.

---

### ნაბიჯი 7: Deploy-ის შემოწმება

#### 7.1 Logs-ის ნახვა

Railway Dashboard → Deployments → **View Logs**

უნდა დაინახო:
```
✓ Google credentials loaded from GOOGLE_CREDENTIALS_BASE64
✓ Environment variables loaded successfully
✓ Database initialized: drafts.db
✓ Text Generator initialized (Model: gemini-1.5-flash)
✓ Image Generator initialized (Project: your-project-id, Location: us-central1)
✓ Telegram Bot initialized
🤖 Telegram Bot started polling...
```

#### 7.2 Dashboard URL-ის მიღება

Railway Dashboard → Deployments → **Domains**

დააკოპირე URL (მაგ: `https://your-app-name.up.railway.app`)

---

### ნაბიჯი 8: ტესტირება

#### 8.1 Telegram Bot-ის ტესტი

1. Telegram-ში მოძებნე შენი bot-ი
2. გაუგზავნე:
   ```
   /start
   ```
3. შექმენი პოსტი:
   ```
   /create ბროწეულის ძმარი
   ```

#### 8.2 Dashboard-ის ტესტი

ბრაუზერში გახსენი: `https://your-app.up.railway.app`

უნდა დაინახო Streamlit dashboard.

---

## 🔧 პრობლემების გადაჭრა

### პრობლემა 1: "Credentials not found"

**გადაწყვეტა:**
```bash
# შეამოწმე Railway Variables-ში GOOGLE_CREDENTIALS_BASE64 არის თუ არა
# დარწმუნდი რომ არის სრული base64 string (ხაზის გადატანების გარეშე)

# ხელახლა გადააქციე base64-ში:
cat service-account-key.json | base64 | tr -d '\n' > credentials-base64.txt
```

### პრობლემა 2: "Module not found"

**გადაწყვეტა:**
Railway Logs → Build logs → ნახე რომელი module ვერ მოიძებნა

შეცვალე `requirements.txt` და push:
```bash
git add requirements.txt
git commit -m "Update dependencies"
git push
```

### პრობლემა 3: Telegram Bot არ პასუხობს

**გადაწყვეტა:**
```bash
# შეამოწმე bot token სისწორე:
curl https://api.telegram.org/bot<YOUR_TOKEN>/getMe

# თუ შეცდომა აქვს, განაახლე Railway Variables-ში TELEGRAM_BOT_TOKEN
```

### პრობლემა 4: Vertex AI API Error

**გადაწყვეტა:**
```bash
# დარწმუნდი რომ Vertex AI API გააქტიურებული გაქვს:
gcloud services enable aiplatform.googleapis.com --project=YOUR_PROJECT_ID

# შეამოწმე Service Account-ის permission:
# Cloud Console → IAM & Admin → Service Accounts
# უნდა ჰქონდეს როლი: "Vertex AI User"
```

---

## 📊 Railway-ზე Monitoring

### Logs-ის ნახვა (Real-time)

Railway Dashboard → Deployments → **View Logs**

### Database-ის ნახვა

Railway-ზე SQLite ფაილი (`drafts.db`) შენახულია container-ის file system-ში.

**⚠️ მნიშვნელოვანი:** Container restart-ის შემდეგ database წაიშლება!

**გადაწყვეტა:** გამოიყენე Railway Volumes:

```bash
# Railway Dashboard → Your Service → Settings → Volumes
# Add Volume: /data
# შეცვალე database.py-ში: DATABASE_PATH=/data/drafts.db
```

---

## 🔄 განახლებების Deploy-ი

კოდის შეცვლის შემდეგ:

```bash
git add .
git commit -m "Update: [describe changes]"
git push
```

Railway **ავტომატურად** გააკეთებს redeploy-ს!

---

## 💰 Railway Pricing

- **Free Plan**: $5 credit/month
- Compute: ~$0.000463/min
- **საკმარისია** ტესტირებისთვის და პატარა ბიზნესებისთვის

**რჩევა:** გამოირთე bot-ი, როცა არ გჭირდება, რომ არ დახარჯო credits:
```bash
# Railway Dashboard → Service → Settings → Sleep when inactive: ON
```

---

## ✅ Deploy Checklist

- [ ] Google Cloud Project შექმნილია
- [ ] Vertex AI API გააქტიურებულია
- [ ] Service Account JSON base64-ში გადაქცეული
- [ ] Telegram Bot Token მიღებული @BotFather-სგან
- [ ] Google Gemini API Key მიღებული
- [ ] GitHub repository შექმნილი და code push-ნილი
- [ ] Railway project შექმნილი
- [ ] ყველა Environment Variable დაყენებული
- [ ] Deploy წარმატებით დასრულდა (logs შეამოწმე)
- [ ] Bot-ი პასუხობს Telegram-ში
- [ ] Dashboard ხელმისაწვდომია ბრაუზერში

---

**🎉 გილოცავ! აგენტი მზადაა მუშაობისთვის Railway-ზე!**

დამატებითი დახმარებისთვის: [README.md](README.md)
