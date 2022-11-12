import os
import json

from app.Engine import Engine
from app.SaveGameManager import SaveGameWindow

if __name__ == '__main__':
    script_dir = os.path.dirname(os.path.realpath(__file__)) + os.sep
    engine = Engine(script_dir)
