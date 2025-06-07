import os
import sys
import subprocess

try:
    subprocess.run(['python', '-m', 'venv', 'venv'])
except FileNotFoundError:
    print('You need to have Python installed to run this script.')
    sys.exit(1)

try:
    subprocess.run(['venv\Scripts\activate' if os.name == 'nt' else 'source venv/bin/activate'], shell=True)
except FileNotFoundError:
    print('You need to have Python installed to run this script.')
    sys.exit(1)

try:
    subprocess.run(['pip', 'install', '-r', 'requirements.txt'])
except FileNotFoundError:
    print('You need to have pip installed to run this script.')
    sys.exit(1)

try:
    subprocess.run(['python', 'src/main.py'])
except FileNotFoundError:
    print('You need to have Python installed to run this script.')
    sys.exit(1)