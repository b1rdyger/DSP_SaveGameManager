import logging
import os
import sys

from app.Engine import Engine


if __name__ == '__main__':
    script_dir = os.path.dirname(os.path.realpath(__file__)) + os.sep

    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s : %(message)s',
                        datefmt='%H:%M:%S', level=logging.INFO)

    logging.debug(f"Python version {str(sys.version)}")

    engine = Engine(script_dir)

