""" Q.Loader (desktop/mobile)

Prerequisites:
    * Have a Python 3 environment available to you (possibly by using a
      virtual environment: https://virtualenv.pypa.io/en/stable/).
    * Run pip install -r requirements.txt --user with this directory.
      or
      Run pip install -r requirements.txt with this directory as your root.

    * Copy q_settings.py.template into q_settings.py and mood for your needs.
    * Create an SSO application at developers.eveonline.com with the scopes
      from g_client_scope list declared in q_settings.py and the
      callback URL "https://localhost/callback/".
      Note: never use localhost as a callback in released applications.

To run this example, make sure you have completed the prerequisites and then
run the following command from this directory:

$ chcp 65001 & @rem on Windows only!
$ python q_loader.py --pilot="Qandra Si" --online --cache_dir=~/.q_zkbot

Required application scopes:
    * public access
"""
import sys
import argparse
import typing
import datetime

import q_settings
import eve_esi_interface as esi
import zkillboard_interface as zkb
import postgresql_interface as db

from __init__ import __version__


def main():
    parser = argparse.ArgumentParser(description='launching server for loading killmails')
    parser.add_argument('--pilot', help='Pilot name', required=True, dest='pilot')
    parser.add_argument('--cache_dir', help='Cache dir', required=False, default='.q_zkbot', dest='cache_dir')
    parser.add_argument('--offline', help='Offline mode', required=False, action=argparse.BooleanOptionalAction, default=False, dest='offline')
    parser.add_argument('-v', '--verbose', help='Verbose mode', action=argparse.BooleanOptionalAction, default=False, dest='verbose')
    parser.add_argument('--verbosity', help='Verbose mode level', required=False, dest='verbosity')
    args = parser.parse_args()

    print(f"Running loader v{__version__}")

    # уровень журнализации: 1 = INFO, 2 = DETAILS, 3 = DEBUG
    verbosity_level: typing.Optional[int] = None
    if args.verbosity:
        verbosity_level = int(args.verbosity)
    elif args.verbose:
        verbosity_level = 1

    # получение информации о текущем времени
    at: datetime.datetime = datetime.datetime.now(datetime.UTC)
    # подключение к БД
    qzdb: db.QZKBotDatabase = db.QZKBotDatabase(debug=verbosity_level == 3)
    qzdb.connect(q_settings.g_database)
    qzm: db.QZKBotMethods = db.QZKBotMethods(qzdb)

    # настройка ZKillboard interface
    zkb_client = zkb.ZKillboardClient(
        keep_alive=True,
        debug=verbosity_level == 3,
        logger=True,
        user_agent='Q.ZKBot/{ver}'.format(ver=__version__),
        restrict_tls13=q_settings.g_client_restrict_tls13)
    zkb_interface = zkb.ZKillboardInterface(
        client=zkb_client,
        cache_dir=f'{args.cache_dir}/zkb_cache',
        offline_mode=args.offline)

    # настройка Eve Online ESI Swagger interface
    auth = esi.EveESIAuth(
        cache_dir=f'{args.cache_dir}/auth_cache',
        debug=verbosity_level is not None)
    esi_client = esi.EveESIClient(
        auth_cache=auth,
        client_id=q_settings.g_esi_client_id,
        keep_alive=True,
        debug=verbosity_level == 3,
        logger=True,
        user_agent='Q.ZKBot/{ver}'.format(ver=__version__),
        restrict_tls13=q_settings.g_client_restrict_tls13)
    esi_interface = esi.EveOnlineInterface(
        client=esi_client,
        scopes=q_settings.g_esi_client_scope,
        cache_dir=f'{args.cache_dir}/esi_cache',
        offline_mode=args.offline)

    authz = esi_interface.authenticate(args.pilot, q_settings.g_esi_client_id)
    character_id = authz["character_id"]
    character_name = authz["character_name"]

    # Public information about a character
    character_data = esi_interface.get_esi_data(
        url=f"characters/{character_id}/",
        fully_trust_cache=True)
    # Public information about a corporation
    corporation_data = esi_interface.get_esi_data(
        url=f"corporations/{character_data["corporation_id"]}/",
        fully_trust_cache=True)

    corporation_id = character_data["corporation_id"]
    corporation_name = corporation_data["name"]
    print(f"{character_name} is from '{corporation_name}' corporation\n")
    sys.stdout.flush()

    # Requires role(s): Director
    corp_killmails_data = esi_interface.get_esi_paged_data(f"corporations/{corporation_id}/killmails/recent/")
    print(f"'{corporation_name}' corporation has {len(corp_killmails_data)} recent killmails\n")
    sys.stdout.flush()

    for zkm in corp_killmails_data:
        qzm.insert_into_zkillmails_hash_only(zkm, esi_interface.last_modified if esi_interface.last_modified else at)
    qzdb.commit()

    # Public information (zkillboard)
    corp_zkillmails_data = zkb_interface.get_zkb_data(f"corporationID/{corporation_id}/")
    print(f"'{corporation_name}' corporation has {len(corp_zkillmails_data)} zkillmails\n")
    sys.stdout.flush()

    for zkm in corp_zkillmails_data:
        qzm.insert_into_zkillmails(zkm, zkb_interface.last_modified if zkb_interface.last_modified else at)
    qzdb.commit()

    del qzm
    qzdb.disconnect()
    del qzdb


if __name__ == "__main__":
    # mem = memory_usage(main, max_usage=True)
    # print("Memory used: {}Mb".format(mem))
    main()
    exit(0)

