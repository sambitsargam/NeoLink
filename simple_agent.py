#!/usr/bin/env python3
"""
Simple DeFi WhatsApp Agent for testing
"""

import os
import asyncio
import logging
import re
from datetime import datetime

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Simple in-memory storage for user wallets
USER_WALLETS = {}

class SimpleDeFiAgent:
    """Simple DeFi WhatsApp Agent"""
    
    def __init__(self):
        """Initialize the agent"""
        self.openai_api_key = os.getenv('OPENAI_API_KEY')

    def is_wallet_address(self, message: str) -> bool:
        """Check if message contains an Ethereum wallet address"""
        eth_address_pattern = r'^0x[a-fA-F0-9]{40}$'
        return bool(re.match(eth_address_pattern, message.strip()))

    def save_user_wallet(self, user_phone: str, wallet_address: str) -> str:
        """Save user wallet address"""
        try:
            # Basic validation
            if not wallet_address.startswith('0x') or len(wallet_address) != 42:
                return "❌ Invalid wallet address format. Please provide a valid Ethereum address starting with 0x"
            
            USER_WALLETS[user_phone] = {
                "wallet_address": wallet_address,
                "created_at": str(datetime.now())
            }
            
            return f"✅ Wallet address saved successfully!\n\nYou can now:\n• Check balances: 'check my ETH balance'\n• Ask about DeFi: 'what is DeFi?'\n• Get help: 'help'"
            
        except Exception as e:
            logger.error(f"Error saving wallet: {str(e)}")
            return f"❌ Error saving wallet address: {str(e)}"

    def get_user_wallet(self, user_phone: str) -> str:
        """Get user's saved wallet address"""
        user_data = USER_WALLETS.get(user_phone)
        if user_data:
            return user_data["wallet_address"]
        return None

    def check_balance(self, wallet_address: str, token_symbol: str = "ETH") -> str:
        """Check token balance (mock implementation)"""
        try:
            # Mock balances for demo
            mock_balances = {
                "ETH": "1.234567",
                "USDC": "1,250.50", 
                "USDT": "890.25",
                "DAI": "500.00"
            }
            
            balance = mock_balances.get(token_symbol, "0.00")
            return f"💰 Balance for {wallet_address[:10]}...{wallet_address[-4:]}: {balance} {token_symbol}"
            
        except Exception as e:
            logger.error(f"Error checking balance: {str(e)}")
            return f"❌ Error checking {token_symbol} balance: {str(e)}"

    async def process_whatsapp_message(self, user_phone: str, message: str) -> str:
        """Process WhatsApp message and return response"""
        try:
            # Check if user is sending a wallet address
            if self.is_wallet_address(message):
                return self.save_user_wallet(user_phone, message.strip())
            
            # Get user's wallet if they have one saved
            user_wallet = self.get_user_wallet(user_phone)
            
            # Handle different message types
            message_lower = message.lower()
            
            if any(word in message_lower for word in ['balance', 'check']):
                if not user_wallet:
                    return "I don't have your wallet address. Please send me your Ethereum wallet address (starts with 0x) to get started."
                
                # Determine token type
                token = "ETH"  # default
                if "usdc" in message_lower:
                    token = "USDC"
                elif "usdt" in message_lower:
                    token = "USDT"
                elif "dai" in message_lower:
                    token = "DAI"
                
                return self.check_balance(user_wallet, token)
            
            elif any(word in message_lower for word in ['help', 'start', 'hello', 'hi']):
                return """🤖 DeFi Assistant Help

Commands I understand:
• Send your wallet address (0x123...) to get started
• "check ETH balance" - Check token balances
• "check USDC balance" - Check USDC balance
• "what is DeFi?" - Learn about DeFi

What would you like to do?"""
            
            elif 'defi' in message_lower:
                return """🔗 DeFi (Decentralized Finance) is a blockchain-based form of finance that doesn't rely on traditional financial institutions.

Key features:
• Decentralized exchanges (DEXs)
• Lending and borrowing protocols
• Yield farming and staking
• Smart contracts for automation

Popular DeFi platforms include Uniswap, Aave, and Compound."""
            
            else:
                return "I'm not sure how to help with that. Type 'help' to see available commands!"
                
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            return "❌ Sorry, I encountered an error. Please try again or type 'help' for assistance."

async def create_agent():
    """Create and initialize the simple DeFi agent"""
    return SimpleDeFiAgent()

# Test function
async def test_agent():
    """Test the agent functionality"""
    print("🚀 Testing Simple DeFi WhatsApp Agent...")
    
    agent = await create_agent()
    
    # Test wallet saving
    test_wallet = "0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8e8"
    response1 = await agent.process_whatsapp_message("test_user", test_wallet)
    print(f"Wallet save response: {response1}")
    
    # Test balance check
    response2 = await agent.process_whatsapp_message("test_user", "check my ETH balance")
    print(f"Balance query response: {response2}")
    
    # Test USDC balance
    response3 = await agent.process_whatsapp_message("test_user", "check my USDC balance")
    print(f"USDC balance response: {response3}")
    
    # Test general query
    response4 = await agent.process_whatsapp_message("test_user", "What is DeFi?")
    print(f"General query response: {response4}")
    
    # Test help
    response5 = await agent.process_whatsapp_message("new_user", "help")
    print(f"Help response: {response5}")

if __name__ == "__main__":
    asyncio.run(test_agent())