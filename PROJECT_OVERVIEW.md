# 🍯 პროექტის მიმოხილვა / Project Overview

**სოციალური მედიის მარკეტინგის AI აგენტი ორგანული ძმრის ბიზნესისთვის**

---

## 📊 პროექტის არქიტექტურა

### სისტემის დიაგრამა

```
┌─────────────────────────────────────────────────────────────┐
│                    USER (Telegram)                          │
│                          ↓                                  │
│                    /create [honey_type]                     │
└─────────────────────────────┬───────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                  TELEGRAM BOT (telegram_bot.py)             │
│  • Handles commands (/create, /status, /help)              │
│  • Inline keyboard buttons (Approve/Reject/Edit)           │
│  • Sends photos + captions to user                         │
└───────┬─────────────────────────────────────────┬───────────┘
        ↓                                         ↓
┌───────────────────┐                  ┌──────────────────────┐
│  TEXT GENERATOR   │                  │  IMAGE GENERATOR     │
│  (Google Gemini)  │                  │ (Google Vertex AI)   │
│ text_generator.py │                  │  image_generator.py  │
│                   │                  │                      │
│ • Model: gemini-  │                  │ • Model: imagen-     │
│   1.5-flash/pro   │                  │   generation@006     │
│ • Language: ქართული│                  │ • Output: PNG 1:1   │
│ • Tone: friendly  │                  │ • Quality: High     │
└─────────┬─────────┘                  └───────────┬──────────┘
          │                                        │
          └────────────────┬───────────────────────┘
                           ↓
                  ┌──────────────────┐
                  │    DATABASE      │
                  │   database.py    │
                  │                  │
                  │ • SQLite (local) │
                  │ • Tables:        │
                  │   - drafts       │
                  │   - edit_history │
                  └────────┬─────────┘
                           │
                ┌──────────┴──────────┐
                ↓                     ↓
    ┌─────────────────────┐  ┌──────────────────┐
    │  TELEGRAM BOT UI    │  │  STREAMLIT WEB   │
    │  (Review/Approve)   │  │    DASHBOARD     │
    │                     │  │                  │
    │ Inline Buttons:     │  │ • View drafts    │
    │ • ✅ Approve        │  │ • Edit text      │
    │ • 🔄 Regenerate     │  │ • Track history  │
    │ • 🎨 New image      │  │ • Statistics     │
    │ • ✏️ Dashboard      │  │                  │
    └─────────────────────┘  └──────────────────┘
```

---

## 🗂️ ფაილების სტრუქტურა და აღწერა

### 🔧 Core Application Files

#### 1. `main.py` (Main Orchestrator)
**როლი:** აპლიკაციის მთავარი შესვლის წერტილი

**ფუნქციონალი:**
- Environment variables-ის ჩატვირთვა (`.env`)
- Google Cloud credentials-ის setup (Railway-compatible)
- ყველა კომპონენტის ინიციალიზაცია
- Telegram bot-ის გაშვება

**კოდის მაგალითი:**
```python
from config import setup_google_credentials, validate_environment
from database import Database
from text_generator import TextGenerator
from image_generator import ImageGenerator
from telegram_bot import MarketingBot

# Initialize all components
db = Database()
text_gen = TextGenerator(api_key=GEMINI_KEY)
image_gen = ImageGenerator(project_id=GCP_PROJECT)
bot = MarketingBot(token, db, text_gen, image_gen)
```

---

#### 2. `config.py` (Configuration Helper)
**როლი:** Google Cloud credentials-ის მართვა Railway deployment-ისთვის

**ფუნქციონალი:**
- მხარს უჭერს 3 მეთოდს:
  1. `GOOGLE_APPLICATION_CREDENTIALS` (file path - local)
  2. `GOOGLE_APPLICATION_CREDENTIALS_JSON` (JSON string - Railway)
  3. `GOOGLE_CREDENTIALS_BASE64` (base64 - Railway)
- Environment variables-ის ვალიდაცია

**მნიშვნელოვანი ფუნქციები:**
```python
setup_google_credentials()  # Setup GCP auth
validate_environment()       # Check required vars
```

---

#### 3. `text_generator.py` (Google Gemini Integration)
**როლი:** ქართული ტექსტების გენერაცია Facebook პოსტებისთვის

**მახასიათებლები:**
- მოდელი: `gemini-1.5-flash` (სწრაფი) ან `gemini-1.5-pro` (ძლიერი)
- ენა: **ქართული**
- Tones: friendly, professional, enthusiastic

**მთავარი ფუნქციები:**
```python
generate_facebook_post(honey_type, tone, include_emoji, max_length)
generate_honey_info(honey_type)
improve_text(original_text, instruction)
```

**მაგალითი:**
```python
generator = TextGenerator(api_key="...")
post = generator.generate_facebook_post(
    honey_type="ბროწეულის ძმარი",
    tone="friendly",
    include_emoji=True
)
# Output: "🍯 ბუნებრივი ბროწეულის ძმარი..."
```

---

#### 4. `image_generator.py` (Google Vertex AI Imagen)
**როლი:** პროდუქტის ფოტოების გენერაცია

**მახასიათებლები:**
- მოდელი: `imagegeneration@006` (Imagen 2)
- ფორმატი: PNG, 1:1 (square for social media)
- Safety filter: `block_some`

**მთავარი ფუნქციები:**
```python
generate_honey_product_image(prompt, negative_prompt, output_path)
generate_honey_marketing_image(honey_type)
```

**მაგალითი:**
```python
generator = ImageGenerator(project_id="my-project")
image_path = generator.generate_honey_marketing_image("ბროწეულის ძმარი")
# Output: "honey_product_ბროწეულის_ძმარი.png"
```

---

#### 5. `database.py` (SQLite Database)
**როლი:** დრაფტების და რედაქტირების ისტორიის შენახვა

**ცხრილები:**

**`drafts` table:**
```sql
CREATE TABLE drafts (
    id INTEGER PRIMARY KEY,
    honey_type TEXT,
    post_text TEXT,
    image_path TEXT,
    status TEXT,  -- 'draft', 'approved', 'published', 'rejected'
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    telegram_message_id INTEGER
);
```

**`edit_history` table:**
```sql
CREATE TABLE edit_history (
    id INTEGER PRIMARY KEY,
    draft_id INTEGER,
    old_text TEXT,
    new_text TEXT,
    edited_by TEXT,  -- 'user', 'gemini', 'telegram'
    edited_at TIMESTAMP
);
```

**მთავარი ფუნქციები:**
```python
create_draft(honey_type, post_text, image_path)
get_draft(draft_id)
update_draft_text(draft_id, new_text)
update_draft_status(draft_id, status)
get_edit_history(draft_id)
```

---

#### 6. `telegram_bot.py` (Telegram Bot Logic)
**როლი:** მომხმარებლის ინტერაქცია Telegram-ით

**ბრძანებები:**
- `/start` - Welcome message
- `/create [honey_type]` - Generate new post
- `/status` - View all drafts
- `/help` - Help message

**Inline Buttons:**
```python
✅ დადასტურება (approve_<id>)
❌ უარყოფა (reject_<id>)
🔄 ტექსტის შეცვლა (regenerate_text_<id>)
🎨 ფოტოს შეცვლა (regenerate_image_<id>)
✏️ დაშბორდზე რედაქტირება (edit_<id>)
```

**Workflow:**
1. User: `/create ბროწეულის ძმარი`
2. Bot: generates image + text
3. Bot: sends to user with buttons
4. User: clicks button
5. Bot: performs action (approve/regenerate/etc)

---

#### 7. `streamlit_dashboard.py` (Web Dashboard)
**როლი:** ვებ ინტერფეისი დრაფტების რედაქტირებისთვის

**გვერდები:**
1. **📝 დრაფტების მართვა**
   - View all drafts
   - Edit text manually
   - Approve/reject/delete
   - View edit history

2. **➕ ახალი პოსტის შექმნა**
   - Manually create draft
   - Enter honey type + text

3. **📊 სტატისტიკა**
   - Draft count by status
   - Recent activity
   - Honey types summary

**URL parameters:**
- `?draft_id=123` - Opens specific draft (from Telegram)

---

### 📦 Configuration Files

#### 8. `requirements.txt`
Python dependencies - **მხოლოდ Google ტექნოლოგიები!**

```txt
google-generativeai==0.8.3      # Gemini API
google-cloud-aiplatform==1.70.0 # Vertex AI Imagen
google-auth==2.35.0             # Authentication
pyTelegramBotAPI==4.24.0        # Telegram bot
streamlit==1.40.1               # Dashboard
pillow==11.0.0                  # Image processing
python-dotenv==1.0.1            # Environment vars
```

---

#### 9. `Procfile` (Railway Deployment)
Defines Railway processes:

```procfile
bot: python main.py
web: streamlit run streamlit_dashboard.py --server.port=$PORT --server.address=0.0.0.0
```

Railway გაუშვებს **ორივე** პროცესს.

---

#### 10. `runtime.txt` (Python Version)
Specifies Python version for Railway:

```
python-3.11.9
```

---

#### 11. `.env.example` (Environment Template)
Template for `.env` file:

```bash
TELEGRAM_BOT_TOKEN=...
GOOGLE_GEMINI_API_KEY=...
GOOGLE_CLOUD_PROJECT=...
GOOGLE_APPLICATION_CREDENTIALS=...
GCP_LOCATION=us-central1
DASHBOARD_URL=http://localhost:8501
```

---

#### 12. `.gitignore`
Prevents sensitive files from being committed:

```gitignore
.env
*.json  # Service account credentials
*.db    # Database files
__pycache__/
venv/
*.png   # Generated images
```

---

### 📖 Documentation Files

#### 13. `README.md`
სრული დოკუმენტაცია:
- პროექტის აღწერა
- ლოკალური გაშვება
- Railway deployment
- კონფიგურაცია
- პრობლემების გადაჭრა

#### 14. `DEPLOY_RAILWAY.md`
Railway deployment step-by-step:
- Google Cloud setup
- Base64 credentials
- Railway variables
- Troubleshooting

#### 15. `QUICKSTART.md`
სწრაფი დაწყება 5 წუთში:
- Installation
- Quick setup
- Basic usage
- Examples

#### 16. `PROJECT_OVERVIEW.md` (ეს ფაილი)
პროექტის არქიტექტურის სრული აღწერა

---

## 🔄 Data Flow

### Scenario: New Post Creation

```
1. User sends: /create ბროწეულის ძმარი
   ↓
2. telegram_bot.py receives command
   ↓
3. text_generator.py generates Georgian text
   ↓
4. image_generator.py generates product photo
   ↓
5. database.py saves draft (status: 'draft')
   ↓
6. telegram_bot.py sends photo + text + buttons to user
   ↓
7a. User clicks ✅ Approve
    → database.py updates status to 'approved'

7b. User clicks 🔄 Regenerate text
    → text_generator.py generates new text
    → database.py updates text + edit_history
    → telegram_bot.py updates message

7c. User clicks ✏️ Dashboard
    → Opens streamlit_dashboard.py in browser
    → User edits text manually
    → database.py saves changes + edit_history
```

---

## 🔐 Security Architecture

### Secrets Management

**Local Development:**
```
.env file → config.py → main.py
```

**Railway Deployment:**
```
Railway Environment Variables → config.py → temporary file → main.py
```

### Credentials Methods

| Method | Use Case | Security |
|--------|----------|----------|
| File path (`GOOGLE_APPLICATION_CREDENTIALS`) | Local dev | ✅ High |
| JSON string (`GOOGLE_APPLICATION_CREDENTIALS_JSON`) | Railway | ⚠️ Medium |
| Base64 (`GOOGLE_CREDENTIALS_BASE64`) | Railway | ✅ Good |

**Best Practice:** Base64 encoding for Railway (recommended in docs)

---

## 🧪 Testing Strategy

### Component Tests

```python
# Test text generator
python text_generator.py

# Test image generator
python image_generator.py

# Test database
python database.py

# Test config
python config.py
```

### Integration Test

```python
# Full application test
python main.py
# Then in Telegram: /create test ძმარი
```

---

## 📊 Technology Stack Summary

| Layer | Technology | File |
|-------|------------|------|
| **AI - Text** | Google Gemini API | `text_generator.py` |
| **AI - Image** | Google Vertex AI Imagen | `image_generator.py` |
| **Bot** | pyTelegramBotAPI | `telegram_bot.py` |
| **Web UI** | Streamlit | `streamlit_dashboard.py` |
| **Database** | SQLite3 | `database.py` |
| **Deployment** | Railway.app | `Procfile` |
| **Auth** | Google Cloud Auth | `config.py` |

---

## 🚀 Performance Considerations

### API Limits

| Service | Free Tier | Cost |
|---------|-----------|------|
| Gemini API | 60 requests/min | Free |
| Vertex AI Imagen | Pay-per-use | ~$0.02-0.04/image |
| Telegram Bot API | Unlimited | Free |
| Railway Hosting | $5 credit/month | ~$0.000463/min |

### Optimization Tips

1. **Cache generated images** (reuse for similar requests)
2. **Use Gemini Flash** instead of Pro for faster response
3. **Railway sleep mode** when inactive to save credits
4. **Batch database operations** for edit history

---

## 🔮 Future Enhancements

### Planned Features

1. **Auto-posting to Facebook**
   - Schedule posts
   - Direct publishing via Facebook Graph API

2. **Multi-language Support**
   - English posts
   - Russian posts

3. **Image Variations**
   - Multiple image styles
   - A/B testing

4. **Analytics Dashboard**
   - Engagement metrics
   - Best performing posts

5. **Database Migration**
   - PostgreSQL for Railway (persistent storage)
   - Automatic backups

---

## 📞 Support & Contributing

### Getting Help

1. Check [README.md](README.md)
2. Check [DEPLOY_RAILWAY.md](DEPLOY_RAILWAY.md)
3. Check [QUICKSTART.md](QUICKSTART.md)
4. Review logs in Railway Dashboard

### Code Structure Best Practices

- ✅ **Modularity**: Each file has single responsibility
- ✅ **Error handling**: Try-except blocks with user feedback
- ✅ **Logging**: Print statements for debugging
- ✅ **Type hints**: Function parameters documented
- ✅ **Comments**: Georgian + English for clarity

---

**შექმნილია ❤️-ით ორგანული ძმრის ბიზნესისთვის**

**Created with ❤️ for organic honey business**
