import csv
import datetime
import json
import uuid
from typing import Optional, Dict
from urllib.parse import quote
from urllib.parse import urljoin

import requests

from .custom_logger import logger
from .utils import is_valid_uuid


class RoomService:
    DEFAULT_HOST = 'https://meetenjoy.herokuapp.com'

    def __init__(self, alias_service: 'AliasService', host=None):
        self.host = self.DEFAULT_HOST if host is None else host
        self.alias_service = alias_service

    def _build_url(self, room, name):
        if self.host in room:
            url = room
        else:
            if is_valid_uuid(room):
                url = urljoin(self.host, room)
            else:
                # trying to get uuid from alias
                room_uuid = self.alias_service.get_room_id(room)
                # case when we didn't find alias
                if room_uuid is None:
                    room_uuid = room
                url = urljoin(self.host, room_uuid)
        if name is not None:
            url += f'?name={quote(name)}'
        else:
            config_name = self.alias_service.get_name()
            if config_name:
                url += f'?name={quote(config_name)}'
        return url

    def create_room(self, name: str = None):
        room_uuid = str(uuid.uuid4())
        return self._build_url(room_uuid, name)

    def get_room(self, room_name: str, name=None):
        return self._build_url(room_name, name)

    def get_export(self, room: str, path: str = None):
        if not is_valid_uuid(room):
            room_uuid = self.alias_service.get_room_id(room)
            if room_uuid is None:
                room_uuid = room
            room = room_uuid
        response = requests.get(urljoin(self.DEFAULT_HOST, f'export/{room}'))
        # TODO export to file
        if not response.ok:
            return None

        data = response.json()
        output_data = []
        for socket_id, info in data.items():
            connected = datetime.datetime.fromtimestamp(info['connectedTime'] / 1000)
            disconnected = info['disconnectedTime']
            nickname = info['nickname']
            if disconnected is not None:
                disconnected = datetime.datetime.fromtimestamp(disconnected / 1000)
                was_in_call = disconnected - connected
            else:
                was_in_call = datetime.datetime.now() - connected
            if was_in_call.seconds <= 10:
                continue

            h, m, s = str(was_in_call).split(':')
            was_in_call = f'{h} hours, {m} minutes, {int(float(s))} seconds'

            output_data.append({
                'nickname': nickname,
                'connected': connected.strftime('%d/%m/%Y, %H:%M:%S'),
                'disconnected': disconnected.strftime('%d/%m/%Y, %H:%M:%S') if disconnected is not None else None,
                'was_in_call': was_in_call,
            })
        if path:
            logger.info("Exporting data to the file: %s", path)
            with open(path, 'w') as f:
                writer = csv.writer(f)
                columns = ['nickname', 'connected', 'disconnected', 'was_in_call']
                writer.writerow(columns)
                for row in output_data:
                    writer.writerow([row[col] for col in columns])
        return output_data

    def get_room_name(self, room_name: str):
        if self.host in room_name:
            endpoint = room_name[len(self.host) + 1:]
            if '?name' in endpoint:
                endpoint = endpoint.split('?name')[0]
            return endpoint
        return room_name


class Config:

    def __init__(self, path, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.config = {}
        self.config_path = path
        self.update_config_from_file(path)
        self.store_config()

    def store_config(self):
        with open(self.config_path, 'w') as f:
            json.dump(self.config, f)

    def update_config_from_file(self, config_path):
        with open(config_path) as f:
            try:
                config = json.load(f)
            except json.decoder.JSONDecodeError:
                logger.info('Given file is empty, updating it')
                config = {}
        config.setdefault('name', '')
        config.setdefault('aliases', {})
        self.config = config


class AliasService:

    def __init__(self, config_path: str) -> None:
        self._config = Config(config_path)

    def create(self, room_id: str, alias_name: str) -> None:
        self._config.config['aliases'][alias_name] = room_id
        self._config.store_config()

    def get_room_id(self, alias_name: str) -> Optional[str]:
        return self._config.config['aliases'].get(alias_name)

    def rename(self, old_alias_name: str, new_alias_name: str) -> None:
        if old_alias_name not in self._config.config['aliases']:
            return
        room_id = self._config.config['aliases'][old_alias_name]
        del self._config.config['aliases'][old_alias_name]
        self._config.config['aliases'][new_alias_name] = room_id
        self._config.store_config()

    def remove(self, alias_name: str) -> None:
        if alias_name not in self._config.config['aliases']:
            return
        del self._config.config['aliases'][alias_name]
        self._config.store_config()

    def get_all(self) -> Dict[str, str]:
        return self._config.config['aliases']

    def get_name(self) -> str:
        return self._config.config['name']

    def set_name(self, name) -> None:
        self._config.config['name'] = name
        self._config.store_config()

    def get_config(self):
        return dict(self._config.config)

    def set_config(self, config_path: str) -> None:
        self._config.update_config_from_file(config_path)
        self._config.store_config()
