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
    parser.add_argument('--online', help='Online mode', required=False, action=argparse.BooleanOptionalAction, default=True, dest='online')
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

    # режим работы с данными: online - загрузка из сети, offline - загрузка из кеша
    offline_mode: bool = args.offline
    if not offline_mode:
        offline_mode: bool = not args.online

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
        offline_mode=offline_mode)

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
        offline_mode=offline_mode)

    authz = esi_interface.authenticate(args.pilot, q_settings.g_esi_client_id)
    character_id = authz["character_id"]
    character_name = authz["character_name"]

    # Public information about a character
    character_data = esi_interface.get_esi_data(
        url=f"characters/{character_id}/",
        fully_trust_cache=True)
    # Public information about a corporation
    corporation_data = esi_interface.get_esi_data(
        url=f"corporations/{character_data['corporation_id']}/",
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

    unrelated_killmails = qzm.get_unrelated_killmails()
    print(f"'{corporation_name}' corporation has {len(unrelated_killmails)} unrelated killmails\n")
    sys.stdout.flush()

    if unrelated_killmails:
        for killmail_id, killmail_hash in unrelated_killmails:
            # Public information
            killmail_data = esi_interface.get_esi_data(f"killmails/{killmail_id}/{killmail_hash}/")
            sys.stdout.flush()

            alliances: typing.Set[int] = set()
            corporations: typing.Set[int] = set()
            characters: typing.Set[int] = set()
            type_ids: typing.Set[int] = set()
            solar_system_id: int = int(killmail_data['solar_system_id'])

            victim: typing.Dict[str, typing.Any] = killmail_data['victim']
            if 'alliance_id' in victim:
                alliances.add(victim['alliance_id'])
            if 'corporation_id' in victim:
                corporations.add(victim['corporation_id'])
            if 'character_id' in victim:
                characters.add(victim['character_id'])
            type_ids.add(victim['ship_type_id'])

            attackers: typing.List[typing.Dict[str, typing.Any]] = killmail_data['attackers']
            for a in attackers:
                if 'alliance_id' in a:
                    alliances.add(a['alliance_id'])
                if 'corporation_id' in a:
                    corporations.add(a['corporation_id'])
                if 'character_id' in a:
                    characters.add(a['character_id'])
                if 'ship_type_id' in a:
                    type_ids.add(a['ship_type_id'])

            if alliances:
                alliances: typing.List[int] = qzm.get_absent_alliance_ids(alliances)
                for alliance_id in alliances:
                    # Public information about an alliance
                    alliance_data = esi_interface.get_esi_data(
                        url=f"alliances/{alliance_id}/",
                        fully_trust_cache=True)
                    sys.stdout.flush()

                    if alliance_data:
                        qzm.insert_or_update_alliance(alliance_id, alliance_data, at)

            if corporations:
                corporations: typing.List[int] = qzm.get_absent_corporation_ids(corporations)
                for corporation_id in corporations:
                    # Public information about a corporation
                    corporation_data = esi_interface.get_esi_data(
                        url=f"corporations/{corporation_id}/",
                        fully_trust_cache=True)
                    sys.stdout.flush()

                    if corporation_data:
                        qzm.insert_or_update_corporation(corporation_id, corporation_data, at)

            if characters:
                characters: typing.List[int] = qzm.get_absent_character_ids(characters)
                for character_id in characters:
                    # Public information about a character
                    character_data = esi_interface.get_esi_data(
                        url=f"characters/{character_id}/",
                        fully_trust_cache=True)
                    sys.stdout.flush()

                    if character_data:
                        qzm.insert_or_update_character(character_id, character_data, at)

            if type_ids:
                type_ids: typing.List[int] = qzm.get_absent_type_ids(type_ids)
                for type_id in type_ids:
                    # Public information about a type_id
                    type_data = esi_interface.get_esi_data(
                        url=f"universe/types/{type_id}/",
                        fully_trust_cache=True)
                    sys.stdout.flush()

                    if type_data:
                        qzm.insert_or_update_type_id(type_id, type_data, at)

            if qzm.get_absent_system_ids({solar_system_id}):
                # Public information about a solar system
                system_data = esi_interface.get_esi_data(
                    url=f"universe/systems/{solar_system_id}/",
                    fully_trust_cache=True)
                sys.stdout.flush()

                if system_data:
                    qzm.insert_or_update_system(solar_system_id, system_data, at)

                    constellation_id: int = system_data['constellation_id']
                    if qzm.get_absent_constellation_ids({constellation_id}):
                        # Public information about a constellation
                        constellation_data = esi_interface.get_esi_data(
                            url=f"universe/constellations/{constellation_id}/",
                            fully_trust_cache=True)
                        sys.stdout.flush()

                        if constellation_data:
                            qzm.insert_or_update_constellation(constellation_id, constellation_data, at)

                            region_id: int = constellation_data['region_id']
                            if qzm.get_absent_region_ids({region_id}):
                                # Public information about a region
                                region_data = esi_interface.get_esi_data(
                                    url=f"universe/regions/{region_id}/",
                                    fully_trust_cache=True)
                                sys.stdout.flush()

                                if region_data:
                                    qzm.insert_or_update_region(region_id, region_data, at)

            qzm.insert_into_killmails(killmail_id, killmail_data)
            qzm.mark_killmail_as_need_refresh(killmail_id)
            qzdb.commit()

            print(f"New killmail {killmail_id} with {len(killmail_data['attackers'])} attackers and {killmail_data['victim'].get('character_id')} victim\n")
            sys.stdout.flush()

        qzm.mark_all_killmails_as_published_if_none()
        qzdb.commit()

    del qzm
    qzdb.disconnect()
    del qzdb


if __name__ == "__main__":
    # mem = memory_usage(main, max_usage=True)
    # print("Memory used: {}Mb".format(mem))
    main()
    exit(0)

