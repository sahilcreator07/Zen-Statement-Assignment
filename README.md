# 🤖 ZenStatement AI-Powered Financial Reconciliation

An intelligent, agentic framework for automated financial transaction reconciliation using AI/ML. This system leverages Groq's Llama-3.3-70b LLM to analyze, categorize, and resolve financial discrepancies with minimal human intervention.

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Groq](https://img.shields.io/badge/Groq-Llama--3.3--70b-orange.svg)](https://console.groq.com/)

## 🎯 Overview

This project implements an **autonomous AI agent** that processes financial reconciliation data through intelligent analysis and categorization. The system can:

- **🔍 Preprocess** large transaction datasets
- **🤖 Analyze** free-text comments using AI
- **📊 Categorize** cases as resolved/unresolved
- **📈 Identify** resolution patterns and trends
- **📋 Generate** actionable next steps

  <img width="807" alt="Screenshot 2025-07-06 at 3 25 29 PM" src="https://github.com/user-attachments/assets/cc037b32-2454-4cb2-a62c-b8011715b0af" />

## ✨ Key Features

### 🧠 **Intelligent Agent System**
- **LangChain ReAct Agent** with dynamic planning
- **Groq Llama-3.3-70b** for advanced reasoning
- **Autonomous workflow** execution
- **Audit trail** for all decisions

### 📊 **Data Processing**
- **CSV preprocessing** with intelligent filtering
- **Discrepancy detection** (recon_status = 'Not Found')
- **Pattern recognition** in resolution types
- **Structured output** generation

### 🛠️ **Modular Architecture**
- **Wrapper functions** for AI agent communication
- **Tool-based design** for extensibility
- **Error handling** with graceful fallbacks
- **Containerized deployment** ready

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Input Data    │    │   AI Agent      │    │   Output Files  │
│                 │    │                 │    │                 │
│ • recon_data_   │───▶│ • LangChain     │───▶│ • resolved.csv  │
│   raw.csv       │    │ • Groq LLM      │    │ • unresolved.csv│
│ • recon_data_   │    │ • Tool Wrappers │    │ • patterns.json │
│   reply.csv     │    │ • ReAct Pattern │    │ • next_steps.csv│
└─────────────────┘    └─────────────────┘    └─────────────────┘
```
<img width="660" alt="Screenshot 2025-07-06 at 8 33 33 PM" src="https://github.com/user-attachments/assets/738c18d6-6b9e-41e4-be04-fd3736eab489" />



## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Groq API key ([Get one here](https://console.groq.com/))

### 1. Clone & Setup
```bash
git clone <your-repo-url>
cd ZenStatement_AI_ML_Assignment
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Environment
```bash
# Copy environment template
cp .env.example .env

# Add your Groq API key
echo "GROQ_API_KEY=your_api_key_here" >> .env
```

### 4. Prepare Data
Place your CSV files in the `data/` directory:
```bash
data/
├── recon_data_raw.csv      # Transaction data
└── recon_data_reply.csv    # Comments/responses
```

### 5. Run the System
```bash
input_data_path = "data/your_dataset_name.csv" -> dataset with col racon_data_raw.csv
comments_data_path = "data/your_dataset_name.csv" -> dataset with col racon_data_reply
python src/agentic_main.py
```

## 📁 Project Structure

```
ZenStatement_AI_ML_Assignment/
├── 📂 src/
│   ├── 🐍 agentic_main.py    # Entry point
│   ├── 🤖 agent.py           # AI agent orchestration
│   ├── 🛠️ tools.py           # Core functions
│   └── 🔧 utils.py           # Utilities
├── 📂 data/                  # Input data
│   ├── recon_data_raw.csv    # Transaction data
│   └── recon_data_reply.csv  # Comments data
├── 📂 output/                # Generated results
│   ├── discrepancies/        # Filtered discrepancies
│   ├── resolved/            # Resolved cases
│   ├── unresolved/          # Unresolved cases
│   └── patterns/            # Pattern analysis
├── 📄 requirements.txt       # Dependencies
├── 🐳 Dockerfile            # Container setup
├── 📄 .env                  # Configuration
└── 📖 README.md            # This file
```

## 🔧 Configuration

### Environment Variables (.env)
```bash
# Required
GROQ_API_KEY=your_groq_api_key_here

# Optional
UPLOAD_TARGET=local
LOG_LEVEL=INFO
```

### Input Data Format

#### Transaction Data (`recon_data_raw.csv`)
```csv
txn_ref_id,sys_a_date,sys_a_amount_attribute_1,recon_status,...
44516715,02/04/24,20.000000,Not Found,...
34286015,07/07/24,116.699997,Not Found,...
```

#### Comments Data (`recon_data_reply.csv`)
```csv
Transaction ID,amount,Comments
44516715,20,The payment was not found in the corresponding financial report...
34286015,116.6999969,The payment gateway didn't return the correct confirmation...
```

## 📊 Output Structure

After running, you'll find organized results in `output/`:

### 📁 `output/discrepancies/`
- **discrepancies.csv**: Filtered transaction discrepancies

### 📁 `output/resolved/`
- **resolved.csv**: Cases marked as resolved by AI

### 📁 `output/unresolved/`
- **unresolved.csv**: Cases needing attention
- **next_steps.csv**: Action items for unresolved cases

### 📁 `output/patterns/`
- **patterns.json**: Analysis of resolution patterns


## 🔍 How It Works

### 1. **Data Preprocessing**
```python
# Filters transactions with recon_status = 'Not Found'
preprocess_transactions("data/recon_data_raw.csv", "output/discrepancies.csv")
```

### 2. **AI Analysis**
```python
# AI analyzes each comment and determines resolution status
resolve_comments("data/recon_data_reply.csv")
```

### 3. **Intelligent Categorization**
```python
# AI response example:
{
  "is_resolved": true,
  "resolution_summary": "Customer provided payment proof",
  "next_steps": "None - resolved",
  "resolution_pattern": "Payment Verification",
  "confidence": 0.95
}
```

### 4. **Pattern Recognition**
- Identifies common resolution types
- Analyzes trends in resolution patterns
- Generates insights for process improvement


## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

