import os
import configparser
from pathlib import Path
from typing import Any, Optional


class Config:
    def __init__(self, cfg_path: Path, prefix: Optional[str]=''):
        self._cfg_path = cfg_path
        self._prefix = prefix
        self._params = self._load_config()

    def _load_config(self) -> dict:
        cfg_parser = configparser.ConfigParser()
        cfg_parser.read(self._cfg_path)

        config = {}
        for section in cfg_parser.sections():
            for k, v in cfg_parser.items(section):
                var_name = f'{self._prefix}_{section}_{k}'
                config[var_name] = os.getenv(var_name, v)

        return config
    
    def __getitem__(self, key: Any):
        return self._params[key]


config = Config(
    cfg_path=Path(Path(__file__).resolve().parents[1],'config', 'bot.ini'), 
    prefix='way_bill'
)
