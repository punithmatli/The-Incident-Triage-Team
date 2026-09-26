# The-Incident-Triage-Team

Before running this, ensure your environment is set up by running the below command:
pip3 install --upgrade langgraph langchain-google-genai langchain-core

Create a virtual environment (Python3)
# 1. Create a virtual environment using your newly installed Python 3.12
python3.12 -m venv venv

# 2. Activate the environment (your terminal prompt will change to show '(venv)')
source venv/bin/activate

# 3. Install the Modern AI Stack
pip3 install --upgrade langgraph langchain-google-genai langchain-core

# 4. Export your API Key in venv
export GOOGLE_API_KEY="your-key-here"