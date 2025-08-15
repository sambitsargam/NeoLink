# NeoLink - DeFi WhatsApp Agent

A conversational WhatsApp bot powered by **Spoon AI** that provides real-time cryptocurrency data and DeFi education through natural AI conversations. Specialized in Neo blockchain ecosystem with comprehensive multi-chain support.

## 🚀 Features

🤖 **Spoon AI Powered**: Built with SpoonReactMCP for intelligent conversation handling  
📊 **Real-Time Data**: Live cryptocurrency prices from CoinGecko API  
⛽ **Gas Tracker**: Real-time Ethereum gas fees monitoring  
🔗 **Multi-Chain Support**: Bitcoin, Ethereum, Neo, Solana, and 100+ cryptocurrencies  
💰 **Neo Ecosystem Focus**: Specialized support for NEO, GAS, and Flamingo (FLM) tokens  
📱 **WhatsApp Native**: Seamless integration with Twilio WhatsApp Business API  
🎓 **DeFi Education**: Educational content and explanations for DeFi concepts  
💾 **Smart Memory**: User wallet storage and context awareness  
🛡️ **Security First**: Read-only operations, no private key handling  

## 🧠 Spoon AI Integration

NeoLink leverages the **Spoon AI SDK** for intelligent conversation handling:

- **SpoonReactMCP**: Advanced agent class with natural language processing
- **OpenRouter Backend**: Uses Claude-3-Haiku model for conversational responses
- **Intelligent Routing**: Automatically detects crypto-specific queries vs general conversation
- **Context Awareness**: Maintains user context across conversations
- **Multi-Modal Processing**: Handles price requests, balance checks, and educational queries

### How Spoon AI Works in NeoLink

1. **Message Processing**: SpoonReactMCP analyzes incoming WhatsApp messages
2. **Intent Detection**: Smart routing between crypto actions and general conversation
3. **Data Integration**: Real-time API calls for live cryptocurrency data
4. **Response Generation**: AI-powered responses with crypto expertise
5. **Context Retention**: Remembers user wallets and preferences

## 🛠️ Setup

### Prerequisites

- Python 3.8+
- Twilio WhatsApp Business Account
- OpenRouter API Key
- Environment variables for API keys

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/sambitsargam/NeoLink.git
   cd NeoLink
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your actual API keys
   ```

   Required variables:
   ```bash
   TWILIO_ACCOUNT_SID=your_twilio_sid
   TWILIO_AUTH_TOKEN=your_twilio_token
   OPENROUTER_API_KEY=your_openrouter_key
   RPC_URL=https://eth.llamarpc.com
   ```

5. **Run the application:**
   ```bash
   python main.py
   ```

6. **Configure Twilio webhook:**
   Set your Twilio WhatsApp webhook URL to: `https://your-domain.com/webhook`

## 💬 Usage

Send WhatsApp messages to your Twilio number:

### Price Queries
- `"bitcoin price"` - Get BTC price with 24h change
- `"NEO price"` - Neo ecosystem token prices
- `"ethereum worth today"` - ETH market data

### Gas Fees
- `"gas fees"` - Current Ethereum gas prices
- `"network fees"` - Transaction cost estimates

### Wallet Management
- Send wallet address: `0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8e8`
- `"my balance"` - Check ETH balance
- `"USDC balance"` - Check token balances

### General Conversation
- `"hi"` - Start conversation
- `"what is DeFi?"` - Educational content
- `"tell me about Neo"` - Blockchain explanations

## 🏗️ Architecture

The agent is built using modern AI and blockchain technologies:

### Core Components

- **main.py**: Flask server handling Twilio webhooks
- **defi_whatsapp_agent.py**: Main NeoLinkSpoonAgent implementation
- **neolink/**: Package containing utilities and tools
- **config.json**: Spoon AI configuration

### Spoon AI Implementation

```python
class NeoLinkSpoonAgent(SpoonReactMCP):
    """DeFi agent using Spoon AI SDK with Neo Chain focus"""
    
    def __init__(self):
        super().__init__(
            llm_client="openrouter",
            model="anthropic/claude-3-haiku", 
            api_key=os.getenv('OPENROUTER_API_KEY'),
            system_prompt="Expert crypto assistant..."
        )
```

### Processing Flow

1. **WhatsApp Message** → Twilio Webhook
2. **Message Processing** → SpoonReactMCP Agent
3. **Intent Analysis** → Crypto actions vs conversation
4. **Data Fetching** → Live APIs (CoinGecko, Etherscan)
5. **AI Response** → OpenRouter Claude-3-Haiku
6. **WhatsApp Reply** → Twilio response

## 🔗 Supported Cryptocurrencies

### Neo Ecosystem (Specialized)
- **NEO**: Native Neo blockchain token
- **GAS**: Network utility token
- **FLM**: Flamingo DeFi protocol token

### Major Cryptocurrencies
- **Bitcoin (BTC)**: The original cryptocurrency
- **Ethereum (ETH)**: Smart contract platform
- **Solana (SOL)**: High-performance blockchain
- **Cardano (ADA)**: Research-driven blockchain
- **Polygon (MATIC)**: Ethereum scaling solution
- **And 100+ more tokens**

## 🔒 Security

### Best Practices

✅ **Environment Variables**: All secrets stored in .env file  
✅ **Read-Only Operations**: No transaction execution  
✅ **No Private Keys**: User wallets stored as addresses only  
✅ **API Key Safety**: Keys never logged or exposed  
✅ **Secure Communication**: HTTPS webhook endpoints  

### Security Notes

- Agent only reads blockchain data, never executes transactions
- User wallet addresses stored in memory only (not persistent)
- All API communication over secure channels
- No handling of private keys or sensitive data

## 🚀 Deployment

### Local Development
```bash
python main.py
# Server runs on http://localhost:5001
```

### Production Deployment
1. Deploy to cloud provider (Heroku, AWS, etc.)
2. Set environment variables in production
3. Configure Twilio webhook to production URL
4. Enable HTTPS for webhook security

### Environment Configuration

```bash
# Production
OPENROUTER_API_KEY=sk-or-your-production-key
RPC_URL=https://eth.llamarpc.com

# Development
OPENROUTER_API_KEY=sk-or-your-dev-key
RPC_URL=https://sepolia.infura.io/v3/your-key
```

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Spoon AI SDK**: Intelligent conversation framework
- **OpenRouter**: AI model access and routing
- **Twilio**: WhatsApp Business API
- **CoinGecko**: Cryptocurrency market data
- **Neo Blockchain**: Inspiration for Neo ecosystem focus

---

Built with ❤️ using [Spoon AI](https://spoon.dev) and focused on the Neo blockchain ecosystem 🔗anced DeFi WhatsApp Agent

A conversational WhatsApp bot that provides real-time DeFi data and education through natural AI-powered conversations. Built with Spoon AI framework and integrated with live blockchain APIs.

## Features

� **Conversational AI**: Natural, friendly conversations powered by OpenRouter's Claude-3-Haiku
📊 **Real Market Data**: Live cryptocurrency prices from CoinGecko API
⛽ **Gas Tracker**: Real-time Ethereum gas fees from Etherscan
🔗 **Blockchain Integration**: Live balance checking with Web3.py
📱 **WhatsApp Native**: Seamless integration with Twilio WhatsApp Business API
🎓 **DeFi Education**: Educational content and explanations for DeFi concepts
- 💾 **Memory** - User wallet storage
- 🛡️ **Security First** - Read-only operations, no private key handling

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your actual API keys and credentials
   ```
   Required variables:
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

- 🔐 **Environment Variables Only** - All API keys and secrets stored in .env file
- ⚠️ **Never Commit Secrets** - .env file is in .gitignore, never commit to version control
- 🛡️ **Private Key Security** - Use dedicated wallet for testing, rotate keys regularly
- ✅ **Read-only Operations** - Agent only reads blockchain data, doesn't execute transactions
- ✅ **Transfer preparation only** - No actual transaction execution
- ✅ **User wallet addresses** stored in memory only
- 🔒 **Config File Clean** - No secrets in config.json, only configuration parameters

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

### 🚨 CRITICAL SECURITY SETUP

**NEVER put API keys or private keys in config files!** All secrets must be in environment variables only.

1. **Create a dedicated wallet** for this agent (don't use your main wallet)
2. **Fund it minimally** - only enough ETH for gas if needed
3. **Use .env file only** - Never commit secrets to version control
4. **Check .gitignore** - Ensure .env is excluded from git

```bash
# In your .env file only:
TWILIO_ACCOUNT_SID=your_twilio_sid
TWILIO_AUTH_TOKEN=your_twilio_token
OPENAI_API_KEY=your_openrouter_key
PRIVATE_KEY=your_64_character_private_key_here
RPC_URL=https://eth.llamarpc.com
CHAINBASE_API_KEY=demo
CHAIN_ID=84532
```

**✅ SAFE:** Environment variables in .env file
**❌ DANGEROUS:** API keys in config.json or source code

### Environment Variables Priority

The Spoon AI SDK uses this priority order:
1. Tool-level `env` configuration (in config.json)
2. System environment variables (from .env file)
3. Default values

### Blockchain Configuration

- **Mainnet**: `CHAIN_ID=1`, `RPC_URL=https://eth.llamarpc.com`
- **Sepolia Testnet**: `CHAIN_ID=11155111`, `RPC_URL=https://sepolia.infura.io/v3/your_key`
- **Local**: `CHAIN_ID=1337`, `RPC_URL=http://localhost:8545`