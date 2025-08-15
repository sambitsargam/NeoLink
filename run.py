#!/usr/bin/env python3
"""
Simple runner script for the DeFi WhatsApp Agent
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Check required environment variables
required_vars = [
    'TWILIO_ACCOUNT_SID',
    'TWILIO_AUTH_TOKEN', 
    'OPENAI_API_KEY',
    'PRIVATE_KEY'
]

missing_vars = [var for var in required_vars if not os.getenv(var)]
if missing_vars:
    print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
    print("Please check your .env file")
    sys.exit(1)

print("🚀 Starting DeFi WhatsApp Agent...")
print(f"📱 Twilio Account: {os.getenv('TWILIO_ACCOUNT_SID')[:8]}...")
print(f"🤖 OpenRouter API configured via OpenAI compatibility")
print(f"🔐 Private key configured: {os.getenv('PRIVATE_KEY')[:8]}...")
print(f"⛓️ Chain ID: {os.getenv('CHAIN_ID', '1')}")

# Import and run the Flask app
from app import app

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    print(f"🌐 Server starting on port {port}")
    print(f"📡 Webhook endpoint: http://localhost:{port}/webhook")
    app.run(host='0.0.0.0', port=port, debug=True)