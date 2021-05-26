import os
from pathlib import Path

from appdirs import user_config_dir

from .custom_logger import logger

CONFIG_FOLDER = Path(user_config_dir('meetenjoy'))
CONFIG_PATH = CONFIG_FOLDER / 'config.json'

Path(CONFIG_FOLDER).mkdir(parents=True, exist_ok=True)
if not os.path.exists(CONFIG_PATH):
    logger.info('Creating config %s', CONFIG_PATH)
    with open(CONFIG_PATH, 'w') as f:
        f.write('{}')

__all__ = [CONFIG_FOLDER, CONFIG_PATH]
