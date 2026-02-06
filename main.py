"""
Social Media Marketing Agent - Main Application
================================================
Orchestrates the Telegram bot for organic honey marketing.
Integrates Google Gemini for text and Google Vertex AI Imagen for images.

Author: Marketing Agent System
License: MIT
"""

import os
import sys
import threading
from dotenv import load_dotenv

# Import our modules
from config import setup_google_credentials, validate_environment
from database import Database
from text_generator import TextGenerator
from image_generator import ImageGenerator
from scheduler import PostScheduler
from telegram_bot import MarketingBot


def load_environment():
    """Load and validate environment variables."""
    # Load .env file if it exists
    load_dotenv()

    # Setup Google Cloud credentials (Railway-compatible)
    print("\n🔐 Setting up Google Cloud credentials...")
    creds_ok = setup_google_credentials()

    if not creds_ok:
        print("\n⚠️  Google Cloud credentials not configured properly.")
        print("Image generation will not work without credentials.")
        print("\nFor Railway deployment, add one of these environment variables:")
        print("  • GOOGLE_APPLICATION_CREDENTIALS_JSON (entire JSON content)")
        print("  • GOOGLE_CREDENTIALS_BASE64 (base64 encoded JSON)")

    # Validate required environment variables
    status, all_ok = validate_environment()

    if not all_ok:
        print("\n⚠️  Missing required environment variables:\n")
        for var, state in status.items():
            print(f"{state} {var}")
        print("\n💡 Please set these in a .env file or as environment variables.")
        print("\nExample .env file:")
        print("=" * 50)
        print("TELEGRAM_BOT_TOKEN=your_telegram_token_here")
        print("GOOGLE_GEMINI_API_KEY=your_gemini_key_here")
        print("GOOGLE_CLOUD_PROJECT=your_gcp_project_id")
        print("GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json")
        print("GCP_LOCATION=us-central1")
        print("DASHBOARD_URL=http://localhost:8501")
        print("=" * 50)
        sys.exit(1)

    print("✓ Environment variables loaded successfully")


def initialize_components():
    """Initialize all application components."""
    print("\n🚀 Initializing Social Media Marketing Agent...")
    print("=" * 50)

    # Initialize database
    print("\n1️⃣ Initializing database...")
    db = Database()

    # Initialize text generator (Gemini)
    print("\n2️⃣ Initializing Google Gemini text generator...")
    text_gen = TextGenerator(
        api_key=os.getenv("GOOGLE_GEMINI_API_KEY"),
        model_name=os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
    )

    # Initialize image generator (Vertex AI Imagen)
    print("\n3️⃣ Initializing Google Vertex AI image generator...")

    # Check for Google Cloud credentials
    credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    if credentials_path and not os.path.exists(credentials_path):
        print(f"⚠️  Warning: Credentials file not found: {credentials_path}")

    image_gen = ImageGenerator(
        project_id=os.getenv("GOOGLE_CLOUD_PROJECT"),
        location=os.getenv("GCP_LOCATION", "us-central1")
    )

    # Initialize scheduler
    print("\n4️⃣ Initializing post scheduler...")
    scheduler = PostScheduler(database=db)
    scheduler.start_scheduler()  # Start background scheduler thread

    # Initialize Telegram bot
    print("\n5️⃣ Initializing Telegram bot...")
    bot = MarketingBot(
        bot_token=os.getenv("TELEGRAM_BOT_TOKEN"),
        database=db,
        text_generator=text_gen,
        image_generator=image_gen,
        scheduler=scheduler,
        admin_chat_id=os.getenv("ADMIN_CHAT_ID")  # Optional
    )

    print("\n" + "=" * 50)
    print("✅ All components initialized successfully!")
    print("=" * 50)

    return db, text_gen, image_gen, scheduler, bot


def run_telegram_bot(bot: MarketingBot):
    """Run Telegram bot in a separate thread."""
    try:
        bot.start_polling()
    except KeyboardInterrupt:
        print("\n⏸️  Stopping Telegram bot...")
        bot.stop()
    except Exception as e:
        print(f"\n❌ Telegram bot error: {e}")


def main():
    """Main application entry point."""
    print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║                                                           ║
    ║   🍯 სოციალური მედიის მარკეტინგის აგენტი                 ║
    ║      Social Media Marketing Agent                         ║
    ║                                                           ║
    ║   📱 Telegram Bot + 🤖 Google Gemini + 🎨 Vertex AI       ║
    ║                                                           ║
    ╚═══════════════════════════════════════════════════════════╝
    """)

    # Load environment
    load_environment()

    # Initialize components
    db, text_gen, image_gen, scheduler, bot = initialize_components()

    print("\n📋 Application Information:")
    print(f"   • Database: {db.db_path}")
    print(f"   • Gemini Model: {text_gen.model_name}")
    print(f"   • GCP Project: {os.getenv('GOOGLE_CLOUD_PROJECT')}")
    print(f"   • GCP Location: {os.getenv('GCP_LOCATION', 'us-central1')}")
    print(f"   • Dashboard URL: {os.getenv('DASHBOARD_URL', 'http://localhost:8501')}")

    print("\n🎯 How to use:")
    print("   1. Open Telegram and find your bot")
    print("   2. Send: /create ბროწეულის ძმარი")
    print("   3. Review the generated post with photo")
    print("   4. Use inline buttons to approve/edit/regenerate")
    print("   5. Edit text manually at the Streamlit dashboard")

    print("\n📝 Note: Make sure Streamlit dashboard is running separately:")
    print("   streamlit run streamlit_dashboard.py")

    print("\n" + "=" * 50)
    print("🤖 Starting Telegram Bot...")
    print("=" * 50)
    print("\n💡 Press Ctrl+C to stop\n")

    # Run bot
    try:
        run_telegram_bot(bot)
    except KeyboardInterrupt:
        print("\n\n👋 Shutting down gracefully...")
        db.close()
        print("✅ Database closed")
        print("✅ Application stopped")
        print("\nმადლობა! / Thank you!\n")


if __name__ == "__main__":
    main()
