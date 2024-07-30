import subprocess
import sys

# Path to your Streamlit app
streamlit_app_path = 'heart_disease_app.py'

# Command to run Streamlit app
subprocess.run([sys.executable, '-m', 'streamlit', 'run', streamlit_app_path])
