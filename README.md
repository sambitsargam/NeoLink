# DeFi WhatsApp Agent

A Python-based DeFi agent built with **Spoon AI SDK** that integrates with WhatsApp via Twilio and uses OpenRouter for AI-powered responses.

## Features

- 🥄 **Spoon AI SDK** - Professional agent framework with built-in tools
- 📱 **WhatsApp Integration** - Twilio webhook for messaging
- 🔗 **Ethereum Blockchain** - Balance checks and transfer preparation  
- 🧠 **AI-Powered** - OpenRouter integration via OpenAI compatibility
- 💾 **Memory** - User wallet storage
- 🛡️ **Security First** - Read-only operations, no private key handling

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure environment variables:**
   Update `.env` with your API keys:
   - `TWILIO_ACCOUNT_SID` and `TWILIO_AUTH_TOKEN`
   - `OPENAI_API_KEY` (set to your OpenRouter API key)
   - `RPC_URL` (Ethereum RPC endpoint)
   - `CHAINBASE_API_KEY` (for blockchain data)
   - `PRIVATE_KEY` (your wallet private key for blockchain operations)
   - `CHAIN_ID` (blockchain chain ID, default: 1 for Ethereum mainnet)

3. **Run the application:**
   ```bash
   python run.py
   ```

4. **Test the agent:**
   ```bash
   python defi_whatsapp_agent.py
   ```

5. **Configure Twilio webhook:**
   Set your Twilio WhatsApp webhook URL to: `https://your-domain.com/webhook`

## Usage

Send WhatsApp messages to your Twilio number:

- **Setup:** Send your wallet address (0x123...)
- **Check balance:** "What's my ETH balance?" or "check my balance"
- **DeFi questions:** "What is DeFi?" or "How does Uniswap work?"
- **Help:** "help" or "hi"

## Architecture

- `app.py` - Flask web server and Twilio webhook handler
- `defi_whatsapp_agent.py` - Main Spoon AI agent implementation
- `config.json` - Spoon AI agent configuration
- `.env` - Environment variables

## Spoon AI SDK Integration

This project uses Spoon AI SDK's:
- **SpoonReactMCP** - Advanced agent with MCP protocol support
- **Built-in Tools** - Crypto tools for price data and balance checks
- **ChatBot** - OpenRouter integration via OpenAI compatibility
- **ToolManager** - Automatic tool loading and management

## Agent Capabilities

The agent can:
- **Save Wallets** - Store user Ethereum wallet addresses
- **Check Balances** - ETH and ERC-20 token balances via built-in tools
- **Answer Questions** - General DeFi knowledge via AI
- **Prepare Transfers** - Generate transfer details (no execution)
- **Context Awareness** - Remember user wallets across conversations

## Security Notes

- ⚠️ **Private Key Required** - Needed for blockchain operations (balance checks, etc.)
- 🔐 **Secure Storage** - Store private key securely, never commit to version control
- ✅ **Read-only Operations** - Agent only reads blockchain data, doesn't execute transactions
- ✅ **Transfer preparation only** - No actual transaction execution
- ✅ **User wallet addresses** stored in memory only
- ✅ **Professional Framework** - Built on Spoon AI SDK
- 🛡️ **Best Practices** - Use dedicated wallet for testing, rotate keys regularly

## Configuration

The agent is configured via `config.json` using Spoon AI SDK's unified configuration system:
- **OpenRouter Integration** - Via OpenAI compatibility layer
- **Built-in Tools** - Crypto price and balance tools
- **Agent Settings** - Max steps, tool choice, etc.
- **Environment Variables** - API keys and RPC endpoints

## Supported Tokens

- **ETH** (native Ethereum)
- **USDC, USDT, DAI** (ERC-20 tokens via built-in tools)

Additional tools can be added via the Spoon AI SDK's built-in tool system or MCP protocol.
## Im
portant Security Setup

### Private Key Configuration

The Spoon AI SDK requires a private key for blockchain operations. Follow these security practices:

1. **Create a dedicated wallet** for this agent (don't use your main wallet)
2. **Fund it minimally** - only enough ETH for gas if needed
3. **Never commit private keys** to version control
4. **Use environment variables** only

```bash
# Generate a new wallet for testing
# You can use MetaMask, MyEtherWallet, or any wallet generator
# Copy the private key (without 0x prefix) to your .env file

PRIVATE_KEY=your_64_character_private_key_here
```

### Environment Variables Priority

The Spoon AI SDK uses this priority order:
1. Tool-level `env` configuration (in config.json)
2. System environment variables (from .env file)
3. Default values

### Blockchain Configuration

- **Mainnet**: `CHAIN_ID=1`, `RPC_URL=https://eth.llamarpc.com`
- **Sepolia Testnet**: `CHAIN_ID=11155111`, `RPC_URL=https://sepolia.infura.io/v3/your_key`
- **Local**: `CHAIN_ID=1337`, `RPC_URL=http://localhost:8545`