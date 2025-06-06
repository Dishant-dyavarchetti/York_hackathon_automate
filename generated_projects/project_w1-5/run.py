import os
import subprocess

# Create virtual environment
subprocess.run(['python', '-m', 'venv', 'env'])

# Activate virtual environment
if os.name == 'nt':
    subprocess.run(['env\Scripts\activate'])
else:
    subprocess.run(['source', 'env/bin/activate'])

# Install requirements
subprocess.run(['pip', 'install', '-r', 'requirements.txt'])

# Run the app
subprocess.run(['python', 'src/main.py'])