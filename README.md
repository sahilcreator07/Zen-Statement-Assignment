# ZenStatement Agentic Reconciliation Framework

## Overview
This project implements an autonomous, agentic framework for financial transaction reconciliation, designed for ZenStatement. It leverages LLM-driven dynamic planning and tool orchestration to process, resolve, and act on financial discrepancies.

---

## Features
- **Dynamic Agent:** Uses LangChain ReAct Agent with Groq Llama-3.3-70b LLM for step-by-step planning and tool selection.
- **Data Preprocessing:** Cleans and filters transaction data from CSVs.
- **Automated Actions:** Uploads files to local output directories.
- **LLM Resolution:** Uses Groq Llama-3.3-70b to reason over free-text comments and suggest next steps.
- **Audit Logging:** Logs all agent thoughts, actions, and decisions for traceability.
- **Modular Tools:** All actions (preprocess, upload, resolve) are modular and agent-invokable.
- **Containerized:** Ready to run locally or in Docker.

---

## Project Structure
```
ZenStatement_AI_ML_Assignment/
  ├── src/
  │   ├── tools.py           # Tool definitions
  │   ├── agent.py           # Agent orchestration
  │   ├── agentic_main.py    # Entry point
  │   ├── utils.py           # Utilities (logging, config)
  ├── data/                  # Example input data
  ├── output/                # Generated outputs
  ├── requirements.txt
  ├── Dockerfile
  ├── .env                   # Secrets/config
  └── README.md
```

---

## Setup
1. **Clone the repo:**
   ```bash
   git clone <repo-url>
   cd ZenStatement_AI_ML_Assignment
   ```
2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Configure environment:**
   - Copy `.env.example` to `.env` and add your Groq API key
   - Place your CSV files in the `data/` directory:
     - `data/recon_data_raw.csv` (transaction data)
     - `data/recon_data_reply.csv` (comments data)

---

## Usage
Run the agent end-to-end:
```bash
python src/agentic_main.py
```

- Input CSVs should be placed in the `data/` directory.
- Outputs will be saved in the `output/` directory with the following structure:
  - `output/discrepancies/` - Filtered transaction discrepancies
  - `output/resolved/` - Resolved cases
  - `output/unresolved/` - Unresolved cases and next steps
  - `output/patterns/` - Resolution pattern analysis

---

## Testing
- Use the provided sample CSVs in `data/` or your own.
- Check `output/` for generated files.
- Review logs for agent reasoning and actions.

---

## Deployment (Docker)
Build and run in Docker:
```bash
docker build -t zenstatement-agent .
docker run --env-file .env -v $(pwd)/data:/app/data -v $(pwd)/output:/app/output zenstatement-agent
```

---

## Configuration (.env)
- `GROQ_API_KEY`: Your Groq API key (get from https://console.groq.com/)
- `UPLOAD_TARGET`: `local` (default)

---

## Groq API Setup
1. Sign up at https://console.groq.com/
2. Get your API key from the console
3. Add it to your `.env` file:
   ```
   GROQ_API_KEY=your_groq_api_key_here
   ```

---

## Notes
- All agent actions and thoughts are logged for auditability.
- The agent dynamically plans its workflow and handles failures/retries.
- Modular tools can be extended or swapped as needed.
- Uses Groq's Llama-3.3-70b-versatile model for fast, cost-effective LLM processing.

---

## License
MIT
