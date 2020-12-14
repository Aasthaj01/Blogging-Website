#!C:\Users\luhad\PycharmProjects\Flask_tutorial\venv\Scripts\python.exe
# EASY-INSTALL-ENTRY-SCRIPT: 'secret-python3==0.8','console_scripts','secret'
__requires__ = 'secret-python3==0.8'
import re
import sys
from pkg_resources import load_entry_point

if __name__ == '__main__':
    sys.argv[0] = re.sub(r'(-script\.pyw?|\.exe)?$', '', sys.argv[0])
    sys.exit(
        load_entry_point('secret-python3==0.8', 'console_scripts', 'secret')()
    )
