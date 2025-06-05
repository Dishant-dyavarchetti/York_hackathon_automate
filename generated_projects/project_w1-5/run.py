import os
import sys
from subprocess import run

if __name__ == '__main__':
    try:
        run(['python', '-m', 'venv', 'env'])
        run(['env\Scripts\activate'], shell=True)
        run(['pip', 'install', '-r', 'requirements.txt'])
        run(['python', 'src/main.py'])
    except Exception as e:
        print(e)
        sys.exit(1)