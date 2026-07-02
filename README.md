# LLMs & Agents Project

This repository contains learning materials and production-ready AI applications built using AutoGen Studio, AutoGen AgentChat, and Streamlit. Each project demonstrates a different multi-agent pattern — from creative writing pipelines to real-time crypto intelligence and AI-powered resume tailoring.

## 📁 Project Structure

```
LLMs&Agents/
├── P02-S01-01-Basic_LLM.ipynb              # Introduction to LLM basics
├── P02-S01-02-Running_autogen.ipynb        # Running AutoGen framework
├── P02-S01-03-Two_standup_comedians.ipynb  # Multi-agent conversation example
├── DeployWriters/                           # AI Writing application (AutoGen Studio)
│   ├── streamlit_selector_writer_app.py    # Streamlit frontend application
│   ├── writers_team.json                   # AutoGen team configuration
│   └── serve_fixed.py                      # Fixed AutoGen Studio API server
├── DeployBitcoin/                           # Crypto Price & News application
│   ├── streamlit_bitcoin_app.py            # Streamlit frontend application
│   └── BitcoinPriceNews.json               # AutoGen team configuration
├── ResumeAdjuster/                          # AI Resume Adaptation application
│   ├── app.py                              # Streamlit frontend application
│   ├── team-resume.json                    # AutoGen team configuration
│   ├── resume.md                           # Base resume file (replace with yours)
│   └── requirements.txt                    # Project-specific dependencies
├── requirements.txt                         # Global Python dependencies
└── README.md                               # Project documentation
```

---

## 📚 Jupyter Notebooks

### P02-S01-01-Basic_LLM.ipynb
**Introduction to Large Language Models**

Covers fundamental concepts of LLMs including:
- Basic LLM architecture
- Prompt engineering basics
- API interactions with OpenAI
- Simple text generation examples

**Usage:**
```bash
jupyter notebook P02-S01-01-Basic_LLM.ipynb
```

### P02-S01-02-Running_autogen.ipynb
**Running AutoGen Framework**

Comprehensive guide to AutoGen framework featuring:
- AutoGen installation and setup
- Creating agents with different roles
- Agent communication patterns
- Task orchestration
- Multi-agent workflows

**Key Topics:**
- AssistantAgent configuration
- UserProxyAgent setup
- Team configurations
- Message passing between agents
- Termination conditions

**Usage:**
```bash
jupyter notebook P02-S01-02-Running_autogen.ipynb
```

### P02-S01-03-Two_standup_comedians.ipynb
**Multi-Agent Conversation Example**

Fun example demonstrating:
- Two-agent dialogue systems
- Role-playing with specialized prompts
- Creative writing with AI agents
- Conversation flow control

**Scenario:** Two AI agents roleplay as standup comedians, generating jokes and banter.

**Usage:**
```bash
jupyter notebook P02-S01-03-Two_standup_comedians.ipynb
```

---

## 🖋️ DeployWriters — AI Writing Application

A production-ready web application that uses multiple AI writers to generate content based on user requests.

### Architecture

```
User Request → Streamlit UI → Fixed API Server → AutoGen Team
                                                  ├─ Selector Agent
                                                  ├─ Technical Writer
                                                  └─ Creative Writer
```

### Components

#### 1. **streamlit_selector_writer_app.py**
**Frontend Web Application**

- **Framework:** Streamlit
- **Port:** Default Streamlit port (typically 8501)
- **Features:**
  - Clean, intuitive text input interface

#### 2. **writers_team.json**
**AutoGen Team Configuration**

Defines the multi-agent writing team with:
- `selector_agent`: Routes requests to the appropriate writer
- `technical_writer`: Generates structured technical content
- `creative_writer`: Produces narrative and creative content

#### 3. **serve_fixed.py**
**Fixed AutoGen Studio API Server**

**Problem Solved:**
Default AutoGen Studio doesn't include message `content` in JSON responses — only `source`, `models_usage`, and `metadata` fields are returned.

**Solution:**
- Custom serialization extracts content using `content` attribute or `to_text()` method
- Properly handles `RequestUsage` objects
- Returns complete messages with content included

**API Endpoint:**
```
GET /predict/{task}
```

**Response Format:**
```json
{
  "message": "Task successfully completed",
  "status": true,
  "data": {
    "task_result": {
      "messages": [
        {
          "source": "technical_writer",
          "content": "# Generated Content\n...",
          "models_usage": {
            "prompt_tokens": 73,
            "completion_tokens": 486
          },
          "metadata": {}
        }
      ],
      "stop_reason": "Text 'TERMINATE' mentioned"
    },
    "usage": "",
    "duration": 12.14
  }
}
```

**Key Functions:**
- `serialize_message()`: Extracts and formats message content
- `serialize_task_result()`: Formats complete task results
- `predict()`: Main API endpoint handler

---

## 💰 DeployBitcoin — Crypto Price & News Application

A real-time cryptocurrency intelligence dashboard powered by two AutoGen agents. Users enter any cryptocurrency name and the app retrieves live price metrics and the latest news in one unified view.

### Architecture

```
User Input (crypto name)
    │
    ▼
Streamlit UI ──► AutoGen Studio API (port 8084)
                        │
              RoundRobinGroupChat
              ├─ price_retriever  ──► CoinGecko API (live prices)
              └─ news_retriever   ──► CryptoPanic API (latest news)
```

### Agents

| Agent | Role | External API |
|-------|------|-------------|
| `price_retriever` | Fetches real-time price, market cap, 24h volume, and 24h change | CoinGecko (free tier) |
| `news_retriever` | Fetches the latest crypto news articles with titles, descriptions, and publication timestamps | CryptoPanic |

Both agents run in a `RoundRobinGroupChat` and coordinate so that the `price_retriever` outputs the combined results and appends `TERMINATE` once both data sources have been collected.

### Features

- **Live Price Metrics:** Current USD price, market cap, 24-hour trading volume, 24-hour percentage change, and last-updated timestamp
- **Latest News Feed:** News title, description, publication date, and article link
- **Works with any cryptocurrency** supported by CoinGecko (e.g., `bitcoin`, `ethereum`, `solana`)
- **JSON Debug View:** Optional toggle to inspect the raw API response

### Components

#### **streamlit_bitcoin_app.py**
**Frontend Web Application**

- **Framework:** Streamlit
- **Port:** 8501 (default)
- **Connects to:** `serve_fixed.py` API on port 8084
- Key session state variables: `api_result`, `is_generating`, `show_full_response`

#### **BitcoinPriceNews.json**
**AutoGen Team Configuration**

Defines the two-agent team:

**`price_retriever` agent:**
- Uses `get_crypto_price(coin)` function tool
- Calls CoinGecko's `/simple/price` endpoint
- Returns price, market cap, 24h volume, 24h change, and last-updated timestamp

**`news_retriever` agent:**
- Uses `get_crypto_news(currency_code, filter_type)` function tool
- Calls CryptoPanic's `/api/v1/posts/` endpoint
- Returns news ID, title, description, published date, kind, and URL

Both agents use **GPT-4o Mini** (`gpt-4o-mini`) as the model backend.

### Running DeployBitcoin

This application shares the API server (`serve_fixed.py`) with DeployWriters. The AutoGen Studio team configuration for this app is `BitcoinPriceNews.json`.

**Terminal 1 — Start API Server (with this team config):**
```bash
cd DeployBitcoin
export AUTOGENSTUDIO_TEAM_FILE="$(pwd)/BitcoinPriceNews.json"
source ../venv/bin/activate
uvicorn serve_fixed:app --host 127.0.0.1 --port 8084
```
> Note: `serve_fixed.py` lives in `DeployWriters/`. Adjust the path accordingly.

**Terminal 2 — Start Streamlit App:**
```bash
cd DeployBitcoin
streamlit run streamlit_bitcoin_app.py
```

**Open your browser** at `http://localhost:8501`

### Configuration

**API Keys to replace in `BitcoinPriceNews.json`:**
```json
{
  "api_key": "YOUR_OPENAI_API_KEY_HERE"
}
```
```python
api_key = 'YOUR_CRYPTOPANIC_API_KEY_HERE'
```

> CoinGecko's public price endpoint is free and requires no API key for basic use.

### Usage Example

```
Input: bitcoin

Output:
📈 Bitcoin Price Metrics
- Price: $68,450.00
- Market Cap: $1,348,291,000,000
- 24H Volume: $28,403,000,000
- 24H Change: +2.34%
- Last Updated At: 2025-03-10 14:32:01

📰 Latest Bitcoin News
- "Bitcoin Hits New Monthly High Amid ETF Inflows"
  Published: 2025-03-10T13:45:00Z
  [Link](https://cryptopanic.com/...)
```

---

## 📄 ResumeAdjuster — AI Resume Adaptation Application

An AI-powered resume tailoring tool that adapts a base resume to match a specific job description using two AutoGen agents. The app outputs an ATS-optimised resume along with a match score and reviewer feedback — all within a clean Streamlit interface.

### Architecture

```
User Input (job description)
    │
    ▼
Streamlit UI
    │
    ▼
RoundRobinGroupChat (autogen-agentchat)
    ├─ adapter_agent ──► reads resume.md ──► adapts content ──► saves resume.md
    └─ reviewer_agent ──► evaluates adapted resume ──► ATS score + feedback
```

> Unlike DeployWriters and DeployBitcoin, this app runs **without a separate API server** — the AutoGen team is instantiated directly inside the Streamlit app using `autogen-agentchat`.

### Agents

| Agent | Role |
|-------|------|
| `adapter_agent` | Loads `resume.md`, rewrites it to mirror the job description's keywords and requirements, and saves the updated version back to disk |
| `reviewer_agent` | Reviews the adapted resume, compares it to the job description, and returns an ATS match score (0–100%) plus improvement suggestions |

Both agents use **GPT-4o Mini** and run in a `RoundRobinGroupChat` so the `adapter_agent` always acts before the `reviewer_agent`.

### Key Design Decisions

- **ATS keyword mirroring**: The adapter agent is instructed to use exact terminology from the job description wherever it appears naturally.
- **Factual accuracy enforcement**: The system prompt explicitly prohibits fabricating experience, dates, or qualifications.
- **File-based resume state**: `resume.md` acts as the working copy. Each adaptation overwrites it, so the reviewer always sees the latest version.

### Features

- **Job Description Input:** Paste any job posting (minimum 50 characters)
- **Adapted Resume Output:** Fully rewritten Markdown resume targeting the job
- **ATS Match Score:** AI-estimated percentage match (0–100%)
- **Reviewer Feedback:** Detailed evaluation of how well the adapted resume aligns with the job posting
- **Download Button:** Save the adapted resume as `adapted_resume.md`
- **Reset Button:** Start fresh with a new job description

### Components

#### **app.py**
**Main Streamlit Application**

- **Framework:** Streamlit (wide layout)
- **Port:** 8501 (default)
- Two-column layout: job description input on the left, results on the right
- `extract_results(messages)`: Parses AutoGen message objects to separate the adapted resume, reviewer feedback, and ATS score
- `run_team(job_description)`: Instantiates the agent team from `team-resume.json` and runs the task asynchronously with `asyncio`

#### **team-resume.json**
**AutoGen Team Configuration**

Defines the two-agent team with:
- `RoundRobinGroupChat` as the coordination strategy
- Function tools embedded in the agent config via `FunctionTool`:
  - `get_fixed_resume_content()`: Reads `resume.md` from the working directory
  - `save_fixed_resume_content(updated_resume)`: Writes the adapted resume back to `resume.md`
- `UnboundedChatCompletionContext` for full message history retention

#### **resume.md**
**Base Resume File**

This is the source resume that the `adapter_agent` reads and adapts. Replace the file contents with your own resume before running the app. The format expected is Markdown with the following sections:
```markdown
# Your Name - Your Title

**Summary:**
...

**Experience:**
* **Company** (dates) - description

**Skills:**
Python, SQL, ...
```

### Running ResumeAdjuster

**Install dependencies:**
```bash
cd ResumeAdjuster
pip install -r requirements.txt
```

**Add your OpenAI API key to `team-resume.json`:**
```json
{
  "api_key": "YOUR_OPENAI_API_KEY_HERE"
}
```

**Add your resume to `resume.md`** (replace the placeholder content with your own).

**Run the app:**
```bash
streamlit run app.py
```

**Open your browser** at `http://localhost:8501`

### How to Use

1. Paste the full job description into the text area on the left (requirements, responsibilities, qualifications)
2. Click **🔄 Adjust Resume**
3. Wait 10–30 seconds for the agents to run
4. Review:
   - **ATS Match Score** shown prominently at the top of the results column
   - **Adapted Resume** in the expandable section below
   - **Reviewer Feedback** with specific alignment suggestions
5. Click **⬇️ Download Resume** to save as `adapted_resume.md`
6. Click **🔄 Start New Adjustment** to try another job description

### File Structure

```
ResumeAdjuster/
├── app.py                 # Main Streamlit application
├── team-resume.json       # AutoGen team configuration
├── requirements.txt       # Project-specific Python dependencies
├── resume.md              # Base resume (edit this with your own)
└── README.md              # Project-level documentation
```

### Notes

- The ATS score is an **AI estimate**, not an actual ATS system output
- The `adapter_agent` overwrites `resume.md` on each run — keep a backup of your original
- Processing time is typically 10–30 seconds depending on job description length
- The app requires an active internet connection to reach the OpenAI API

---

## 🚀 Getting Started

### Prerequisites

```bash
python 3.8+
pip
virtualenv or venv
```

### Installation

1. **Clone the repository:**
```bash
git clone https://github.com/reemelmahdi/LLMs-Agents.git
cd LLMs-Agents
```

2. **Create and activate virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Configure your OpenAI API key:**
   - **DeployWriters:** Edit `DeployWriters/writers_team.json`
   - **DeployBitcoin:** Edit `DeployBitcoin/BitcoinPriceNews.json`
   - **ResumeAdjuster:** Edit `ResumeAdjuster/team-resume.json`
   - Replace all instances of `"YOUR_OPENAI_API_KEY_HERE"` with your actual key

### Running Each Application

| Project | Command | Notes |
|---------|---------|-------|
| **DeployWriters** | `uvicorn serve_fixed:app` + `streamlit run streamlit_selector_writer_app.py` | Requires two terminals |
| **DeployBitcoin** | `uvicorn serve_fixed:app` + `streamlit run streamlit_bitcoin_app.py` | Requires two terminals + CryptoPanic API key |
| **ResumeAdjuster** | `streamlit run app.py` | Single terminal; no separate server needed |

---

## 💡 Usage Examples

### Technical Writing Request (DeployWriters)
```
Input: "Explain quantum computing"

Output: Structured article with:
- Introduction
- Key Concepts (Qubits, Entanglement, Quantum Gates)
- Quantum Algorithms
- Applications
- Current Challenges
- Conclusion
```

### Creative Writing Request (DeployWriters)
```
Input: "Write a story about a robot discovering emotions"

Output: Engaging narrative with:
- Character development
- Emotional arc
- Literary devices
- Descriptive language
- Creative plot structure
```

### Crypto Insights Request (DeployBitcoin)
```
Input: "ethereum"

Output:
- Real-time price, market cap, 24h volume, 24h change
- Latest Ethereum news from CryptoPanic
```

### Resume Adaptation Request (ResumeAdjuster)
```
Input: Job description for a Senior ML Engineer role requiring
       PyTorch, MLflow, and Kubernetes experience

Output:
- Adapted resume with repositioned and reworded bullet points
- ATS Match Score: 82%
- Reviewer feedback on keyword alignment and suggested improvements
```

---

## 🔧 Configuration

### API Configuration

| File | Variable | Description |
|------|----------|-------------|
| `streamlit_selector_writer_app.py` | `BASE_API_URL` | AutoGen API server URL (default: `http://127.0.0.1:8084`) |
| `streamlit_bitcoin_app.py` | `BASE_API_URL` | AutoGen API server URL (default: `http://127.0.0.1:8084`) |
| `streamlit_bitcoin_app.py` | `GPT4O_API_KEY` | OpenAI API key passed in the Authorization header |

### Agent Configuration

To modify agent behavior, edit the relevant `*.json` team configuration file:
1. Edit `system_message` for each agent to change instructions
2. Adjust `max_messages` for longer conversations
3. Change `model` to use a different GPT version
4. Update `api_key` with your OpenAI key

### Model Selection

All applications currently use `gpt-4o-mini`. To switch models:
```json
{
  "model": "gpt-4o",
  "api_key": "your-api-key"
}
```

---

## 🔐 Security Notes

**API Keys:**
- Current configuration includes OpenAI API keys in JSON team files
- **⚠️ Never commit API keys to version control**
- Use environment variables for production:

```bash
export OPENAI_API_KEY="your-key-here"
```

Update the relevant JSON file:
```json
{
  "api_key": "${OPENAI_API_KEY}"
}
```

---

## 📚 Resources

### AutoGen Documentation
- [AutoGen Official Docs](https://microsoft.github.io/autogen/)
- [AutoGen Studio Guide](https://microsoft.github.io/autogen/docs/autogen-studio/)

### Streamlit Documentation
- [Streamlit Docs](https://docs.streamlit.io/)
- [Streamlit API Reference](https://docs.streamlit.io/library/api-reference)

### OpenAI Documentation
- [OpenAI API Reference](https://platform.openai.com/docs/api-reference)
- [GPT-4 Guide](https://platform.openai.com/docs/guides/gpt)

### External APIs Used
- [CoinGecko API](https://www.coingecko.com/en/api) — Free cryptocurrency price data
- [CryptoPanic API](https://cryptopanic.com/developers/api/) — Cryptocurrency news aggregator

---

## 🙏 Acknowledgments

All the information mentioned in this repo is the result of learning the **"AutoGen Studio: No Code AI Agents"** course on Udemy. You can find it [here](https://www.udemy.com/course/autogen-studio-no-code-ai-agents/?couponCode=MT251110G1).