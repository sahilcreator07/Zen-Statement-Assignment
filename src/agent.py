"""
agent.py
Defines the agent orchestration using LangChain ReAct Agent pattern with Groq Llama-3.3-70b.
"""

from langchain.agents import initialize_agent, Tool
from langchain_groq import ChatGroq
from typing import List
import os
from loguru import logger
from src.tools import preprocess_transactions, resolve_comments
import re



# Before Wrapper, AI agents use human-like format:
# "input_csv = 'data/file.csv', output_csv = 'output/result.csv'" 
# therefore, it do not send as a python object.

def parse_kwargs_from_string(s):
    """Parse a string like 'input_csv = "foo.csv", output_csv = "bar.csv"' into kwargs dict."""
    s = s.strip()
    matches = re.findall(r'(\w+)\s*=\s*[\'"]([^\'"]+)[\'"]', s)
    return {k: v for k, v in matches}

def preprocess_wrapper(*args, **kwargs):
    logger.debug(f"preprocess_wrapper called with args={args}, kwargs={kwargs}")
    # Handle stringified input from agent
    if args and isinstance(args[0], str) and 'input_csv' in args[0]:
        kw = parse_kwargs_from_string(args[0])
        logger.debug(f"Parsed kwargs from string: {kw}")
        input_csv = kw.get('input_csv')
        output_csv = kw.get('output_csv', 'output/discrepancies/discrepancies.csv')
        if not input_csv:
            raise ValueError('input_csv not found in agent input string')
        return (input_csv, output_csv)
    # Handle normal positional/keyword args
    input_csv = args[0] if args else kwargs.get('input_csv')
    output_csv = args[1] if len(args) > 1 else kwargs.get('output_csv', 'output/discrepancies/discrepancies.csv')
    return preprocess_transactions(input_csv, output_csv)



def resolve_wrapper(*args, **kwargs):
    print(f"RESOLVE_WRAPPER CALLED with args={args}, kwargs={kwargs}")
    logger.debug(f"resolve_wrapper called with args={args}, kwargs={kwargs}")
    
    # Get the input string
    if args and isinstance(args[0], str):
        s = args[0].strip()
        print(f"Input string: '{s}'")
        
        # Try to extract the file path from quotes (handle incomplete quotes)
        # First try normal quoted strings
        quoted = re.findall(r'["\']([^"\']+)["\']', s)
        print(f"Extracted quoted strings: {quoted}")
        
        if quoted:
            file_path = quoted[0]
            print(f"Using file path: {file_path}")
            return resolve_comments(file_path)
        else:
            # Try to extract from incomplete quotes (missing closing quote)
            incomplete = re.findall(r'["\']([^"\']+)$', s)
            if incomplete:
                file_path = incomplete[0]
                print(f"Using incomplete quoted file path: {file_path}")
                return resolve_comments(file_path)
            else:
                # Try to extract the last part after the last space
                parts = s.split()
                if len(parts) > 1:
                    file_path = parts[-1].strip('"\'')
                    print(f"Using last part as file path: {file_path}")
                    return resolve_comments(file_path)
                else:
                    print(f"No quoted string found, using entire string: {s}")
                    return resolve_comments(s)
    
    # Fallback
    comments_csv = args[0] if args else kwargs.get('comments_csv')
    print(f"Fallback using: {comments_csv}")
    return resolve_comments(comments_csv)

def get_tools():
    """
    Register all tools for the agent.
    Returns a list of LangChain Tool objects.
    """
    tools = [
        Tool(
            name="preprocess_transactions",
            func=preprocess_wrapper,
            description="Clean and filter transaction data from CSV. Input: input_csv, output_csv. Output: path to filtered CSV with discrepancies."
        ),
        # remove upload_file cuz it was redundant. 
        # Tool(
        #     name="upload_file",
        #     description="Use LLM to analyze comments and determine resolution status, generate summaries, next steps, and identify patterns. Input: comments_csv. Output: dict with resolution results and file paths."
        # )
        Tool(
            name="resolve_comments",
            func=resolve_wrapper,
            description="Use LLM to analyze comments and determine resolution status, generate summaries, next steps, and identify patterns. Input: comments_csv. Output: dict with resolution results and file paths."
        )
    ]
    return tools

def create_agent():
    """
    Initializes and returns the LangChain agent with registered tools using Groq Llama-3.3-70b.
    """
    # Initialize Groq LLM
    llm = ChatGroq(
        groq_api_key=os.getenv("GROQ_API_KEY"),
        model_name="llama-3.3-70b-versatile",
        temperature=0.1
    )
    
    tools = get_tools()
    
    # Create agent with ReAct pattern
    agent = initialize_agent(
        tools,
        llm,
        agent="zero-shot-react-description",
        verbose=True,
        handle_parsing_errors=True,
        max_iterations=10
    )
    
    logger.info("Agent initialized with Groq Llama-3.3-70b LLM and tools")
    return agent

def run_agent_workflow(agent, input_data_path: str, comments_data_path: str):
    """
    Run the complete agent workflow for financial reconciliation.
    """
    workflow_prompt = f"""
    You are a financial reconciliation agent. Your task is to:
    
    1. Preprocess transaction data from {input_data_path} to find discrepancies (recon_status = 'Not Found')
    2. Save the discrepancy file to output/discrepancies/discrepancies.csv
    3. Process comments from {comments_data_path} using LLM to determine resolution status
    
    Plan your steps dynamically and execute them. Log your reasoning at each step.
    """
    
    logger.info("Starting agent workflow")
    result = agent.run(workflow_prompt)
    logger.info("Agent workflow completed")
    return result


