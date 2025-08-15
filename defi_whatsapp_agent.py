#!/usr/bin/env python3
"""
DeFi WhatsApp Agent using Spoon AI SDK
Based on Spoon Core documentation and cookbook examples
"""

import os
import sys
import asyncio
import logging
import re
from typing import Dict, Any, Optional, List
from datetime import datetime
from pydantic import Field

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Import SpoonAI components
from spoon_ai.agents.toolcall import ToolCallAgent
from spoon_ai.chat import ChatBot
from spoon_ai.tools import ToolManager, Terminate
from spoon_ai.tools.base import BaseTool

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Simple in-memory storage for user wallets
USER_WALLETS = {}

class WalletManagerTool(BaseTool):
    """Tool for managing user wallet addresses"""
    name: str = "wallet_manager"
    description: str = "Save and retrieve user wallet addresses for DeFi operations"
    parameters: dict = {
        "type": "object",
        "properties": {
            "operation": {
                "type": "string",
                "description": "Operation to perform (save, get)",
                "enum": ["save", "get"]
            },
            "user_phone": {
                "type": "string",
                "description": "User's phone number identifier"
            },
            "wallet_address": {
                "type": "string",
                "description": "Ethereum wallet address (for save operation)"
            }
        },
        "required": ["operation", "user_phone"]
    }

    async def execute(self, operation: str, user_phone: str, wallet_address: Optional[str] = None) -> str:
        """Execute wallet management operations"""
        try:
            if operation == "save":
                if not wallet_address:
                    return "Error: wallet_address is required for save operation"
                
                # Basic validation
                if not wallet_address.startswith('0x') or len(wallet_address) != 42:
                    return "❌ Invalid wallet address format. Please provide a valid Ethereum address starting with 0x"
                
                USER_WALLETS[user_phone] = {
                    "wallet_address": wallet_address,
                    "created_at": str(datetime.now())
                }
                
                return f"✅ Wallet address saved successfully! You can now check balances and prepare transfers."
                
            elif operation == "get":
                user_data = USER_WALLETS.get(user_phone)
                if user_data:
                    return f"User wallet: {user_data['wallet_address']}"
                else:
                    return "No wallet address found for this user"
                    
            else:
                return f"Error: Unsupported operation '{operation}'"
                
        except Exception as e:
            logger.error(f"Error in wallet manager: {str(e)}")
            return f"Error: {str(e)}"

class BalanceCheckerTool(BaseTool):
    """Tool for checking token balances"""
    name: str = "balance_checker"
    description: str = "Check ETH and ERC-20 token balances for wallet addresses"
    parameters: dict = {
        "type": "object",
        "properties": {
            "wallet_address": {
                "type": "string",
                "description": "Ethereum wallet address to check balance for"
            },
            "token_symbol": {
                "type": "string",
                "description": "Token symbol (ETH, USDC, USDT, DAI)",
                "enum": ["ETH", "USDC", "USDT", "DAI"]
            }
        },
        "required": ["wallet_address", "token_symbol"]
    }

    async def execute(self, wallet_address: str, token_symbol: str = "ETH") -> str:
        """Check token balance"""
        try:
            # Basic validation
            if not wallet_address.startswith('0x') or len(wallet_address) != 42:
                return "❌ Invalid wallet address format"
            
            # For demo purposes, return mock data
            # In production, this would use Web3 to check actual balances
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

class DeFiWhatsAppAgent(ToolCallAgent):
    """DeFi WhatsApp Agent using Spoon AI SDK"""
    
    name: str = "defi_whatsapp_agent"
    description: str = "A DeFi assistant for WhatsApp that helps with wallet management and balance checks"
    
    system_prompt: str = """You are a helpful DeFi assistant for WhatsApp users. You can:

1. Save user wallet addresses when they send you an Ethereum address (0x...)
2. Check token balances (ETH, USDC, USDT, DAI) for saved wallets
3. Provide general DeFi information and guidance
4. Help users understand blockchain and cryptocurrency concepts

When users send you an Ethereum address, use the wallet_manager tool to save it.
When users ask about balances, use the balance_checker tool.
Keep responses concise and friendly for WhatsApp messaging.
Use emojis to make responses engaging.
Always prioritize security and never ask for private keys.

Use the available tools to answer queries. Follow this process:
1. Understand what the user wants
2. Use the appropriate tool if needed
3. Provide a helpful response
4. Use 'terminate' when the task is complete
"""
    
    max_steps: int = 5
    tool_choice: str = "auto"
    
    # Available tools
    available_tools: ToolManager = Field(
        default_factory=lambda: ToolManager([
            WalletManagerTool(),
            BalanceCheckerTool(),
            Terminate()
        ])
    )

    def is_wallet_address(self, message: str) -> bool:
        """Check if message contains an Ethereum wallet address"""
        eth_address_pattern = r'^0x[a-fA-F0-9]{40}$'
        return bool(re.match(eth_address_pattern, message.strip()))

    async def process_whatsapp_message(self, user_phone: str, message: str) -> str:
        """Process WhatsApp message and return response"""
        try:
            # Check if user is sending a wallet address
            if self.is_wallet_address(message):
                # Use the agent's run method to save the wallet
                query = f"Save wallet address {message.strip()} for user {user_phone}"
                response = await self.run(query)
                return response
            
            # For other messages, use the agent's run method
            # Add user context to the message
            enhanced_message = f"User {user_phone} says: {message}"
            response = await self.run(enhanced_message)
            return response
                
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            return "❌ Sorry, I encountered an error. Please try again or type 'help' for assistance."

async def create_agent():
    """Create and initialize the DeFi WhatsApp agent"""
    try:
        # Create ChatBot with OpenRouter configuration
        chatbot = ChatBot(
            model_name="anthropic/claude-3-haiku",
            llm_provider="openai",
            base_url="https://openrouter.ai/api/v1"
        )
        
        # Create agent with the chatbot
        agent = DeFiWhatsAppAgent(llm=chatbot)
        return agent
        
    except Exception as e:
        logger.error(f"Error creating agent: {str(e)}")
        # Fallback to default chatbot
        agent = DeFiWhatsAppAgent()
        return agent

# Test function
async def test_agent():
    """Test the agent functionality"""
    print("🚀 Testing DeFi WhatsApp Agent...")
    
    agent = await create_agent()
    
    # Test wallet saving
    test_wallet = "0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8e8"
    response1 = await agent.process_whatsapp_message("test_user", test_wallet)
    print(f"Wallet save response: {response1}")
    
    # Test message processing
    response2 = await agent.process_whatsapp_message("test_user", "check my ETH balance")
    print(f"Balance query response: {response2}")
    
    # Test general query
    response3 = await agent.process_whatsapp_message("test_user", "What is DeFi?")
    print(f"General query response: {response3}")
    
    # Test help
    response4 = await agent.process_whatsapp_message("new_user", "help")
    print(f"Help response: {response4}")

if __name__ == "__main__":
    asyncio.run(test_agent())