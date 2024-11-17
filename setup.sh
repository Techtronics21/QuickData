
#!/bin/bash

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
fi

# Activate virtual environment
source .venv/bin/activate

# Install requirements
pip3 install -r requirements.txt

# Print environment info
echo "Python version:"
python3 --version
echo "Virtual environment location:"
which python3