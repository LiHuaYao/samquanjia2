import sys
import os
from threading import Thread
from init import Init
import os

sys.path.append('./')

if __name__ == '__main__':
    init_thread = Thread(target=Init.window)
    init_thread.start()
    os.system(os.getenv('PY_NAME', 'python3') + " ./controller/app.py ")