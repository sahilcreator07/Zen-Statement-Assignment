"""
tools.py
Defines modular tools for the ZenStatement agentic framework.
"""

from typing import List, Dict, Any
import pandas as pd
import os
import json
from loguru import logger
from groq import Groq

# --- Preprocessing Tool ---
def preprocess_transactions(input_csv: str, output_csv: str) -> str:
    """
    Cleans and filters transaction data from input_csv.
    Exports rows with recon_status == 'Not Found' to output_csv (Order ID, Amount, Date).
    Returns the path to the output CSV.
    """
    logger.info(f"Preprocessing transactions from {input_csv}")
    # Read the CSV file
    try:
        df = pd.read_csv(input_csv, encoding='utf-8')
    except UnicodeDecodeError:
        df = pd.read_csv(input_csv, encoding='latin-1')
    logger.info(f"Loaded {len(df)} transactions from {input_csv}")
    # Drop rows with missing critical fields
    df = df.dropna(subset=["txn_ref_id", "sys_a_amount_attribute_1", "sys_a_date", "recon_status"])
    # Filter rows where recon_status == 'Not Found'
    filtered = df[df["recon_status"] == "Not Found"]
    # Rename columns for output
    filtered = filtered.rename(columns={
        "txn_ref_id": "Order ID",
        "sys_a_amount_attribute_1": "Amount",
        "sys_a_date": "Date"
    })
    filtered = filtered[["Order ID", "Amount", "Date"]]
    
    # Create output directory if it doesn't exist
    os.makedirs(os.path.dirname(output_csv), exist_ok=True)
    filtered.to_csv(output_csv, index=False)
    logger.info(f"Exported {len(filtered)} discrepancies to {output_csv}")
    return output_csv

# --- Upload Tool (Local Only) ---
def upload_file(file_path: str, target_dir: str = "output/") -> str:
    """
    Moves or copies a file to the specified local output directory.
    Returns the new file path.
    """
    os.makedirs(target_dir, exist_ok=True)
    base_name = os.path.basename(file_path)
    dest_path = os.path.join(target_dir, base_name)
    
    # If source and destination are the same, just return the path
    if file_path == dest_path:
        logger.info(f"File already at destination: {dest_path}")
        return dest_path
    
    # Copy file
    import shutil
    shutil.copy(file_path, dest_path)
    logger.info(f"Uploaded {file_path} to {dest_path}")
    return dest_path

# --- Email Tool ---
def send_email(subject: str, body: str, attachments: List[str], to: List[str]) -> str:
    """
    Sends an email with attachments.
    Returns a status message.
    """
    # TODO: Implement email sending
    pass

# --- LLM Resolution Tool (Groq Llama-3.3-70b) ---
def resolve_comments(comments_csv: str) -> Dict[str, Any]:
    """
    Uses Groq Llama-3.3-70b LLM to process comments and decide resolution status, summaries, next steps, and patterns.
    Returns dicts for resolved, unresolved, next_steps, and patterns.
    """
    logger.info(f"Starting LLM resolution of comments from {comments_csv}")
    
    # Initialize Groq client
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    
    # Read comments data
    try:
        df = pd.read_csv(comments_csv, encoding='utf-8')
    except UnicodeDecodeError:
        df = pd.read_csv(comments_csv, encoding='latin-1')
    # Limit to first 10 rows for testing else it will take too long to generate the summary for all the comments.
    df = df.head(10)
    logger.info(f"Processing {len(df)} comments (sample mode)")
    
    resolved_cases = []
    unresolved_cases = []
    next_steps = []
    resolution_patterns = []
    
    # Process each comment
    for idx, row in df.iterrows():
        # Use 'Order ID' if present, else 'Transaction ID'
        if 'Order ID' in row:
            order_id = row['Order ID']
        elif 'Transaction ID' in row:
            order_id = row['Transaction ID'] # in our case we have Transaction ID
        else:
            raise KeyError('Neither "Order ID" nor "Transaction ID" found in comments CSV row')
        comment = row["Comments"]
        
        # Create prompt for LLM analysis
        prompt = f"""
        Analyze this financial reconciliation comment and determine:
        
        Order ID: {order_id}
        Comment: {comment}
        
        Please respond in JSON format with the following structure:
        {{
            "is_resolved": true/false,
            "resolution_summary": "Brief summary of what happened",
            "next_steps": "What should be done next (if unresolved)",
            "resolution_pattern": "Category/pattern of resolution (e.g., 'Payment Verification', 'System Sync Issue', 'Manual Correction', 'Customer Refund', etc.)",
            "confidence": 0.0-1.0
        }}
        
        Consider:
        - Is the issue fully resolved?
        - What was the root cause?
        - What pattern does this resolution follow?
        - What are the next steps if unresolved?
        """
        
        try:
            # Call Groq Llama-3.3-70b API
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=500
            )
            
            
            llm_response = response.choices[0].message.content.strip() # This line extracts the actual text content of the LLM’s reply.
            
            # Extract JSON from response (handle cases where LLM adds extra text)
            try:
                # Find JSON in the response
                start_idx = llm_response.find('{')
                end_idx = llm_response.rfind('}') + 1
                json_str = llm_response[start_idx:end_idx]
                result = json.loads(json_str)
                
                # Add order_id to result
                result["order_id"] = order_id
                result["original_comment"] = comment
                
                # Categorize based on resolution status
                if result.get("is_resolved", False):
                    resolved_cases.append(result)
                    resolution_patterns.append({
                        "order_id": order_id,
                        "pattern": result.get("resolution_pattern", "Unknown"),
                        "summary": result.get("resolution_summary", "")
                    })
                else:
                    unresolved_cases.append(result)
                    next_steps.append({
                        "order_id": order_id,
                        "next_steps": result.get("next_steps", "No steps specified"),
                        "summary": result.get("resolution_summary", "")
                    })
                
                logger.info(f"Processed Order ID {order_id}: {'Resolved' if result.get('is_resolved') else 'Unresolved'}")
                
            except json.JSONDecodeError:
                logger.warning(f"Failed to parse LLM response for Order ID {order_id}")
                # Fallback categorization
                unresolved_cases.append({
                    "order_id": order_id,
                    "original_comment": comment,
                    "resolution_summary": "Failed to parse LLM response",
                    "next_steps": "Manual review required",
                    "resolution_pattern": "Unknown",
                    "confidence": 0.0
                })
                
        except Exception as e:
            logger.error(f"Error processing Order ID {order_id}: {str(e)}")
            unresolved_cases.append({
                "order_id": order_id,
                "original_comment": comment,
                "resolution_summary": f"Error: {str(e)}",
                "next_steps": "Manual review required",
                "resolution_pattern": "Error",
                "confidence": 0.0
            })
    
    # Create output directories
    os.makedirs("output/resolved", exist_ok=True)
    os.makedirs("output/unresolved", exist_ok=True)
    os.makedirs("output/patterns", exist_ok=True)
    
    # Save resolved cases
    resolved_df = pd.DataFrame(resolved_cases)
    resolved_df.to_csv("output/resolved/resolved.csv", index=False)
    
    # Save unresolved cases
    unresolved_df = pd.DataFrame(unresolved_cases)
    unresolved_df.to_csv("output/unresolved/unresolved.csv", index=False)
    
    # Save next steps
    next_steps_df = pd.DataFrame(next_steps)
    next_steps_df.to_csv("output/unresolved/next_steps.csv", index=False)
    
    # Analyze and save resolution patterns
    pattern_analysis = analyze_resolution_patterns(resolution_patterns)
    with open("output/patterns/patterns.json", "w") as f:
        json.dump(pattern_analysis, f, indent=2)
    
    # Upload resolved data
    upload_file("output/resolved/resolved.csv", "output/")
    
    logger.info(f"Resolution complete: {len(resolved_cases)} resolved, {len(unresolved_cases)} unresolved")
    
    return {
        "resolved_count": len(resolved_cases),
        "unresolved_count": len(unresolved_cases),
        "resolved_path": "output/resolved/resolved.csv",
        "unresolved_path": "output/unresolved/unresolved.csv",
        "next_steps_path": "output/unresolved/next_steps.csv",
        "patterns_path": "output/patterns/patterns.json"
    }

def analyze_resolution_patterns(patterns: List[Dict]) -> Dict[str, Any]:
    """
    Analyze resolution patterns to identify common categories and insights.
    """
    pattern_counts = {}
    pattern_examples = {}
    
    for pattern_data in patterns:
        pattern = pattern_data["pattern"]
        if pattern not in pattern_counts:
            pattern_counts[pattern] = 0
            pattern_examples[pattern] = []
        
        pattern_counts[pattern] += 1
        pattern_examples[pattern].append({
            "order_id": pattern_data["order_id"],
            "summary": pattern_data["summary"]
        })
    
    # Sort by frequency
    sorted_patterns = sorted(pattern_counts.items(), key=lambda x: x[1], reverse=True)
    
    return {
        "total_resolved": len(patterns),
        "pattern_frequency": dict(sorted_patterns),
        "pattern_examples": pattern_examples,
        "top_patterns": [p[0] for p in sorted_patterns[:5]],
        "analysis_summary": f"Most common resolution pattern: {sorted_patterns[0][0] if sorted_patterns else 'None'}"
    }
