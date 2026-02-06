#!/bin/bash
# Startup script for Railway deployment
# Runs both Telegram bot and Streamlit dashboard

echo "🚀 Starting Social Media Marketing Agent on Railway..."

# Start Streamlit dashboard in background
echo "📊 Starting Streamlit dashboard on port $PORT..."
streamlit run streamlit_dashboard.py \
    --server.port=$PORT \
    --server.address=0.0.0.0 \
    --server.headless=true \
    --browser.gatherUsageStats=false &

# Give Streamlit time to start
sleep 5

# Start Telegram bot in foreground
echo "🤖 Starting Telegram bot..."
python main.py
