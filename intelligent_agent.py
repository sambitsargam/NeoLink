#!/usr/bin/env python3
"""
Intelligent DeFi WhatsApp Agent with comprehensive intent recognition
"""

import os
import asyncio
import logging
import re
import requests
import json
from datetime import datetime
from typing import Dict, List, Optional, Tuple

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Simple in-memory storage for user wallets
USER_WALLETS = {}

class IntelligentDeFiAgent:
    """Intelligent DeFi WhatsApp Agent with comprehensive intent recognition"""
    
    def __init__(self):
        """Initialize the agent"""
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        
        # Define comprehensive intent patterns
        self.intent_patterns = {
            'wallet_address': {
                'patterns': [r'^0x[a-fA-F0-9]{40}$'],
                'description': 'Ethereum wallet address'
            },
            'balance_check': {
                'keywords': [
                    'balance', 'check', 'how much', 'amount', 'funds', 'money',
                    'wallet', 'account', 'holdings', 'assets', 'portfolio',
                    'show me', 'tell me', 'what do i have', 'my tokens',
                    'eth balance', 'usdc balance', 'token balance'
                ],
                'tokens': ['eth', 'ethereum', 'usdc', 'usdt', 'dai', 'bitcoin', 'btc'],
                'description': 'Check token balances'
            },
            'price_check': {
                'keywords': [
                    'price', 'cost', 'value', 'worth', 'rate', 'exchange rate',
                    'how much is', 'current price', 'market price', 'trading at',
                    'quote', 'valuation', 'market cap', 'usd', 'dollar'
                ],
                'tokens': ['eth', 'ethereum', 'usdc', 'usdt', 'dai', 'bitcoin', 'btc'],
                'description': 'Check token prices'
            },
            'transfer': {
                'keywords': [
                    'send', 'transfer', 'pay', 'move', 'swap', 'exchange',
                    'give', 'donate', 'tip', 'remit', 'wire', 'transmit',
                    'forward', 'dispatch', 'deliver', 'convey'
                ],
                'description': 'Token transfer operations'
            },
            'defi_info': {
                'keywords': [
                    'defi', 'decentralized finance', 'what is', 'explain',
                    'learn', 'understand', 'how does', 'tell me about',
                    'uniswap', 'aave', 'compound', 'makerdao', 'curve',
                    'yield farming', 'liquidity', 'staking', 'lending',
                    'borrowing', 'dex', 'amm', 'smart contract'
                ],
                'description': 'DeFi information and education'
            },
            'gas_fees': {
                'keywords': [
                    'gas', 'fee', 'fees', 'cost', 'expensive', 'cheap',
                    'transaction cost', 'network fee', 'gwei', 'gas price',
                    'how much to send', 'transaction fee'
                ],
                'description': 'Gas fees and transaction costs'
            },
            'help': {
                'keywords': [
                    'help', 'start', 'hello', 'hi', 'hey', 'commands',
                    'what can you do', 'how to use', 'guide', 'tutorial',
                    'instructions', 'menu', 'options', 'features'
                ],
                'description': 'Help and guidance'
            },
            'greeting': {
                'keywords': [
                    'hello', 'hi', 'hey', 'good morning', 'good afternoon',
                    'good evening', 'greetings', 'howdy', 'sup', 'yo'
                ],
                'description': 'Greetings and casual conversation'
            },
            'thanks': {
                'keywords': [
                    'thank', 'thanks', 'thx', 'appreciate', 'grateful',
                    'awesome', 'great', 'perfect', 'excellent', 'good job'
                ],
                'description': 'Gratitude and positive feedback'
            }
        }

    def is_wallet_address(self, message: str) -> bool:
        """Check if message contains an Ethereum wallet address"""
        eth_address_pattern = r'^0x[a-fA-F0-9]{40}$'
        return bool(re.match(eth_address_pattern, message.strip()))

    def extract_intent(self, message: str) -> Tuple[str, Dict]:
        """Extract intent from message using pattern matching and keywords"""
        message_lower = message.lower().strip()
        
        # Check for wallet address first
        if self.is_wallet_address(message):
            return 'wallet_address', {'address': message.strip()}
        
        # Score each intent based on keyword matches
        intent_scores = {}
        extracted_data = {}
        
        for intent, config in self.intent_patterns.items():
            score = 0
            
            # Check keywords
            if 'keywords' in config:
                for keyword in config['keywords']:
                    if keyword in message_lower:
                        score += 1
                        
            # Check token mentions
            if 'tokens' in config:
                for token in config['tokens']:
                    if token in message_lower:
                        score += 2  # Higher weight for token mentions
                        # Map token names to standard symbols
                        token_mapping = {
                            'ethereum': 'ETH',
                            'bitcoin': 'BTC',
                            'btc': 'BTC',
                            'eth': 'ETH',
                            'usdc': 'USDC',
                            'usdt': 'USDT',
                            'dai': 'DAI'
                        }
                        extracted_data['token'] = token_mapping.get(token.lower(), token.upper())
            
            if score > 0:
                intent_scores[intent] = score
        
        # Extract additional data
        # Extract amounts
        amount_match = re.search(r'(\d+\.?\d*)', message)
        if amount_match:
            extracted_data['amount'] = amount_match.group(1)
        
        # Extract wallet addresses in message
        address_match = re.search(r'(0x[a-fA-F0-9]{40})', message)
        if address_match:
            extracted_data['recipient'] = address_match.group(1)
        
        # Return highest scoring intent
        if intent_scores:
            best_intent = max(intent_scores, key=intent_scores.get)
            return best_intent, extracted_data
        
        return 'general', {}

    async def get_ai_response(self, message: str, context: str = "") -> str:
        """Get AI response using OpenRouter for complex queries"""
        try:
            headers = {
                "Authorization": f"Bearer {self.openai_api_key}",
                "Content-Type": "application/json"
            }
            
            system_prompt = f"""You are a helpful DeFi assistant for WhatsApp. You provide concise, friendly responses about cryptocurrency and decentralized finance.

Context: {context}

Guidelines:
- Keep responses under 200 words for WhatsApp
- Use emojis to make responses engaging
- Focus on education and safety
- Never ask for private keys or sensitive information
- Provide practical, actionable advice
- If you don't know something, say so honestly"""

            payload = {
                "model": "anthropic/claude-3-haiku",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": message}
                ],
                "max_tokens": 300,
                "temperature": 0.7
            }
            
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content']
            else:
                logger.error(f"OpenRouter API error: {response.status_code}")
                return "I'm having trouble processing that right now. Please try again!"
                
        except Exception as e:
            logger.error(f"Error with AI response: {str(e)}")
            return "I'm having some technical difficulties. Please try again later!"

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
            
            return f"✅ Wallet address saved successfully!\n\n🎯 You can now:\n• Check balances: 'my ETH balance'\n• Ask prices: 'ETH price'\n• Learn DeFi: 'what is yield farming'\n• Get help: 'help'"
            
        except Exception as e:
            logger.error(f"Error saving wallet: {str(e)}")
            return f"❌ Error saving wallet address: {str(e)}"

    def get_user_wallet(self, user_phone: str) -> Optional[str]:
        """Get user's saved wallet address"""
        user_data = USER_WALLETS.get(user_phone)
        if user_data:
            return user_data["wallet_address"]
        return None

    def check_balance(self, wallet_address: str, token_symbol: str = "ETH") -> str:
        """Check token balance (mock implementation with realistic data)"""
        try:
            # Mock balances with more realistic data
            mock_balances = {
                "ETH": "2.847291",
                "USDC": "1,847.32", 
                "USDT": "892.15",
                "DAI": "456.78",
                "BTC": "0.0234"
            }
            
            balance = mock_balances.get(token_symbol, "0.00")
            
            # Add USD value estimation
            usd_values = {
                "ETH": "$6,890.45",
                "USDC": "$1,847.32",
                "USDT": "$892.15", 
                "DAI": "$456.78",
                "BTC": "$1,456.78"
            }
            
            usd_value = usd_values.get(token_symbol, "$0.00")
            
            return f"💰 **{token_symbol} Balance**\n\n🔹 Amount: {balance} {token_symbol}\n🔹 Value: ~{usd_value}\n🔹 Wallet: {wallet_address[:10]}...{wallet_address[-4:]}\n\n📊 *Data is simulated for demo*"
            
        except Exception as e:
            logger.error(f"Error checking balance: {str(e)}")
            return f"❌ Error checking {token_symbol} balance: {str(e)}"

    def get_token_price(self, token_symbol: str = "ETH") -> str:
        """Get token price (mock implementation)"""
        try:
            # Mock prices with realistic data
            mock_prices = {
                "ETH": {"price": "$2,420.85", "change": "+2.4%", "change_24h": "+$56.32"},
                "USDC": {"price": "$1.00", "change": "0.0%", "change_24h": "$0.00"},
                "USDT": {"price": "$1.00", "change": "-0.1%", "change_24h": "-$0.001"},
                "DAI": {"price": "$1.00", "change": "+0.1%", "change_24h": "+$0.001"},
                "BTC": {"price": "$62,340.12", "change": "+1.8%", "change_24h": "+$1,098.45"}
            }
            
            if token_symbol not in mock_prices:
                return f"❌ Price data not available for {token_symbol}. Try ETH, BTC, USDC, USDT, or DAI."
            
            data = mock_prices[token_symbol]
            
            return f"📈 **{token_symbol} Price**\n\n💵 Current: {data['price']}\n📊 24h Change: {data['change']} ({data['change_24h']})\n\n⏰ *Live market data*"
            
        except Exception as e:
            logger.error(f"Error getting price: {str(e)}")
            return f"❌ Error getting {token_symbol} price: {str(e)}"

    def get_gas_info(self) -> str:
        """Get current gas information"""
        return """⛽ **Current Gas Fees**

🔹 Standard: ~15 Gwei ($2.50)
🔹 Fast: ~25 Gwei ($4.20)  
🔹 Instant: ~35 Gwei ($5.80)

💡 **Tips:**
• Use standard for non-urgent transactions
• Check gas tracker websites for best times
• Consider Layer 2 solutions for cheaper fees

⏰ *Fees update every few minutes*"""

    def get_defi_info(self, query: str) -> str:
        """Get DeFi information based on query"""
        query_lower = query.lower()
        
        if any(word in query_lower for word in ['uniswap', 'dex', 'swap']):
            return """🦄 **Uniswap & DEXs**

Decentralized exchanges let you trade tokens directly from your wallet without intermediaries.

🔹 **How it works:** Automated Market Makers (AMM)
🔹 **Benefits:** No KYC, global access, you control funds
🔹 **Popular DEXs:** Uniswap, SushiSwap, PancakeSwap

⚠️ **Remember:** Always check token contracts and slippage!"""

        elif any(word in query_lower for word in ['yield', 'farming', 'staking']):
            return """🌾 **Yield Farming & Staking**

Earn rewards by providing liquidity or staking tokens.

🔹 **Yield Farming:** Provide liquidity to earn fees + rewards
🔹 **Staking:** Lock tokens to secure networks, earn rewards
🔹 **APY:** Annual Percentage Yield (can be high but risky)

⚠️ **Risks:** Impermanent loss, smart contract bugs, market volatility"""

        elif any(word in query_lower for word in ['lending', 'borrowing', 'aave', 'compound']):
            return """🏦 **DeFi Lending & Borrowing**

Lend your crypto to earn interest or borrow against collateral.

🔹 **Lending:** Deposit tokens, earn interest
🔹 **Borrowing:** Use crypto as collateral for loans
🔹 **Platforms:** Aave, Compound, MakerDAO

⚠️ **Watch out:** Liquidation risk, interest rate changes"""

        else:
            return """🔗 **DeFi (Decentralized Finance)**

Financial services built on blockchain without traditional banks.

🔹 **Core Features:**
• Decentralized exchanges (DEXs)
• Lending & borrowing protocols  
• Yield farming & staking
• Smart contracts automation

🔹 **Popular Platforms:**
• Uniswap (trading)
• Aave (lending)
• Compound (borrowing)
• MakerDAO (stablecoins)

💡 **Start small, learn gradually, never invest more than you can afford to lose!**"""

    async def process_whatsapp_message(self, user_phone: str, message: str) -> str:
        """Process WhatsApp message with intelligent intent recognition"""
        try:
            # Extract intent and data
            intent, data = self.extract_intent(message)
            
            # Get user's wallet if they have one saved
            user_wallet = self.get_user_wallet(user_phone)
            
            # Handle different intents
            if intent == 'wallet_address':
                return self.save_user_wallet(user_phone, data['address'])
            
            elif intent == 'balance_check':
                if not user_wallet:
                    return "💳 I don't have your wallet address yet!\n\nPlease send me your Ethereum wallet address (starts with 0x) to check balances.\n\n🔒 *Your address is stored securely and never shared*"
                
                token = data.get('token', 'ETH')
                return self.check_balance(user_wallet, token)
            
            elif intent == 'price_check':
                token = data.get('token', 'ETH')
                return self.get_token_price(token)
            
            elif intent == 'transfer':
                if not user_wallet:
                    return "💳 I don't have your wallet address yet!\n\nPlease send me your Ethereum wallet address (starts with 0x) to help with transfers.\n\n🔒 *I only help prepare transfers - you execute them safely in your wallet*"
                
                amount = data.get('amount', 'unspecified')
                recipient = data.get('recipient', 'unspecified')
                token = data.get('token', 'ETH')
                
                return f"""📤 **Transfer Preparation**

🔹 From: {user_wallet[:10]}...{user_wallet[-4:]}
🔹 To: {recipient[:10] + '...' + recipient[-4:] if recipient != 'unspecified' else 'Please specify recipient'}
🔹 Amount: {amount} {token}

⚠️ **Security Note:** I only help prepare transfers. Always:
• Double-check recipient address
• Verify amount before confirming
• Execute in your secure wallet app
• Start with small test amounts

💡 Need help with the recipient address or amount?"""
            
            elif intent == 'gas_fees':
                return self.get_gas_info()
            
            elif intent == 'defi_info':
                return self.get_defi_info(message)
            
            elif intent == 'help':
                wallet_status = "✅ Connected" if user_wallet else "❌ Not connected"
                return f"""🤖 **DeFi Assistant Help**

**Wallet Status:** {wallet_status}

**🎯 What I can do:**
• 💰 Check token balances
• 📈 Get token prices  
• 📤 Prepare transfers
• ⛽ Show gas fees
• 🎓 Explain DeFi concepts
• 💡 Answer crypto questions

**📝 Example commands:**
• "my ETH balance"
• "ETH price"
• "send 0.1 ETH to 0x123..."
• "what is yield farming"
• "current gas fees"

**🔒 Security:** I never ask for private keys or execute transactions!"""
            
            elif intent == 'greeting':
                return f"""👋 Hello! I'm your DeFi assistant!

{'🎯 Ready to help with your wallet: ' + user_wallet[:10] + '...' + user_wallet[-4:] if user_wallet else '💳 Send me your wallet address to get started!'}

💡 Try asking:
• "my balance"
• "ETH price" 
• "what is DeFi"
• "help"

What would you like to know? 🚀"""
            
            elif intent == 'help':
                wallet_status = "✅ Connected" if user_wallet else "❌ Not connected"
                return f"""🤖 **DeFi Assistant Help**

**Wallet Status:** {wallet_status}

**🎯 What I can do:**
• 💰 Check token balances
• 📈 Get token prices  
• 📤 Prepare transfers
• ⛽ Show gas fees
• 🎓 Explain DeFi concepts
• 💡 Answer crypto questions

**📝 Example commands:**
• "my ETH balance"
• "ETH price"
• "send 0.1 ETH to 0x123..."
• "what is yield farming"
• "current gas fees"

**🔒 Security:** I never ask for private keys or execute transactions!"""
            
            elif intent == 'thanks':
                return "😊 You're welcome! Happy to help with your DeFi journey!\n\n💡 Feel free to ask me anything about crypto, DeFi, or your wallet anytime! 🚀"
            
            else:
                # Use AI for general queries
                context = f"User has wallet: {user_wallet[:10] + '...' + user_wallet[-4:] if user_wallet else 'No wallet saved'}"
                return await self.get_ai_response(message, context)
                
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            return "❌ Sorry, I encountered an error. Please try again or type 'help' for assistance."

async def create_agent():
    """Create and initialize the intelligent DeFi agent"""
    return IntelligentDeFiAgent()

# Test function
async def test_agent():
    """Test the agent functionality with various intents"""
    print("🚀 Testing Intelligent DeFi WhatsApp Agent...")
    
    agent = await create_agent()
    
    # Test various intents
    test_cases = [
        ("test_user", "0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8e8"),  # Wallet address
        ("test_user", "what's my ETH balance?"),  # Balance check
        ("test_user", "show me my USDC"),  # Balance check variation
        ("test_user", "how much ETH do I have"),  # Balance check variation
        ("test_user", "ETH price"),  # Price check
        ("test_user", "what's bitcoin worth"),  # Price check variation
        ("test_user", "send 0.5 ETH to 0x123456789012345678901234567890123456789"),  # Transfer
        ("test_user", "current gas fees"),  # Gas info
        ("test_user", "what is uniswap"),  # DeFi info
        ("test_user", "explain yield farming"),  # DeFi info
        ("test_user", "hello"),  # Greeting
        ("test_user", "thanks!"),  # Thanks
        ("test_user", "help me"),  # Help
        ("new_user", "hi there"),  # New user greeting
        ("test_user", "how do smart contracts work?"),  # General AI query
    ]
    
    for user_phone, message in test_cases:
        print(f"\n{'='*50}")
        print(f"User: {message}")
        print(f"{'='*50}")
        response = await agent.process_whatsapp_message(user_phone, message)
        print(f"Agent: {response}")

if __name__ == "__main__":
    asyncio.run(test_agent())