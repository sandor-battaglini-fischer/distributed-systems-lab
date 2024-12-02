#!/usr/bin/env python3

import os
import sys
import logging
import traceback
from datetime import datetime
import importlib.util
import subprocess

# Set up logging
log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
os.makedirs(log_dir, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(log_dir, 'incident_scrapers.log')),
        logging.StreamHandler(sys.stdout)
    ]
)

def import_module_from_file(file_path):
    """Import a module from file path."""
    try:
        spec = importlib.util.spec_from_file_location("module", file_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    except Exception as e:
        logging.error(f"Failed to import module from {file_path}: {str(e)}")
        return None

def run_stability_scraper():
    """Run the StabilityAI scraper."""
    logging.info("Starting StabilityAI scraper...")
    
    try:
        # Get the path to StabilityAI.py
        stability_path = os.path.join(
            os.path.dirname(__file__),
            "data_gen_modules",
            "StabilityAI.py"
        )
        
        # Run the script as a subprocess to ensure clean execution
        result = subprocess.run(
            [sys.executable, stability_path],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            logging.info("StabilityAI scraper completed successfully")
            if result.stdout:
                logging.info("Output: " + result.stdout)
            return True
        else:
            logging.error("StabilityAI scraper failed")
            if result.stderr:
                logging.error("Error: " + result.stderr)
            return False
            
    except Exception as e:
        logging.error(f"Error running StabilityAI scraper: {str(e)}")
        logging.error(traceback.format_exc())
        return False

def run_oac_scraper():
    """Run the OpenAI/Anthropic/Character.AI scraper."""
    logging.info("Starting OAC scraper...")
    
    try:
        # Get the path to incident_scraper_oac.py
        oac_path = os.path.join(
            os.path.dirname(__file__),
            "data_gen_modules",
            "incident_scraper_oac.py"
        )
        
        # Run the script as a subprocess to ensure clean execution
        result = subprocess.run(
            [sys.executable, oac_path],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            logging.info("OAC scraper completed successfully")
            if result.stdout:
                logging.info("Output: " + result.stdout)
            return True
        else:
            logging.error("OAC scraper failed")
            if result.stderr:
                logging.error("Error: " + result.stderr)
            return False
            
    except Exception as e:
        logging.error(f"Error running OAC scraper: {str(e)}")
        logging.error(traceback.format_exc())
        return False

def main():
    start_time = datetime.now()
    logging.info(f"Starting incident scraper run at {start_time}")
    
    try:
        # Run StabilityAI scraper first
        stability_success = run_stability_scraper()
        
        if stability_success:
            logging.info("StabilityAI scraper completed successfully, proceeding with OAC scraper")
            
            # Run OAC scraper next
            oac_success = run_oac_scraper()
            
            if oac_success:
                logging.info("All scrapers completed successfully")
            else:
                logging.error("OAC scraper failed")
        else:
            logging.error("StabilityAI scraper failed, skipping OAC scraper")
        
    except Exception as e:
        logging.error(f"Error in main execution: {str(e)}")
        logging.error(traceback.format_exc())
    
    end_time = datetime.now()
    duration = end_time - start_time
    logging.info(f"Scraper run completed at {end_time} (Duration: {duration})")

if __name__ == "__main__":
    main() 