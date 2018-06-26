from pathlib import Path
import os

BOARD = 1
IN = 2
OUT = 3
HIGH = 1
LOW = 0

def setup(port, status):
    print('setup')

def setwarnings(bool):
    print('setWarnings')

def setmode(status):
    print('setmode')

def output(port, status):
    if (status == HIGH):
        f = open(str(port), "w+")
        f.close()
    else:
        arquivo = Path(str(port))
        if (arquivo.is_file()):
            os.remove(str(port))

def input(port):
    arquivo = os.path.isfile(str(port))
    if arquivo:
        return 1
    else:
        return 0