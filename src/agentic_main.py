"""
agentic_main.py
Entry point for running the ZenStatement agentic reconciliation framework.
"""

import os
import sys
from dotenv import load_dotenv
from loguru import logger

# Add src directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.agent import create_agent, run_agent_workflow
from src.utils import setup_logging, load_config

def main():
    """
    Loads config, instantiates the agent, and runs the end-to-end workflow.
    """
    # Setup logging
    setup_logging()
    logger.info("Starting ZenStatement Agentic Reconciliation Framework...")
    
    # Load configuration
    config = load_config()
    
    # Check for required environment variables
    if not config.get("GROQ_API_KEY"):
        logger.error("GROQ_API_KEY not found in environment variables")
        logger.info("Please add your Groq API key to the .env file")
        sys.exit(1)
    
    # Store the dataset in 'data' folder
    input_data_path = "data/your_dataset_name.csv"  
    comments_data_path = "data/your_dataset_name.csv"
    
    if not os.path.exists(input_data_path):
        logger.error(f"Input data file not found: {input_data_path}")
        logger.info("Please place your transaction data CSV in the data/ directory")
        sys.exit(1)
    
    if not os.path.exists(comments_data_path):
        logger.error(f"Comments data file not found: {comments_data_path}")
        logger.info("Please place your comments data CSV in the data/ directory")
        sys.exit(1)
    
    try:
        # Create agent
        logger.info("Initializing agent...")
        agent = create_agent()
        
        # Run the workflow
        logger.info("Starting agent workflow...")
        result = run_agent_workflow(agent, input_data_path, comments_data_path)
        
        logger.info("Agent workflow completed successfully!")
        logger.info(f"Result: {result}")
        
        # Log output file locations
        logger.info("Output files generated:")
        logger.info("- output/discrepancies/ (filtered transaction discrepancies)")
        logger.info("- output/resolved/ (resolved cases)")
        logger.info("- output/unresolved/ (unresolved cases and next steps)")
        logger.info("- output/patterns/ (resolution pattern analysis)")
        
    except Exception as e:
        logger.error(f"Error during agent execution: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
