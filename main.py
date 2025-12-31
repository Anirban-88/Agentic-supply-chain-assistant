

import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import subprocess
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def run_streamlit():
    """Run the Streamlit app"""
    logger.info("🚀 Starting Store Supply Chain Assistant...")
    
    streamlit_script = os.path.join(os.path.dirname(__file__), 'ui', 'streamlit_app.py')
    
    subprocess.run([
        'streamlit', 'run', streamlit_script,
        '--server.port', '8501',
        '--server.address', 'localhost',
        '--browser.gatherUsageStats', 'false'
    ])

if __name__ == "__main__":
    try:
        run_streamlit()
    except KeyboardInterrupt:
        logger.info("\n👋 Shutting down...")
    except Exception as e:
        logger.error(f"❌ Error: {e}")