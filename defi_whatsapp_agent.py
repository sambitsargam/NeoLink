#!/usr/bin/env python3
"""
NeoLink DeFi WhatsApp Agent - Spoon AI Implementation
Conversational DeFi assistant with Spoon AI SDK integration and Neo blockchain focus
"""

import os
import sys
import asyncio
import logging
import re
import json
import aiohttp
import requests
from typing import Dict, Any, Optional, List
from datetime import datetime
from web3 import Web3
from dotenv import load_dotenv

# Spoon AI SDK imports
from spoon_ai.agents.spoon_react_mcp import SpoonReactMCP

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Web3 for real blockchain data
RPC_URL = os.getenv('RPC_URL', 'https://eth.llamarpc.com')
w3 = Web3(Web3.HTTPProvider(RPC_URL))

# Token contracts for real data - Multi-chain support
TOKEN_CONTRACTS = {
    # Ethereum Mainnet
    'USDC': '0xA0b86a33E6441b8C4505E2c52C6b6046d4b0b8e8',
    'USDT': '0xdAC17F958D2ee523a2206206994597C13D831ec7',
    'DAI': '0x6B175474E89094C44Da98b954EedeAC495271d0F',
    # Neo N3 - Special focus
    'NEO': 'neo_native',
    'GAS': 'gas_native',
    'NNEO': '0x17104cccccccccccccccccccccccccccccccccc',  # Neo N3 wrapped
}

# Comprehensive token symbol mapping for all chains
COMPREHENSIVE_TOKEN_MAPPING = {
    # Major cryptocurrencies
    'bitcoin': 'BTC', 'btc': 'BTC',
    'ethereum': 'ETH', 'eth': 'ETH', 'ether': 'ETH',
    
    # Neo ecosystem (special focus)
    'neo': 'NEO', 'neocoin': 'NEO', 'neo token': 'NEO',
    'gas': 'GAS', 'neo gas': 'GAS', 'neogas': 'GAS',
    'nneo': 'NNEO', 'wrapped neo': 'NNEO',
    'flamingo': 'FLM', 'flm': 'FLM',
    'neoburger': 'BURGER', 'burger': 'BURGER',
    
    # Popular altcoins
    'algorand': 'ALGO', 'algo': 'ALGO',
    'cardano': 'ADA', 'ada': 'ADA',
    'polkadot': 'DOT', 'dot': 'DOT',
    'solana': 'SOL', 'sol': 'SOL',
    'polygon': 'MATIC', 'matic': 'MATIC',
    'avalanche': 'AVAX', 'avax': 'AVAX',
    'chainlink': 'LINK', 'link': 'LINK',
    'uniswap': 'UNI', 'uni': 'UNI',
    'aave': 'AAVE',
    'compound': 'COMP', 'comp': 'COMP',
    'maker': 'MKR', 'mkr': 'MKR',
    'curve': 'CRV', 'crv': 'CRV',
    'synthetix': 'SNX', 'snx': 'SNX',
    'binance coin': 'BNB', 'bnb': 'BNB',
    'ripple': 'XRP', 'xrp': 'XRP',
    'dogecoin': 'DOGE', 'doge': 'DOGE',
    'shiba inu': 'SHIB', 'shib': 'SHIB', 'shiba': 'SHIB',
    'litecoin': 'LTC', 'ltc': 'LTC',
    'bitcoin cash': 'BCH', 'bch': 'BCH',
    'ethereum classic': 'ETC', 'etc': 'ETC',
    'filecoin': 'FIL', 'fil': 'FIL',
    'cosmos': 'ATOM', 'atom': 'ATOM',
    
    # Stablecoins
    'usdc': 'USDC', 'usd coin': 'USDC',
    'usdt': 'USDT', 'tether': 'USDT',
    'dai': 'DAI', 'dai stablecoin': 'DAI',
    'busd': 'BUSD', 'binance usd': 'BUSD',
    'tusd': 'TUSD', 'trueusd': 'TUSD',
    
    # Layer 2 & Other chains
    'arbitrum': 'ARB', 'arb': 'ARB',
    'optimism': 'OP', 'op': 'OP',
    'immutable': 'IMX', 'imx': 'IMX',
    'loopring': 'LRC', 'lrc': 'LRC',
    
    # Meme coins
    'pepe': 'PEPE',
    'wojak': 'WOJAK',
    'bonk': 'BONK',
}

# ERC-20 ABI for balance checking
ERC20_ABI = [
    {
        "constant": True,
        "inputs": [{"name": "_owner", "type": "address"}],
        "name": "balanceOf",
        "outputs": [{"name": "balance", "type": "uint256"}],
        "type": "function"
    },
    {
        "constant": True,
        "inputs": [],
        "name": "decimals",
        "outputs": [{"name": "", "type": "uint8"}],
        "type": "function"
    }
]

# Simple in-memory storage for user wallets
USER_WALLETS = {}

class RealDataService:
    """Service for fetching real blockchain and market data"""
    
    def __init__(self):
        self.w3 = w3
        
    async def get_eth_balance(self, address: str) -> float:
        """Get real ETH balance"""
        try:
            # Convert to checksum address
            checksum_address = w3.to_checksum_address(address)
            balance_wei = w3.eth.get_balance(checksum_address)
            balance_eth = w3.from_wei(balance_wei, 'ether')
            return float(balance_eth)
        except Exception as e:
            logger.error(f"Error getting ETH balance: {e}")
            return 0.0

    async def get_token_balance(self, address: str, token_symbol: str) -> float:
        """Get real ERC-20 token balance"""
        try:
            if token_symbol not in TOKEN_CONTRACTS:
                return 0.0
                
            # Convert to checksum address
            checksum_address = w3.to_checksum_address(address)
            contract_address = TOKEN_CONTRACTS[token_symbol]
            contract = self.w3.eth.contract(address=contract_address, abi=ERC20_ABI)
            
            balance = contract.functions.balanceOf(checksum_address).call()
            decimals = contract.functions.decimals().call()
            
            return balance / (10 ** decimals)
        except Exception as e:
            logger.error(f"Error getting {token_symbol} balance: {e}")
            return 0.0

    async def get_token_price(self, token_symbol: str) -> dict:
        """Get token price from multiple sources including Neo Chain"""
        try:
            # Special handling for Neo ecosystem
            if token_symbol.upper() in ['NEO', 'GAS', 'NNEO', 'FLM', 'BURGER']:
                return await self.get_neo_chain_price(token_symbol)
            
            # Comprehensive token mapping for all major cryptocurrencies
            token_map = {
                # Major cryptocurrencies  
                'ETH': 'ethereum', 'BTC': 'bitcoin',
                'ALGO': 'algorand', 'ADA': 'cardano', 'DOT': 'polkadot',
                'SOL': 'solana', 'MATIC': 'matic-network', 'AVAX': 'avalanche-2',
                'LINK': 'chainlink', 'UNI': 'uniswap', 'AAVE': 'aave',
                'COMP': 'compound-governance-token', 'MKR': 'maker',
                'CRV': 'curve-dao-token', 'SNX': 'havven', 'BNB': 'binancecoin',
                'XRP': 'ripple', 'DOGE': 'dogecoin', 'SHIB': 'shiba-inu',
                'LTC': 'litecoin', 'BCH': 'bitcoin-cash', 'ETC': 'ethereum-classic',
                'FIL': 'filecoin', 'ATOM': 'cosmos',
                # Stablecoins
                'USDC': 'usd-coin', 'USDT': 'tether', 'DAI': 'dai',
                'BUSD': 'binance-usd', 'TUSD': 'true-usd',
                # Layer 2 & Others
                'ARB': 'arbitrum', 'OP': 'optimism', 'IMX': 'immutable-x',
                'LRC': 'loopring', 'PEPE': 'pepe', 'BONK': 'bonk',
                # Neo ecosystem
                'NEO': 'neo', 'GAS': 'gas', 'FLM': 'flamingo-finance'
            }
            
            token_id = token_map.get(token_symbol.upper(), token_symbol.lower())
            
            async with aiohttp.ClientSession() as session:
                url = f"https://api.coingecko.com/api/v3/simple/price?ids={token_id}&vs_currencies=usd&include_24hr_change=true&include_market_cap=true"
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        if token_id in data:
                            return {
                                'price': data[token_id]['usd'],
                                'change_24h': data[token_id]['usd_24h_change'],
                                'market_cap': data[token_id].get('usd_market_cap', 0)
                            }
            return None
        except Exception as e:
            logger.error(f"Error getting price for {token_symbol}: {e}")
            return None

    async def get_neo_chain_price(self, token_symbol: str) -> dict:
        """Get Neo chain token prices with special handling"""
        try:
            token_map = {
                'NEO': 'neo',
                'GAS': 'gas', 
                'NNEO': 'neo',  # Fallback to NEO price
                'FLM': 'flamingo-finance',
                'BURGER': 'neoburger'
            }
            
            token_id = token_map.get(token_symbol.upper(), token_symbol.lower())
            
            async with aiohttp.ClientSession() as session:
                url = f"https://api.coingecko.com/api/v3/simple/price?ids={token_id}&vs_currencies=usd&include_24hr_change=true&include_market_cap=true"
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        if token_id in data:
                            return {
                                'price': data[token_id]['usd'],
                                'change_24h': data[token_id]['usd_24h_change'],
                                'market_cap': data[token_id].get('usd_market_cap', 0)
                            }
            return None
            
        except Exception as e:
            logger.error(f"Error getting Neo chain price for {token_symbol}: {e}")
            return None
        except Exception as e:
            logger.error(f"Error getting price for {token_symbol}: {e}")
            return None

    async def get_gas_price(self) -> dict:
        """Get current gas prices"""
        try:
            etherscan_key = os.getenv('ETHERSCAN_API_KEY')
            
            async with aiohttp.ClientSession() as session:
                # Try EthGasStation API alternative with API key
                if etherscan_key:
                    url = f"https://api.etherscan.io/api?module=gastracker&action=gasoracle&apikey={etherscan_key}"
                else:
                    url = "https://api.etherscan.io/api?module=gastracker&action=gasoracle"
                
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data.get('status') == '1':
                            result = data['result']
                            return {
                                'safe': int(float(result['SafeGasPrice'])),
                                'standard': int(float(result['ProposeGasPrice'])),
                                'fast': int(float(result['FastGasPrice']))
                            }
                
                # Fallback to alternative API
                url = "https://gas-api.metaswap.codefi.network/networks/1/suggestedGasFees"
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {
                            'safe': int(float(data['low']['suggestedMaxFeePerGas'])),
                            'standard': int(float(data['medium']['suggestedMaxFeePerGas'])),
                            'fast': int(float(data['high']['suggestedMaxFeePerGas']))
                        }
            
            # Final fallback to Web3 estimation
            if hasattr(self, 'w3') and self.w3.is_connected():
                gas_price = self.w3.eth.gas_price
                gas_gwei = self.w3.from_wei(gas_price, 'gwei')
                return {
                    'safe': int(gas_gwei * 0.8),
                    'standard': int(gas_gwei),
                    'fast': int(gas_gwei * 1.2)
                }
            else:
                # Hardcoded reasonable estimates if all else fails
                return {
                    'safe': 12,
                    'standard': 15,
                    'fast': 20
                }
                
        except Exception as e:
            logger.error(f"Error getting gas prices: {e}")
            # Return reasonable estimates
            return {
                'safe': 12,
                'standard': 15,
                'fast': 20
            }
            return {'safe': 15, 'standard': 20, 'fast': 25}

class NeoLinkSpoonAgent(SpoonReactMCP):
    """DeFi WhatsApp agent using Spoon AI SDK with Neo blockchain focus"""
    
    def __init__(self):
        # Initialize SpoonReactMCP with OpenRouter configuration
        super().__init__(
            llm_client="openrouter",
            model="anthropic/claude-3-haiku", 
            api_key=os.getenv('OPENROUTER_API_KEY'),
            system_prompt="""You are a friendly, enthusiastic crypto and DeFi expert specializing in Neo blockchain and multi-chain DeFi. 

Your personality:
- Conversational and warm, like chatting with a friend ☕
- Use emojis naturally to make responses engaging 😊  
- Explain complex concepts in simple terms
- Always enthusiastic about crypto but honest about risks
- Keep responses under 250 words for WhatsApp
- Focus on Neo ecosystem when relevant 
- Support all major blockchains and tokens

For price queries, extract the token symbol and provide accurate analysis.
For educational queries, provide helpful explanations.
Never ask for private keys or sensitive information.

When users mention token prices like "Algo price", "NEO price", "ETH price", etc., 
focus on that specific token and provide current market data."""
        )
        
        self.data_service = RealDataService()
        self.user_wallets = {}  # Store user wallet addresses
    
    async def process_whatsapp_message(self, user_phone: str, message: str) -> str:
        """Process WhatsApp message using Spoon AI with crypto context"""
        try:
            logger.info(f"Processing message from {user_phone}: {message}")
            
            # Check if user is sending a wallet address
            if re.match(r'^0x[a-fA-F0-9]{40}$', message.strip()):
                return await self._handle_wallet_address(user_phone, message.strip())
            
            # Extract token symbols for price queries
            token_context = self._extract_token_context(message)
            
            # Get user context
            user_wallet = self.user_wallets.get(user_phone)
            context_parts = []
            
            if user_wallet:
                context_parts.append(f"User wallet: {user_wallet[:10]}...{user_wallet[-6:]}")
            else:
                context_parts.append("User has no wallet connected")
            
            if token_context:
                context_parts.append(f"User is asking about: {token_context}")
                
                # Handle direct price queries with real data
                if any(word in message.lower() for word in ['price', 'cost', 'worth', 'value']):
                    return await self._get_token_price_response(token_context)
            
            # Handle gas fee queries
            if any(word in message.lower() for word in ['gas', 'fees', 'gwei', 'transaction cost']):
                return await self._get_gas_fees_response()
            
            context = " | ".join(context_parts)
            
            # Use Spoon AI to process the message with context
            enhanced_message = f"Context: {context}\n\nUser message: {message}"
            response = await self.run(user_input=enhanced_message)
            
            logger.info(f"Spoon AI response generated: {response[:100]}...")
            return response
            
        except Exception as e:
            logger.error(f"Error processing message with Spoon AI: {str(e)}")
            return "Oops! Something went wrong on my end. Could you try that again? I promise I'm usually more reliable than this! 😅"

    def _extract_token_context(self, message: str) -> str:
        """Extract token symbols from message"""
        message_lower = message.lower().strip()
        
        crypto_tokens = {
            'algo': 'ALGO', 'algorand': 'ALGO',
            'neo': 'NEO', 'gas': 'GAS', 'nneo': 'NNEO',
            'eth': 'ETH', 'ethereum': 'ETH',
            'btc': 'BTC', 'bitcoin': 'BTC', 
            'ada': 'ADA', 'cardano': 'ADA',
            'dot': 'DOT', 'polkadot': 'DOT',
            'sol': 'SOL', 'solana': 'SOL',
            'matic': 'MATIC', 'polygon': 'MATIC',
            'avax': 'AVAX', 'avalanche': 'AVAX',
            'link': 'LINK', 'chainlink': 'LINK',
            'uni': 'UNI', 'uniswap': 'UNI',
            'aave': 'AAVE', 'comp': 'COMP',
            'mkr': 'MKR', 'maker': 'MKR',
            'crv': 'CRV', 'curve': 'CRV',
            'bnb': 'BNB', 'binance': 'BNB',
            'xrp': 'XRP', 'ripple': 'XRP',
            'doge': 'DOGE', 'dogecoin': 'DOGE',
            'shib': 'SHIB', 'shiba': 'SHIB'
        }
        
        for token_name, symbol in crypto_tokens.items():
            if token_name in message_lower:
                return symbol
        
        return None

    async def _get_token_price_response(self, token_symbol: str) -> str:
        """Get real token price with enthusiastic response"""
        try:
            price_data = await self.data_service.get_token_price(token_symbol)
            
            if not price_data:
                return f"❌ Couldn't find price data for {token_symbol}. Could you check the symbol? I support most major cryptocurrencies including Neo ecosystem tokens! 🔍"

            price = price_data['price']
            change_24h = price_data['change_24h']
            change_emoji = "📈" if change_24h > 0 else "📉"
            
            if price > 1000:
                price_str = f"${price:,.2f}"
            elif price > 1:
                price_str = f"${price:.4f}"
            else:
                price_str = f"${price:.8f}".rstrip('0').rstrip('.')

            sentiment = self._get_price_sentiment(change_24h)

            return f"""🔥 **{token_symbol} Price Update** 🔥

💰 **Current Price:** {price_str}
{change_emoji} **24h Change:** {change_24h:+.2f}%

{sentiment}

Want to check another token or need help with anything else? 😊"""
        
        except Exception as e:
            logger.error(f"Error getting price for {token_symbol}: {e}")
            return f"Oops! Having trouble getting {token_symbol} price right now. The APIs might be busy. Try again in a moment! 😅"

    async def _get_gas_fees_response(self) -> str:
        """Get gas fees with conversational response"""
        try:
            gas_data = await self.data_service.get_gas_price()
            
            return f"""⛽ **Current Gas Fees** ⛽

🟢 **Safe:** {gas_data['safe']} Gwei
🟡 **Standard:** {gas_data['standard']} Gwei  
🔴 **Fast:** {gas_data['fast']} Gwei

💡 **Pro Tips:**
• Use Safe for non-urgent transactions
• Weekends are usually cheaper! 📅
• Try Layer 2 solutions like Polygon for way lower fees 🌉

Gas updates constantly - if it's too high, grab a coffee and check back later! ☕😊"""
            
        except Exception as e:
            logger.error(f"Error getting gas fees: {e}")
            return "Having trouble checking gas fees right now. But between you and me, it's probably expensive! 😅 Maybe try Layer 2 solutions?"

    async def _handle_wallet_address(self, user_phone: str, wallet_address: str) -> str:
        """Handle wallet address submission"""
        try:
            # Validate Ethereum address format
            if not re.match(r'^0x[a-fA-F0-9]{40}$', wallet_address):
                return "That doesn't look like a valid Ethereum address! Make sure it starts with 0x and is 42 characters long. 🤔"
            
            self.user_wallets[user_phone] = wallet_address
            
            return f"""✅ **Wallet Connected!** ✅

Your wallet {wallet_address[:10]}...{wallet_address[-6:]} is now linked! 🔗

I can now help you with:
• Check your token balances 💰
• Monitor your portfolio 📊  
• DeFi strategy advice 🎯
• Transaction guidance ⚡

What would you like to explore first? 😄"""
            
        except Exception as e:
            logger.error(f"Error handling wallet address: {e}")
            return "Oops! Had trouble saving your wallet. Could you try again? 😅"

    def _get_price_sentiment(self, change_24h: float) -> str:
        """Get enthusiastic price sentiment"""
        if change_24h > 10:
            return "🚀 TO THE MOON! What a pump! 🌙"
        elif change_24h > 5:
            return "📈 Nice gains! The bulls are running!"  
        elif change_24h > 0:
            return "💚 Green candles! Slow and steady!"
        elif change_24h > -5:
            return "😐 Just a little dip, nothing major!"
        elif change_24h > -10:
            return "📉 Ouch, red day. But we hodl! 💎🙌"
        else:
            return "🩸 Major correction! Perfect buying opportunity? 🤔"
        
        # Store user data for context
        self.user_wallets = {}

    def is_wallet_address(self, message: str) -> bool:
        """Check if message contains an Ethereum wallet address"""
        eth_address_pattern = r'^0x[a-fA-F0-9]{40}$'
        return bool(re.match(eth_address_pattern, message.strip()))

    def extract_token_symbol(self, message: str) -> str:
        """Extract token symbol from message using comprehensive mapping"""
        message_lower = message.lower().strip()
        
        # Check for exact matches in our comprehensive mapping
        for token_name, symbol in COMPREHENSIVE_TOKEN_MAPPING.items():
            if token_name in message_lower:
                # Prefer longer matches (e.g., "bitcoin cash" over "bitcoin")
                return symbol
        
        # Check for common patterns like "ALGO price", "BTC value", etc.
        import re
        token_pattern = r'\b([A-Z]{2,10})\b'  # 2-10 uppercase letters
        matches = re.findall(token_pattern, message.upper())
        
        for match in matches:
            if match in ['USD', 'API', 'URL', 'FAQ', 'CEO', 'CTO']:  # Skip common non-crypto words
                continue
            # Check if it's a known token symbol
            if match in [symbol for symbol in COMPREHENSIVE_TOKEN_MAPPING.values()]:
                return match
        
        return None

    async def get_ai_response(self, message: str, context: str = "") -> str:
        """Get conversational AI response using OpenRouter with crypto intelligence"""
        try:
            # Get API key from environment
            openrouter_api_key = os.getenv('OPENROUTER_API_KEY')
            if not openrouter_api_key:
                logger.error("No OpenRouter API key found")
                return "I'm having trouble accessing my AI capabilities right now. Try again in a moment! 🤔"
            
            headers = {
                "Authorization": f"Bearer {openrouter_api_key}",
                "Content-Type": "application/json"
            }
            
            # Enhanced system prompt with crypto expertise
            system_prompt = f"""You are an expert crypto and DeFi assistant with deep knowledge of ALL blockchains, especially Neo blockchain. You're enthusiastic, friendly, and always provide accurate information.

Your expertise includes:
🔗 **Multi-chain knowledge**: Bitcoin, Ethereum, Neo, Solana, Cardano, Polygon, Avalanche, and 100+ more
💰 **Real-time data access**: Can provide live prices, gas fees, and blockchain data
🎓 **DeFi education**: Uniswap, Aave, Compound, yield farming, staking, liquidity mining
⛓️ **Neo blockchain specialist**: NEO, GAS, Flamingo (FLM), N3 ecosystem, Neo smart contracts

Context: {context}

Guidelines:
- Be conversational and enthusiastic about crypto! 😊
- If user asks about token prices, suggest they can get REAL live data
- For Neo tokens (NEO, GAS, FLM), provide extra insights about the Neo ecosystem
- Keep responses under 250 words for WhatsApp
- Use emojis naturally 
- Never ask for private keys or sensitive info
- If you don't know something specific, be honest but helpful

Original message: "{message}"

Respond naturally as if chatting with a crypto enthusiast friend!"""

            payload = {
                "model": "anthropic/claude-3-haiku",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": message}
                ],
                "max_tokens": 400,
                "temperature": 0.7
            }
            
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=15
            )
            
            if response.status_code == 200:
                result = response.json()
                ai_response = result['choices'][0]['message']['content']
                
                # Post-process to add real data suggestions
                ai_response = self.enhance_ai_response_with_suggestions(ai_response, message)
                return ai_response
            else:
                logger.error(f"OpenRouter API error: {response.status_code} - {response.text}")
                return "I'm having trouble thinking right now! 🤔 Give me a second and try again?"
                
        except Exception as e:
            logger.error(f"Error with AI response: {str(e)}")
            return "Oops! My brain had a little hiccup there! 😅 Could you try asking again?"

    def enhance_ai_response_with_suggestions(self, ai_response: str, original_message: str) -> str:
        """Enhance AI response with actionable suggestions for real data"""
        message_lower = original_message.lower()
        
        # If user mentions price-related terms, add suggestion for real data
        if any(word in message_lower for word in ['price', 'cost', 'worth', 'value', 'expensive', 'cheap']):
            ai_response += "\n\n💡 *Want live prices? Just ask me like 'ETH price' or 'ALGO price' and I'll get you real-time data!*"
        
        # If user mentions Neo ecosystem
        if any(word in message_lower for word in ['neo', 'gas', 'flamingo', 'flm']):
            ai_response += "\n\n🔗 *Neo blockchain fan? I can get live NEO, GAS, and FLM prices plus Neo ecosystem insights!*"
        
        # If user mentions gas or fees
        if any(word in message_lower for word in ['gas', 'fee', 'fees', 'transaction']):
            ai_response += "\n\n⛽ *Need current gas fees? Just ask 'gas fees' for real-time Ethereum network costs!*"
        
        return ai_response

    def save_user_wallet(self, user_phone: str, wallet_address: str) -> str:
        """Save user wallet address with conversational response"""
        try:
            # Basic validation
            if not wallet_address.startswith('0x') or len(wallet_address) != 42:
                return """Hmm, that doesn't look like a valid Ethereum wallet address to me! 🤔 

I need an address that starts with '0x' and has 42 characters total. Could you double-check and send it again? 

For example: 0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8e8

Don't worry, I'll keep it safe and never share it with anyone! 🔒"""
            
            USER_WALLETS[user_phone] = {
                "wallet_address": wallet_address,
                "created_at": str(datetime.now())
            }
            
            return f"""Perfect! I've got your wallet saved now! 🎉

Your address: {wallet_address[:10]}...{wallet_address[-6:]}

Now I can help you with all sorts of things! You can ask me:
• "What's my ETH balance?" 
• "How much is Ethereum worth today?"
• "Tell me about DeFi"
• Or just chat about crypto! 💬

What would you like to know first? 😊"""
            
        except Exception as e:
            logger.error(f"Error saving wallet: {str(e)}")
            return "Oops! Something went wrong saving that. Could you try sending your wallet address again? 😅"

    def get_user_wallet(self, user_phone: str) -> Optional[str]:
        """Get user's saved wallet address"""
        user_data = USER_WALLETS.get(user_phone)
        if user_data:
            return user_data["wallet_address"]
        return None

    async def check_real_balance(self, wallet_address: str, token_symbol: str = "ETH") -> str:
        """Check real token balance with conversational response"""
        try:
            if token_symbol.upper() == "ETH":
                balance = await self.data_service.get_eth_balance(wallet_address)
                price_data = await self.data_service.get_token_price("ETH")
                
                if balance == 0:
                    return f"""I checked your wallet and it looks like you don't have any ETH right now! 😅

Your wallet: {wallet_address[:10]}...{wallet_address[-6:]}

But hey, no worries! Everyone starts somewhere. You can get some ETH from exchanges like Coinbase, Binance, or use a faucet if you're on a testnet.

{f"Current ETH price is ${price_data['price']:,.2f} by the way! {'📈' if price_data['change_24h'] > 0 else '📉'} ({price_data['change_24h']:+.2f}% today)" if price_data else ""}

Need help getting started with crypto? Just ask! 😊"""

                if price_data:
                    usd_value = balance * price_data['price']
                    change_emoji = "📈" if price_data['change_24h'] > 0 else "📉"
                    
                    return f"""Nice! Here's what you've got in your wallet: 💰

🔸 **ETH Balance:** {balance:.6f} ETH
🔸 **USD Value:** ${usd_value:,.2f}
{change_emoji} **ETH Price:** ${price_data['price']:,.2f} ({price_data['change_24h']:+.2f}% today)

Your wallet: {wallet_address[:10]}...{wallet_address[-6:]}

{'Looking good!' if usd_value > 100 else 'Every satoshi counts!'} Want me to check any other tokens? 😊"""
                else:
                    return f"""Here's your ETH balance: 💰

🔸 **ETH Balance:** {balance:.6f} ETH

Your wallet: {wallet_address[:10]}...{wallet_address[-6:]}

I couldn't get the current price right now, but your balance is looking good! 😊"""

            else:
                balance = await self.data_service.get_token_balance(wallet_address, token_symbol.upper())
                
                if balance == 0:
                    return f"""I don't see any {token_symbol.upper()} in your wallet right now! 🤷‍♂️

Your wallet: {wallet_address[:10]}...{wallet_address[-6:]}

You might want to check if:
• You have the token on a different network
• The token symbol is correct
• You actually own some {token_symbol.upper()} 😅

Want me to check ETH or another token instead?"""

                return f"""Here's your {token_symbol.upper()} balance: 💰

🔸 **{token_symbol.upper()} Balance:** {balance:.6f} {token_symbol.upper()}

Your wallet: {wallet_address[:10]}...{wallet_address[-6:]}

Looking good! Want me to check the current price or other tokens? 😊"""
                
        except Exception as e:
            logger.error(f"Error checking balance: {str(e)}")
            return "Hmm, I'm having trouble connecting to the blockchain right now. Could you try again in a moment? 😅"

    async def get_real_price(self, token_symbol: str = "ETH") -> str:
        """Get real price with conversational response"""
        try:
            price_data = await self.data_service.get_token_price(token_symbol)
            
            if not price_data:
                return f"""Hmm, I couldn't find price data for {token_symbol.upper()} right now! 🤔

Maybe check the symbol? I can definitely help with:
• ETH (Ethereum)
• BTC (Bitcoin)  
• USDC, USDT, DAI (stablecoins)

What token were you looking for? 😊"""

            price = price_data['price']
            change_24h = price_data['change_24h']
            change_emoji = "📈" if change_24h > 0 else "📉"
            
            if price > 1000:
                price_str = f"${price:,.2f}"
            else:
                price_str = f"${price:.4f}"

            enthusiasm = ""
            if abs(change_24h) > 5:
                enthusiasm = " Wow, quite a move!" if change_24h > 5 else " That's a big dip!"
            elif abs(change_24h) > 2:
                enthusiasm = " Nice movement!" if change_24h > 2 else " Bit of a slide there."

            commentary = self._get_price_commentary(token_symbol.upper(), price, change_24h)

            return f"""Here's the latest on {token_symbol.upper()}! 📊

💰 **Current Price:** {price_str}
{change_emoji} **24h Change:** {change_24h:+.2f}%{enthusiasm}

{commentary}

Want me to check any other tokens or help with something else? 😊"""
                
        except Exception as e:
            logger.error(f"Error getting price: {str(e)}")
            return "I'm having trouble getting price data right now. The crypto markets never sleep, but sometimes the APIs need a coffee break! ☕ Try again in a moment?"

    def _get_price_commentary(self, symbol: str, price: float, change: float) -> str:
        """Add some personality to price responses"""
        if symbol == "ETH":
            if price > 3000:
                return "ETH is looking strong! 💪"
            elif price > 2000:
                return "ETH holding steady in good territory! 👍"
            else:
                return "Might be a good time to stack some ETH! 🤔"
        elif symbol == "BTC":
            if price > 60000:
                return "Bitcoin to the moon! 🚀"
            elif price > 40000:
                return "BTC looking solid! 💎"
            else:
                return "Bitcoin having a moment... HODL! 💪"
        elif symbol in ["USDC", "USDT", "DAI"]:
            return "Stable as always! 😌"
        else:
            return "Keep an eye on those charts! 📈"

    async def get_real_gas_info(self) -> str:
        """Get real gas information with conversational response"""
        try:
            gas_data = await self.data_service.get_gas_price()
            
            return f"""Here's what gas is looking like right now! ⛽

🔸 **Safe:** {gas_data['safe']} Gwei (~$2.50)
🔸 **Standard:** {gas_data['standard']} Gwei (~$4.20)  
🔸 **Fast:** {gas_data['fast']} Gwei (~$5.80)

💡 **Pro tips:**
• Use "Safe" for non-urgent transactions
• Weekends are usually cheaper! 📅
• Try Layer 2 solutions like Polygon for way cheaper fees 🌉

Gas prices update constantly, so if it's expensive now, maybe grab a coffee and check back later! ☕😊"""
                
        except Exception as e:
            logger.error(f"Error getting gas info: {str(e)}")
            return "I'm having trouble checking gas prices right now. But between you and me, it's probably expensive! 😅 Maybe try Layer 2 solutions?"

    def get_defi_education(self, query: str) -> str:
        """Get DeFi education with conversational responses"""
        query_lower = query.lower()
        
        if any(word in query_lower for word in ['blockchain', 'block chain', 'what is blockchain']):
            return """Oh, blockchain! The foundation of everything we're talking about! 🧱⛓️

Think of blockchain like a **digital ledger** that everyone can see, but no one can cheat on! Here's the simple version:

**Imagine a notebook that:**
• Everyone has an identical copy 📚
• Every transaction gets written down
• Once written, you can't erase it
• Everyone has to agree before adding new pages

**Why it's revolutionary:**
• **No central authority** - no bank needed! 🏦❌
• **Transparent** - you can verify everything 👀
• **Secure** - super hard to hack when decentralized 🔒
• **Global** - works the same everywhere 🌍

Each "block" contains transactions, and they're all linked together in a "chain" - hence blockchain! When someone tries to change something, everyone else's copy would show it's wrong.

That's how we can have digital money (like Bitcoin) without needing a bank to keep track! Pretty cool, right? 😎

Want me to explain Bitcoin, Ethereum, or dive deeper into how mining works?"""

        elif any(word in query_lower for word in ['defi', 'decentralized finance', 'tell me about defi', 'more about defi']):
            return """DeFi - Decentralized Finance! This is where things get REALLY exciting! 🚀

Imagine if you could:
• Lend money and earn interest 📈
• Borrow without banks 🏦❌
• Trade stocks 24/7 globally 🌍
• Earn yield on your savings 💰
• All without asking permission from anyone! 🙅‍♂️

That's DeFi! It's like rebuilding the entire financial system, but on blockchain, so it's:
• **Open** - anyone can use it
• **Transparent** - all transactions visible
• **Permissionless** - no gatekeepers
• **Composable** - protocols work together like Lego blocks! 🧱

**Popular DeFi things:**
• **Uniswap** - trade tokens instantly 🦄
• **Aave** - lend & borrow crypto 💸
• **Compound** - earn interest on deposits 🏛️
• **MakerDAO** - create stable coins 🪙

The crazy part? Most of this stuff didn't exist 5 years ago! We're literally watching the future of finance being built in real-time! 🏗️

What aspect interests you most? Trading? Lending? Yield farming? I could talk about this all day! 😄"""

        elif any(word in query_lower for word in ['uniswap', 'dex', 'swap', 'trade']):
            return """Oh, you're curious about Uniswap and DEXs! Cool stuff! 🦄

So imagine you want to trade tokens, but instead of going through a traditional exchange, you trade directly from your wallet. That's what Uniswap does!

Here's the magic: Instead of order books, it uses "liquidity pools" - basically big pots of tokens that people contribute to. When you swap, you're trading against these pools!

**Why it's awesome:**
• No sign-ups or KYC 🙅‍♂️
• You control your funds the whole time 🔐
• Works 24/7 globally 🌍
• Tons of tokens available 🪙

**Just watch out for:**
• Gas fees (especially when Ethereum is busy!) ⛽
• Slippage on big trades 📉
• Always double-check token contracts! ⚠️

Want me to explain liquidity pools or something else? I love talking about this stuff! 😄"""

        elif any(word in query_lower for word in ['yield', 'farm', 'stake', 'earn']):
            return """Yield farming and staking - now we're talking about making your crypto work for you! 💰

**Staking** is like putting your money in a savings account, but for crypto. You lock up your tokens to help secure a network and earn rewards. Pretty straightforward!

**Yield farming** is more like... advanced treasure hunting! 🏴‍☠️ You provide liquidity to different protocols, earn fees, get reward tokens, maybe stake those too... it can get wild!

**The good news:** You can earn way more than traditional savings (we're talking 5-50%+ APY sometimes!)

**The reality check:** 
• Higher rewards = higher risks 📈📉
• Smart contract bugs happen 🐛  
• "Impermanent loss" is a real thing with liquidity providing
• Some projects... well, let's just say not all treasure is real 💎

Start small, learn as you go, and never invest more than you can afford to lose. Sound good? 😊

Want me to explain any of these concepts deeper?"""

        elif any(word in query_lower for word in ['aave', 'compound', 'lend', 'borrow']):
            return """Lending and borrowing in DeFi - it's like traditional banking, but with superpowers! 🦸‍♂️

**How it works:**
• You deposit crypto (like ETH) as collateral
• You can borrow other tokens (like USDC) against it
• Or just lend and earn interest on your deposits!

**Platforms like Aave and Compound** make this super smooth. They're like decentralized banks that run on smart contracts.

**Cool things you can do:**
• Earn interest on crypto you're just holding anyway 💰
• Borrow stablecoins without selling your ETH 🤝
• Leverage your positions (but be careful!) 📊

**The catch:** If your collateral value drops too much, you get liquidated! It's like the bank taking your house, but faster and automated 🏠💨

**Pro tip:** Start with over-collateralization (like putting up $150 of ETH to borrow $100 of stablecoins). Safety first! 🛡️

Questions about any of this? I can break it down further! 😊"""

        else:
            return """Hey there! I love chatting about DeFi and crypto! 😄

I can help explain tons of stuff like:
🦄 **Uniswap & DEXs** - Trading without intermediaries
🌾 **Yield Farming** - Making your crypto earn more crypto  
🏦 **Lending/Borrowing** - DeFi banking superpowers
⛽ **Gas Fees** - Why transactions cost money and how to save
🔗 **Different Blockchains** - Ethereum, Polygon, and more!
💎 **Investment Strategies** - From conservative to degen 😅

I'm also here to help with:
• Understanding your portfolio 📊
• Explaining confusing crypto terms 🤓
• Sharing market insights 📈
• Just chatting about this wild world! 🌍

What's on your mind? I promise to keep it fun and easy to understand! 😊"""

    async def process_whatsapp_message(self, user_phone: str, message: str) -> str:
        """Process WhatsApp message using Spoon AI with specific crypto handling"""
        try:
            logger.info(f"Processing message from {user_phone}: {message}")
            
            # Check for wallet address first
            if self.is_wallet_address(message):
                response = self.save_user_wallet(user_phone, message.strip())
                logger.info(f"Wallet address response generated")
                return response
            
            # Get user's wallet if they have one saved
            user_wallet = self.get_user_wallet(user_phone)
            logger.info(f"User wallet: {user_wallet[:10] + '...' if user_wallet else 'None'}")
            
            # Check for specific crypto actions we can handle directly
            message_lower = message.lower().strip()
            
            # Handle price requests
            token = self.extract_token_symbol(message_lower)
            if token and any(word in message_lower for word in ['price', 'cost', 'worth', 'value', 'trading', 'market']):
                response = await self.get_real_price(token)
                logger.info(f"Price check response generated for {token}")
                return response
            
            # Handle gas fee requests
            if any(word in message_lower for word in ['gas fee', 'gas fees', 'gas price', 'gwei', 'network fee']):
                response = await self.get_real_gas_info()
                logger.info(f"Gas fees response generated")
                return response
            
            # Handle balance requests
            if user_wallet and any(word in message_lower for word in ['balance', 'check balance', 'my balance', 'wallet balance']):
                token_for_balance = token if token else 'ETH'
                response = await self.check_real_balance(user_wallet, token_for_balance)
                logger.info(f"Balance check response generated")
                return response
            elif any(word in message_lower for word in ['balance', 'check balance', 'my balance', 'wallet balance']):
                response = """I don't have your wallet address yet! 💳 

Send me your Ethereum wallet address (starts with 0x) and I'll check your real balance from the blockchain! 

I'll keep it safe and secure - just between us! 🔒�"""
                logger.info(f"No wallet response generated")
                return response
            
            # For all other messages, use Spoon AI's natural conversation with enhanced context
            context = self.build_crypto_context(user_wallet, {'token': token} if token else {}, message)
            logger.info(f"Using Spoon AI for conversation, context: {context[:100]}...")
            
            # Use OpenRouter as LLM backend through Spoon AI
            response = await self.get_ai_response(message, context)
            logger.info(f"AI response generated: {response[:50]}...")
            return response
                
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            return "Oops! Something went wrong on my end. Could you try that again? I promise I'm usually more reliable than this! 😅"

    def build_crypto_context(self, user_wallet: str, data: dict, original_message: str) -> str:
        """Build crypto context for OpenRouter with token and chain information"""
        context_parts = []
        
        # User wallet status
        if user_wallet:
            context_parts.append(f"User has wallet: {user_wallet[:10]}...{user_wallet[-6:]}")
        else:
            context_parts.append("User has no wallet saved")
        
        # Token context if detected
        if 'token' in data:
            token = data['token']
            context_parts.append(f"User mentioned token: {token}")
            
            # Special handling for Neo ecosystem
            if token.upper() in ['NEO', 'GAS', 'NNEO', 'FLM', 'BURGER']:
                context_parts.append("This is a Neo blockchain token - provide Neo-specific insights")
        
        # Add capabilities context
        context_parts.append("You can provide real-time crypto prices, gas fees, balance checks, and DeFi education")
        context_parts.append("You specialize in Neo blockchain and support ALL major cryptocurrencies")
        context_parts.append("If user asks about prices, you can get real data - just mention the token symbol clearly")
        
        return " | ".join(context_parts)

async def create_neolink_agent():
    """Create and initialize the NeoLink Spoon AI agent"""
    try:
        agent = NeoLinkSpoonAgent()
        logger.info("NeoLink Spoon AI agent created successfully")
        return agent
    except Exception as e:
        logger.error(f"Error creating Spoon AI agent: {str(e)}")
        raise

# Test function
async def test_neolink_agent():
    """Test the NeoLink agent functionality with various queries"""
    print("🚀 Testing NeoLink DeFi WhatsApp Agent with Real Data...")
    
    agent = await create_neolink_agent()
    
    # Test various intents with real API calls
    test_cases = [
        ("test_user", "0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8e8"),  # Real wallet
        ("test_user", "what's my ETH balance?"),  # Real balance check
        ("test_user", "how much is ethereum worth today?"),  # Real price
        ("test_user", "what's bitcoin doing?"),  # BTC price
        ("test_user", "check current gas fees"),  # Real gas data
        ("test_user", "tell me about uniswap"),  # DeFi education
        ("new_user", "hey there! I'm new to crypto"),  # New user greeting
        ("test_user", "thanks for all the help!"),  # General conversation
    ]
    
    for user_phone, message in test_cases:
        print(f"\n{'='*70}")
        print(f"💬 User: {message}")
        print(f"{'='*70}")
        response = await agent.process_whatsapp_message(user_phone, message)
        print(f"🤖 Agent: {response}")
        print("\n⏱️  Waiting 3 seconds for API rate limits...\n")
        await asyncio.sleep(3)  # Be respectful to APIs

if __name__ == "__main__":
    asyncio.run(test_neolink_agent())
