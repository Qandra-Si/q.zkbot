﻿import typing
import json
import discord

import q_settings


class FormattedDiscordMessage:
    def __init__(self,
                 killmail_id: int,
                 killmail_data: typing.Dict[str, typing.Any],
                 killmail_attackers: typing.Dict[str, typing.Any],
                 tracked_corporation_ids: typing.List[int]):
        self.contents: typing.Optional[str] = None
        self.embed: typing.Optional[discord.Embed] = None
        self.__killmail_id: int = killmail_id
        self.__killmail_data: typing.Dict[str, typing.Any] = killmail_data
        self.__killmail_attackers: typing.Dict[str, typing.Any] = killmail_attackers
        self.format(tracked_corporation_ids)

    def format(self, tracked_corporation_ids: typing.List[int]) -> None:
        attacker_corps: typing.List[typing.Dict[str, typing.Any]] = self.__killmail_attackers['corporations']
        attacker_alli: typing.List[typing.Dict[str, typing.Any]] = self.__killmail_attackers['alliances']
        attacker_solo: typing.Optional[typing.Dict[str, typing.Any]] = self.__killmail_attackers['solo']
        zkb: typing.Dict[str, typing.Any] = self.__killmail_data['zkb']
        solar_system: typing.Dict[str, typing.Any] = self.__killmail_data['solar_system']
        victim: typing.Dict[str, typing.Any] = self.__killmail_data['victim']
        final_blow: typing.Dict[str, typing.Any] = self.__killmail_data['final_blow']

        loss: bool = victim.get('corporation_id', 0) in tracked_corporation_ids
        attacker_pilots_qty: int = 0 if not attacker_corps else sum([_['pilots'] for _ in attacker_corps])
        solo: bool = attacker_pilots_qty == 1
        final_character_id: typing.Optional[int] = final_blow.get('id')
        final_ship_name: typing.Optional[int] = final_blow.get('ship')

        # Внимание!
        #  * solo выставляется, если атакующий пилот был один (непись не учитывается)
        #  * final_blow-пилот может быть неписью
        #  * solo_attacker-пилот не является неписью

        # см. про расположение элементов в embed-е тут: https://guide.disnake.dev/popular-topics/embeds
        if solo and attacker_solo:
            solo_attacker_id: int = attacker_solo.get('character_id')
            solo_attacker_name: str = attacker_solo.get('character_name', str(solo_attacker_id))
            # Бой был выигран в соло пилотом Qandra Si
            attackers_txt: str = \
                f"Бой был выигран в соло пилотом" \
                f" [{solo_attacker_name}](https://zkillboard.com/character/{solo_attacker_id}/)"
            solo_ship_name: int = attacker_solo.get('ship_name')
            if solo_ship_name:
                # Бой был выигран в соло пилотом Qandra Si на Tristan
                attackers_txt += f" на **{solo_ship_name}**"
        else:
            attackers_txt: str = "Его добил"
            if final_character_id:
                # Его добил Qandra Si
                final_character_name: str = final_blow.get('name', str(final_character_id))
                attackers_txt += f" [{final_character_name}](https://zkillboard.com/character/{final_character_id}/)"
            if final_ship_name:
                if final_character_id is not None:
                    # Его добил Qandra Si на Tristan
                    attackers_txt += f" на **{final_ship_name}**"
                else:
                    # Его добил Tristan
                    attackers_txt += f" **{final_ship_name}**"
        attackers_txt += "."

        if attacker_pilots_qty >= 2:
            attackers_txt += f"\nАтакующие: {attacker_pilots_qty}"
            attacker_corps_len: int = len(attacker_corps)
            if attacker_corps_len == 1:
                corp: typing.Dict[str, typing.Optional[int]] = attacker_corps[0]
                corporation_id: int = corp['id']
                if attacker_alli and corporation_id not in q_settings.q_tracked_corporations:
                    # Атакующие: (2) из Ragequit Cancel Sub
                    alli: typing.Dict[str, typing.Optional[int]] = attacker_alli[0]
                    alliance_id: int = alli['id']
                    alliance_name: str = alli.get('name', str(alliance_id))
                    attackers_txt += f" из [{alliance_name}](https://zkillboard.com/alliance/{alliance_id}/)"
                else:
                    # Атакующие: (2) из Warriors tribe
                    corporation_name: str = corp.get('name', str(corporation_id))
                    attackers_txt += f" из [{corporation_name}](https://zkillboard.com/corporation/{corporation_id}/)"
            elif attacker_corps_len >= 2:
                attacker_corps.sort(key=lambda _: _['pilots'], reverse=True)
                if not attacker_alli:
                    # если нет атакующих альянсов, то работаем лишь только со списком
                    # корпораций, в котором 2 или более элемента
                    pilots0: int = attacker_corps[0]['pilots']
                    pilots1: int = attacker_corps[1]['pilots']
                    if pilots0 > pilots1:
                        # Атакующие: (5), основная группа из Warriors tribe
                        corp: typing.Dict[str, typing.Any] = attacker_corps[0]
                        corporation_id: int = corp['id']
                        corporation_name: str = corp.get('name', str(corporation_id))
                        attackers_txt += \
                            ", основная группа из " \
                            f"[{corporation_name}](https://zkillboard.com/corporation/{corporation_id}/) " \
                            f"({pilots0})"
                    elif pilots0 > 1 and pilots0 == pilots1:
                        num: int = 2
                        while num < attacker_corps_len:
                            if pilots0 != attacker_corps[num]['pilots']:
                                break
                            num += 1
                        if num <= 3:
                            if num == attacker_corps_len:
                                # Атакующие: (6) группы из Warriors tribe (2), R Initiative (2), Phoenix Tag. (2)
                                attackers_txt += " группы из "
                            else:
                                # Атакующие: (6), основные группы из Warriors tribe (2), R Initiative (2), Phoenix Tag. (2)
                                attackers_txt += ", основные группы из "
                            for i in range(num):
                                corp: typing.Dict[str, typing.Any] = attacker_corps[i]
                                corporation_id: int = corp['id']
                                corporation_name: str = corp.get('name', str(corporation_id))
                                attackers_txt += \
                                    (", " if i else "") + \
                                    f"[{corporation_name}](https://zkillboard.com/corporation/{corporation_id}/) " \
                                    f"({pilots0})"
                else:
                    # если есть атакующие альянсы, то работать придётся с двумя списками, в каждом из которых может
                    # быть различная ситуация по накопленным данным, поэтому ищем паттерны
                    ordered_groups: typing.List[typing.Tuple[str, typing.Dict[str, typing.Optional[int]]]] = \
                        [('c', _) for _ in attacker_corps if _['alli'] is None] + \
                        [('a', _) for _ in attacker_alli]
                    # суммарно в объединённом списке может быть меньше 2х элементов (2 корпы из одного альянса удалятся)
                    if len(ordered_groups) == 1:
                        # Атакующие: (2) из C A M E L O T
                        grp: typing.Dict[str, typing.Optional[int]] = ordered_groups[0][1]
                        group_id: int = grp['id']
                        group_name: str = grp.get('name', str(group_id))
                        attackers_txt += f" из [{group_name}](https://zkillboard.com/alliance/{group_id}/)"
                    else:
                        ordered_groups.sort(key=lambda _: _[1]['pilots'], reverse=True)
                        pilots0: int = ordered_groups[0][1]['pilots']
                        pilots1: int = ordered_groups[1][1]['pilots']
                        if pilots0 > pilots1:
                            # Атакующие: (5), основная группа из Warriors tribe
                            grp: typing.Dict[str, typing.Any] = ordered_groups[0][1]
                            group_id: int = grp['id']
                            group_name: str = grp.get('name', str(group_id))
                            group_type: str = 'corporation' if ordered_groups[0] == 'c' else 'alliance'
                            attackers_txt += \
                                ", основная группа из " \
                                f"[{group_name}](https://zkillboard.com/{group_type}/{group_id}/) " \
                                f"({pilots0})"
                        elif pilots0 > 1 and pilots0 == pilots1:
                            num: int = 2
                            sz: int = len(ordered_groups)
                            while num < sz:
                                if pilots0 != ordered_groups[num][1]['pilots']:
                                    break
                                num += 1
                            if num <= 3:
                                if num == attacker_corps_len:
                                    # Атакующие: (6) группы из Warriors tribe (2), R Initiative (2), Phoenix Tag. (2)
                                    attackers_txt += " группы из "
                                else:
                                    # Атакующие: (7), основные группы из G.T.U. (2), Compi's (2), lolshto (2)
                                    attackers_txt += ", основные группы из "
                                for i in range(num):
                                    grp: typing.Dict[str, typing.Any] = attacker_corps[i]
                                    group_id: int = grp['id']
                                    group_name: str = grp.get('name', str(group_id))
                                    group_type: str = 'corporation' if ordered_groups[0] == 'c' else 'alliance'
                                    attackers_txt += \
                                        (", " if i else "") + \
                                        f"[{group_name}](https://zkillboard.com/{group_type}/{group_id}/) " \
                                        f"({pilots0})"
            attackers_txt += "."

        # Blood Khanid (Warriors tribe)
        victim_character_id: typing.Optional[int] = victim.get('character_id')
        victim_corporation_id: typing.Optional[int] = victim.get('corporation_id')
        victim_alliance_id: typing.Optional[int] = victim.get('alliance_id')
        if victim_character_id:
            character_name: str = victim.get('character_name', str(victim_character_id))
            victim_txt: str = f"[{character_name}](https://zkillboard.com/character/{victim_character_id}/)"
        else:
            victim_txt: str = ""
        if victim_corporation_id:
            corporation_name: str = victim.get('corporation_name', str(victim_corporation_id))
            victim_txt += f" ([{corporation_name}](https://zkillboard.com/corporation/{victim_corporation_id}/))"

        # Blood Khanid (Warriors tribe) потерял Rupture
        victim_ship_type_id: int = victim['ship_type_id']
        victim_ship_type_name: str = victim.get('ship_name', str(victim_ship_type_id))
        victim_txt += f" потерял **{victim_ship_type_name}**"

        # Blood Khanid (Warriors tribe) потерял Rupture в P-E9GN
        solar_system_id: int = solar_system['id']
        solar_system_name: str = solar_system.get('name', str(solar_system_id))
        region_name: typing.Optional[str] = solar_system.get('region')
        victim_txt += f" в [{solar_system_name}](https://zkillboard.com/system/{solar_system_id}/)"
        if region_name:
            # Blood Khanid (Warriors tribe) потерял Rupture в P-E9GN в Geminate
            victim_txt += f" в **{region_name}**"

        worth: typing.Optional[float] = zkb.get('worth')
        if worth:
            if worth < 1000000.0:
                victim_txt += f" стоимостью **{worth/1000.0:.2f}k** ISK"
            elif worth < 1000000000.0:
                victim_txt += f" стоимостью **{worth/1000000.0:.2f}m** ISK"
            else:
                victim_txt += f" стоимостью **{worth/1000000000.0:,.2f}b** ISK"
        victim_txt += "."

        datetime_txt: str = str(self.__killmail_data['time'])
        datetime_txt = f"{datetime_txt[:10]} {datetime_txt[11:16]}"
        footer_txt: str = datetime_txt
        if zkb.get('points', 0):
            points: str = self.get_points_description(zkb['points'])
            footer_txt += f" ● {points}"
        if solo or zkb.get('solo', False):
            footer_txt += " ● соло"
        if zkb.get('npc', False):
            footer_txt += " ● npc"
        if zkb.get('awox', False):
            footer_txt += " ● awox"

        # выбор иконки, которая появится в footer-е
        footer_icon: typing.Optional[str] = None
        if loss and q_settings.g_use_corporation_emblem_instead_alliance and victim_corporation_id:
            footer_icon = f"https://images.evetech.net/corporations/{victim_corporation_id}/logo?size=32"
        elif victim_alliance_id:
            footer_icon = f"https://images.evetech.net/alliances/{victim_alliance_id}/logo?size=32"
        elif victim_corporation_id:
            footer_icon = f"https://images.evetech.net/corporations/{victim_corporation_id}/logo?size=32"

        # await channel.send(contents=text, embed=embed)
        self.contents = \
            f"[**{solar_system_name} | {victim_ship_type_name}**]" \
            f"(https://zkillboard.com/kill/{self.__killmail_id}/)"
        self.embed = discord.Embed(
            description=victim_txt + "\n" + attackers_txt,
            colour=0xC85C70 if loss else 0x2e6b4d)
        self.embed.set_thumbnail(
            url=f"https://images.evetech.net/types/{victim_ship_type_id}/render?size=64")
        if footer_icon:
            self.embed.set_footer(text=footer_txt, icon_url=footer_icon)
        else:
            self.embed.set_footer(text=footer_txt)

    def get_points_description(self, points: int) -> str:
        #return f"{points} points"
        modulo: int = points % 100
        if 5 <= modulo <= 20:
            return f"{points} попугаев"
        else:
            modulo = points % 10
            if (0 == modulo) or (5 <= modulo <= 9):
                return f"{points} попугаев"
            elif 2 <= modulo <= 4:
                return f"{points} попугая"
            elif modulo == 1:
                return f"{points} попугай"
