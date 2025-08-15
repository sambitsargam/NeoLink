from flask import Flask, request, jsonify
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client
import os
import asyncio
from dotenv import load_dotenv
import logging
from simple_agent import create_agent

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Initialize Twilio client
twilio_client = Client(
    os.getenv('TWILIO_ACCOUNT_SID'),
    os.getenv('TWILIO_AUTH_TOKEN')
)

# Initialize DeFi agent (will be created async)
defi_agent = None

async def get_agent():
    """Get or create the DeFi agent"""
    global defi_agent
    if defi_agent is None:
        defi_agent = await create_agent()
    return defi_agent

@app.route('/webhook', methods=['POST'])
def whatsapp_webhook():
    """Handle incoming WhatsApp messages from Twilio"""
    try:
        # Get message details
        from_number = request.form.get('From')
        message_body = request.form.get('Body', '').strip()
        
        logger.info(f"Received message from {from_number}: {message_body}")
        
        # Process the message through our DeFi agent (async)
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            agent = loop.run_until_complete(get_agent())
            response_text = loop.run_until_complete(
                agent.process_whatsapp_message(from_number, message_body)
            )
        finally:
            loop.close()
        
        # Create Twilio response
        resp = MessagingResponse()
        resp.message(response_text)
        
        return str(resp)
        
    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}")
        resp = MessagingResponse()
        resp.message("Sorry, I encountered an error processing your request. Please try again.")
        return str(resp)

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy"})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)