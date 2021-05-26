import argparse
import json
import sys
from pprint import PrettyPrinter
from typing import List

from .browser import Browser
from .config import CONFIG_PATH
from .custom_logger import logger
from .services import RoomService, AliasService


class Executor:

    def __init__(self, commands=None):
        self.commands = commands if commands is not None else {
            'create': self.create_room,
            'connect': self.connect_to_room,
            'alias': self.new_alias,
            'get': self.get_room,
            'remove': self.remove_room,
            'rename': self.rename_room,
            'aliases': self.get_all_rooms,
            'get-config': self.get_config,
            'set-config': self.set_config,
            'set-name': self.set_default_name,
            'export': self.export_data,
        }
        self.alias_service = AliasService(CONFIG_PATH)
        self.room_service = RoomService(self.alias_service)
        self.browser = Browser()

    def create_room(self, args: List[str]):
        parser = argparse.ArgumentParser()
        parser.add_argument('-c', '--connect', action='store_true', help='Instantly connect to the room')
        parser.add_argument('-n', '--name', type=str, help='Name what will be displayed in the room')
        parser.add_argument('-a', '--alias', type=str, help='Add alias to the given')

        args = parser.parse_args(args)

        room_url = self.room_service.create_room(name=args.name)
        logger.info("Link: %s", room_url)
        if args.alias:
            self.alias_service.create(self.room_service.get_room_name(room_url), args.alias)
            logger.info("Saved alias: %s", args.alias)
        if args.connect:
            logger.info("Opening in browser...")
            self.browser.open_url(room_url)

    def new_alias(self, args: List[str]):
        parser = argparse.ArgumentParser()
        parser.add_argument('room', type=str, help='Link/UUID of the room')
        parser.add_argument('alias', type=str, help='Alias name')

        args = parser.parse_args(args)

        self.alias_service.create(self.room_service.get_room_name(args.room), args.alias)
        logger.info("Created a room %s with alias: %s", args.room, args.alias)

    def connect_to_room(self, args):
        parser = argparse.ArgumentParser()
        parser.add_argument('room', type=str, help='Link/UUID/Alias of the room')
        parser.add_argument('-n', '--name', type=str, help='Name what will be displayed in the room')

        args = parser.parse_args(args)

        room_url = self.room_service.get_room(args.room, name=args.name)
        logger.info("Connecting to the room: %s", room_url)
        self.browser.open_url(room_url)

    def get_room(self, args):
        parser = argparse.ArgumentParser()
        parser.add_argument('room', type=str, help='Link/UUID/Alias of the room')

        args = parser.parse_args(args)

        room_url = self.room_service.get_room(args.room)
        logger.info(room_url)

    def get_all_rooms(self, args):
        aliases = self.alias_service.get_all()
        if aliases:
            logger.info('All available aliases for the rooms:')
            for alias, room_id in aliases.items():
                logger.info("Alias name: %s with url %s", alias, self.room_service.get_room(room_id))
        else:
            logger.info('There are no aliases created yet')

    def get_config(self, args):
        parser = argparse.ArgumentParser()
        parser.add_argument('-p', '--pretty', action='store_true', help='Pretty print')

        args = parser.parse_args(args)

        config = self.alias_service.get_config()
        if args.pretty:
            printer = PrettyPrinter()
            logger.info(printer.pformat(config))
        else:
            logger.info(json.dumps(config))

    def set_config(self, args):
        parser = argparse.ArgumentParser()
        parser.add_argument('path', type=str, help='Path to new config')

        args = parser.parse_args(args)

        self.alias_service.set_config(args.path)
        logger.info('Successfully updated config')

    def set_default_name(self, args):
        parser = argparse.ArgumentParser()
        parser.add_argument('name', type=str, help='Name what will be set default for rooms')

        args = parser.parse_args(args)

        self.alias_service.set_name(args.name)
        logger.info('Successfully set name')

    def remove_room(self, args):
        parser = argparse.ArgumentParser()
        parser.add_argument('room', type=str, help='Alias of the room')

        args = parser.parse_args(args)

        self.alias_service.remove(args.room)
        logger.info("Room alias %s is removed", args.room)

    def rename_room(self, args):
        parser = argparse.ArgumentParser()
        parser.add_argument('old_alias', type=str, help='Old alias of the room')
        parser.add_argument('new_alias', type=str, help='New alias of the room')

        args = parser.parse_args(args)
        self.alias_service.rename(args.old_alias, args.new_alias)
        logger.info("Room alias %s is renamed to %s", args.old_alias, args.new_alias)

    def export_data(self, args):
        parser = argparse.ArgumentParser()
        parser.add_argument('room', type=str, help='UUID/Alias of the room')
        parser.add_argument('-p', '--path', type=str, help='Path to output file')

        args = parser.parse_args(args)

        data = self.room_service.get_export(args.room, args.path)

        logger.info("Exported data for the room %s: \n%s", args.room, data)

    def execute_from_command_line(self):
        parser = argparse.ArgumentParser()

        parser.add_argument('command', help='Command to execute', choices=(self.commands.keys()))

        args = parser.parse_args(sys.argv[1:2])

        # noinspection PyArgumentList
        self.commands[args.command](sys.argv[2:])
