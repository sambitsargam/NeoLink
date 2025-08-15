#!/usr/bin/env python3
"""
DeFi WhatsApp Agent using Spoon AI SDK
"ased on Spoon Core documentation: https://github.com/XSpoonAi/spoon-core
"""

import os
import sys
import json
import re
from typing import Dict, Any, Optional
from datetime import datetime
from web3 import Web3
import logging

# Add spoon to path if needed
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

logger = logging.getLogger(__name__)

# Initialize Web3 connection
rpc_url = os.getenv('ETHEREUM_RPC_URL', 'https://mainnet.infura.io/v3/your_key')
w3 = Web3(Web3.HTTPProvider(rpc_url))

# Common token contracts (mainnet)
TOKEN_CONTRACTS = {
    'USDC': '0xA0b86a33E6441b8C4505E2c52C6b6046d4b0b8e8',
    'USDT': '0xdAC17F958D2ee523a2206206994597C13D831ec7',
    'DAI': '0x6B175474E89094C44Da98b954EedeAC495271d0F'
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

class DeFiSpoonAgent:
    """DeFi agent using Spoon Core framework"""
    
    def __init__(self):
        """Initialize the agent"""
        self.openrouter_api_key = os.getenv('OPENROUTER_API_KEY')
        if not self.openrouter_api_key:
            raise ValueError("OPENROUTER_API_KEY environment variable is required")
    
    def process_message(self, user_phone: str, message: str) -> str:
        """Process WhatsApp message and return response"""
        try:
            # Check if user is sending a wallet address
            if self._is_wallet_address(message):
                return self._save_user_wallet(user_phone, message.strip())
            
            # Get user's wallet if they have one saved
            user_wallet = self._get_user_wallet(user_phone)
            
            # Parse the message to understand intent
            intent = self._parse_message_intent(message)
            
            # Handle different intents
            if intent['action'] == 'balance':
                if not user_wallet:
                    return "I don't have your wallet address. Please send me your Ethereum wallet address (starts with 0x) to get started."
                return self._get_token_balance(user_wallet, intent.get('token', 'ETH'))
            
            elif intent['action'] == 'transfer':
                if not user_wallet:
                    return "I don't have your wallet address. Please send me your Ethereum wallet address (starts with 0x) to get started."
                return self._prepare_transfer(user_wallet, intent)
            
            elif intent['action'] == 'gas':
                return self._get_gas_price()
            
            elif intent['action'] == 'help':
                return self._get_help_message()
            
            else:
                # Use OpenRouter for general queries
                return self._handle_general_query(message, user_wallet)
                
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            return "Sorry, I encountered an error. Please try again or type 'help' for assistance."
    
    def _is_wallet_address(self, message: str) -> bool:
        """Check if message contains an Ethereum wallet address"""
        eth_address_pattern = r'^0x[a-fA-F0-9]{40}$'
        return bool(re.match(eth_address_pattern, message.strip()))
    
    def _parse_message_intent(self, message: str) -> Dict[str, Any]:
        """Parse message to understand user intent"""
        message_lower = message.lower()
        
        # Balance check patterns
        if any(word in message_lower for word in ['balance', 'check', 'how much']):
            # Extract token symbol if mentioned
            token = 'ETH'  # default
            for token_symbol in ['eth', 'usdc', 'usdt', 'dai']:
                if token_symbol in message_lower:
                    token = token_symbol.upper()
                    break
            return {'action': 'balance', 'token': token}
        
        # Transfer patterns
        elif any(word in message_lower for word in ['send', 'transfer', 'pay']):
            # Try to extract amount and recipient
            amount_match = re.search(r'(\d+\.?\d*)', message)
            address_match = re.search(r'(0x[a-fA-F0-9]{40})', message)
            
            return {
                'action': 'transfer',
                'amount': amount_match.group(1) if amount_match else None,
                'recipient': address_match.group(1) if address_match else None,
                'token': 'ETH'  # default
            }
        
        # Gas price
        elif any(word in message_lower for word in ['gas', 'fee']):
            return {'action': 'gas'}
        
        # Help
        elif any(word in message_lower for word in ['help', 'start', 'hello', 'hi']):
            return {'action': 'help'}
        
        else:
            return {'action': 'general'}
    
    def _save_user_wallet(self, user_phone: str, wallet_address: str) -> str:
        """Save user wallet address"""
        try:
            if not w3.is_address(wallet_address):
                return "Invalid wallet address format. Please provide a valid Ethereum address starting with 0x"
            
            wallet_address = w3.to_checksum_address(wallet_address)
            USER_WALLETS[user_phone] = {
                "wallet_address": wallet_address,
                "created_at": str(datetime.now())
            }
            
            return f"✅ Wallet address saved successfully!\n\nYou can now:\n• Check balances: 'check ETH balance'\n• Prepare transfers: 'send 0.1 ETH to 0x123...'\n• Get gas prices: 'gas price'"
            
        except Exception as e:
            logger.error(f"Error saving wallet: {str(e)}")
            return f"Error saving wallet address: {str(e)}"
    
    def _get_user_wallet(self, user_phone: str) -> Optional[str]:
        """Get user's saved wallet address"""
        user_data = USER_WALLETS.get(user_phone)
        if user_data:
            return user_data["wallet_address"]
        return None
    
    def _get_token_balance(self, wallet_address: str, token_symbol: str = "ETH") -> str:
        """Get token balance for a wallet address"""
        try:
            wallet_address = w3.to_checksum_address(wallet_address)
            
            if token_symbol.upper() == 'ETH':
                # Get ETH balance
                balance_wei = w3.eth.get_balance(wallet_address)
                balance_eth = w3.from_wei(balance_wei, 'ether')
                return f"💰 Your {token_symbol} balance: {balance_eth:.6f} ETH"
            
            else:
                # Get ERC-20 token balance
                token_address = TOKEN_CONTRACTS.get(token_symbol.upper())
                if not token_address:
                    return f"Token {token_symbol} not supported. Supported tokens: ETH, USDC, USDT, DAI"
                
                contract = w3.eth.contract(
                    address=w3.to_checksum_address(token_address),
                    abi=ERC20_ABI
                )
                
                balance = contract.functions.balanceOf(wallet_address).call()
                decimals = contract.functions.decimals().call()
                
                # Convert to human readable format
                balance_formatted = balance / (10 ** decimals)
                return f"💰 Your {token_symbol.upper()} balance: {balance_formatted:.6f} {token_symbol.upper()}"
                
        except Exception as e:
            logger.error(f"Error getting balance: {str(e)}")
            return f"Error retrieving {token_symbol} balance. Please try again later."
    
    def _prepare_transfer(self, from_address: str, intent: Dict[str, Any]) -> str:
        """Prepare transfer transaction details"""
        try:
            amount = intent.get('amount')
            recipient = intent.get('recipient')
            token_symbol = intent.get('token', 'ETH')
            
            if not amount or not recipient:
                return "To prepare a transfer, please specify:\n• Amount (e.g., 0.1)\n• Recipient address (0x123...)\n\nExample: 'Send 0.1 ETH to 0x123...'"
            
            if not w3.is_address(recipient):
                return "Invalid recipient address format. Please provide a valid Ethereum address starting with 0x"
            
            from_address = w3.to_checksum_address(from_address)
            recipient = w3.to_checksum_address(recipient)
            
            # Get current gas price
            gas_price = w3.eth.gas_price
            gas_price_gwei = w3.from_wei(gas_price, 'gwei')
            
            transfer_summary = f"""📤 Transfer Prepared:

• From: {from_address[:10]}...{from_address[-4:]}
• To: {recipient[:10]}...{recipient[-4:]}
• Amount: {amount} {token_symbol.upper()}
• Gas Price: {gas_price_gwei:.2f} Gwei

⚠️ This is preparation only. Please execute the transfer in your wallet app for security."""
            
            return transfer_summary
            
        except Exception as e:
            logger.error(f"Error preparing transfer: {str(e)}")
            return f"Error preparing transfer: {str(e)}"
    
    def _get_gas_price(self) -> str:
        """Get current Ethereum gas price"""
        try:
            gas_price = w3.eth.gas_price
            gas_price_gwei = w3.from_wei(gas_price, 'gwei')
            return f"⛽ Current gas price: {gas_price_gwei:.2f} Gwei"
        except Exception as e:
            logger.error(f"Error getting gas price: {str(e)}")
            return "Unable to fetch current gas price"
    
    def _get_help_message(self) -> str:
        """Get help message"""
        return """🤖 DeFi Assistant Help

Commands I understand:
• Send your wallet address (0x123...) to get started
• "check ETH balance" - Check token balances
• "send 0.1 ETH to 0x456..." - Prepare transfers
• "gas price" - Current gas prices

Supported tokens: ETH, USDC, USDT, DAI

What would you like to do?"""
    
    def _handle_general_query(self, message: str, user_wallet: Optional[str]) -> str:
        """Handle general queries using OpenRouter"""
        try:
            import requests
            
            headers = {
                "Authorization": f"Bearer {self.openrouter_api_key}",
                "Content-Type": "application/json"
            }
            
            context = ""
            if user_wallet:
                context = f"User has wallet: {user_wallet[:10]}...{user_wallet[-4:]}\n"
            
            prompt = f"""You are a helpful DeFi assistant for WhatsApp. {context}

User message: "{message}"

You can help with:
- Token balance checks (ETH, USDC, USDT, DAI)
- Transfer preparation (security-focused, no execution)
- Gas price information
- General DeFi questions

Keep responses concise and friendly for WhatsApp. If the user needs specific actions, guide them to use commands like "check ETH balance" or "send 0.1 ETH to 0x123..."."""
            
            payload = {
                "model": "anthropic/claude-3-haiku",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 200
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
                return "I'm having trouble processing that. Try 'help' to see what I can do!"
                
        except Exception as e:
            logger.error(f"Error with general query: {str(e)}")
            return "I'm not sure how to help with that. Type 'help' to see available commands!"