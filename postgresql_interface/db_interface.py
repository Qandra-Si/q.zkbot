# -*- encoding: utf-8 -*-
import sys
import json
import typing
import psycopg2
from sshtunnel import SSHTunnelForwarder


class QZKBotDatabase:
    def __init__(self,
                 settings: typing.Optional[typing.Dict[str, typing.Union[str, typing.Dict[str, str]]]] = None,
                 debug: bool = False):
        """ constructor

        :param connection settings: dbname, user, password, host, port
        :param debug: flag which says that we are in debug mode
        """
        self.__settings: typing.Optional[typing.Dict[str, typing.Union[str, typing.Dict[str, str]]]] = settings
        self.__debug: bool = debug
        self.__ssh_tunnel: typing.Optional[SSHTunnelForwarder] = None
        self.__conn = None

    def __del__(self):
        """ destructor
        """
        self.disconnect()

    @property
    def settings(self) -> typing.Optional[typing.Dict[str, typing.Union[str, typing.Dict[str, str]]]]:
        """ connection settings: dbname, user, password, host, port
        """
        return self.__settings

    @property
    def debug(self) -> bool:
        """ flag which says that we are in debug mode
        """
        return self.__debug

    def enable_debug(self) -> None:
        self.__debug = True

    def disable_debug(self) -> None:
        self.__debug = False

    def connect(self, settings: typing.Optional[typing.Dict[str, typing.Union[str, typing.Dict[str, str]]]] = None):
        """ connects to the database with specified settings and discover module id parameter
        """
        if not (settings is None):
            self.__settings = settings

        try:
            self.disconnect()
            if "ssh_tunnel" in self.settings:
                self.__ssh_tunnel = SSHTunnelForwarder(
                    (self.settings["ssh_tunnel"]["host"], self.settings["ssh_tunnel"]["port"]),
                    ssh_username=self.settings["ssh_tunnel"]["username"],
                    ssh_private_key=self.settings["ssh_tunnel"]["private_key"],
                    ssh_password=self.settings["ssh_tunnel"]["password"],
                    remote_bind_address=(self.settings["host"], self.settings["port"])
                )
                self.__ssh_tunnel.start()
                self.__conn = psycopg2.connect(
                    dbname=self.settings["dbname"],
                    user=self.settings["user"],
                    password=self.settings["password"],
                    host="localhost",
                    port=self.__ssh_tunnel.local_bind_port
                )
            else:
                self.__conn = psycopg2.connect(
                    dbname=self.settings["dbname"],
                    user=self.settings["user"],
                    password=self.settings["password"],
                    host=self.settings["host"],
                    port=self.settings["port"]
                )
            self.execute("SET search_path TO qz")
        except psycopg2.DatabaseError as e:
            print(f"Error {e}")
            print(sys.exc_info())
            raise e

    def disconnect(self):
        if self.__conn is not None:
            with self.__conn as conn:
                if not conn.cursor().closed:
                    conn.cursor().close()
                if self.debug and (conn.closed != 0):
                    print('Error on closing database connection: code={}'.format(conn.closed))
                if self.__ssh_tunnel is None:
                    conn.cancel()
            del self.__conn
            self.__conn = None
        if self.__ssh_tunnel is not None:
            self.__ssh_tunnel.stop()
            del self.__ssh_tunnel
            self.__ssh_tunnel = None

    def commit(self) -> None:
        self.__conn.commit()

    def rollback(self) -> None:
        self.__conn.rollback()

    def select_one_row(self, query, *args):
        with self.__conn.cursor() as cur:
            if isinstance(args, tuple) and (len(args) == 1) and isinstance(args[0], dict):
                cur.execute(query, args[0])
            else:
                cur.execute(query, args)
            if self.debug:
                print(cur.query)
            records = cur.fetchone()
            cur.close()
            return records

    def select_many_rows(self, fetch_size, query, *args):
        with self.__conn.cursor() as cur:
            if isinstance(args, tuple) and (len(args) == 1) and isinstance(args[0], dict):
                cur.execute(query, args[0])
            else:
                cur.execute(query, args)
            if self.debug:
                print(cur.query)
            records = cur.fetchmany(fetch_size)
            cur.close()
            return records

    def select_all_rows(self, query, *args):
        with self.__conn.cursor() as cur:
            if isinstance(args, tuple) and (len(args) == 1) and isinstance(args[0], dict):
                cur.execute(query, args[0])
            else:
                cur.execute(query, args)
            if self.debug:
                print(cur.query)
            records = cur.fetchall()
            cur.close()
            return records

    def execute(self, query, *args):
        with self.__conn.cursor() as cur:
            if isinstance(args, tuple) and (len(args) == 1) and isinstance(args[0], dict):
                cur.execute(query, args[0])
            else:
                cur.execute(query, args)
            if self.debug:
                print(cur.query)
            cur.close()
            # if self.debug:
            #     print(f"{cur.rowcount} rows affected.")
