import os

from app.Engine import Engine

if __name__ == '__main__':
    script_dir = os.path.dirname(os.path.realpath(__file__)) + os.sep
    engine = Engine(script_dir)
