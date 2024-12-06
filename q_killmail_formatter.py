import typing
import json
import discord


class FormattedDiscordMessage:
    def __init__(self,
                 killmail_id: int,
                 killmail_data: typing.Dict[str, typing.Any],
                 killmail_attackers: typing.Dict[str, typing.Any],
                 tracked_corporation_ids: typing.List[int],
                 use_corporation_instead_alliance: bool):
        self.contents: typing.Optional[str] = None
        self.embed: typing.Optional[discord.Embed] = None
        self.__killmail_id: int = killmail_id
        self.__killmail_data: typing.Dict[str, typing.Any] = killmail_data
        self.__killmail_attackers: typing.Dict[str, typing.Any] = killmail_attackers
        self.format(tracked_corporation_ids, use_corporation_instead_alliance)

    @staticmethod
    def __pilot_url(pilot_id: int, pilot_name: typing.Optional[str]) -> str:
        if not pilot_name:
            pilot_name = str(pilot_id)
        return f" [{pilot_name}](https://zkillboard.com/character/{pilot_id}/)"

    @staticmethod
    def __pilots_group(group_type: str,
                       group_id: int,
                       group_name: typing.Optional[str],
                       pilots: typing.Optional[int] = None) -> str:
        if not group_name:
            group_name = str(group_id)
        group_type: str = 'corporation' if group_type == 'c' else 'alliance'
        res: str = f"[{group_name}](https://zkillboard.com/{group_type}/{group_id}/)"
        if pilots and pilots > 1:
            res += f" ({pilots})"
        return res

    def format(self,
               tracked_corporation_ids: typing.List[int],
               use_corporation_instead_alliance: bool) -> None:
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
            # Бой был выигран в соло пилотом Qandra Si
            attackers_txt: str = \
                f"Бой был выигран в соло пилотом " + \
                self.__pilot_url(solo_attacker_id, attacker_solo.get('character_name'))
            solo_ship_name: int = attacker_solo.get('ship_name')
            if solo_ship_name:
                # Бой был выигран в соло пилотом Qandra Si на Tristan
                attackers_txt += f" на **{solo_ship_name}**"
        else:
            attackers_txt: str = "Его добил"
            if final_character_id:
                # Его добил Qandra Si
                attackers_txt += " "
                attackers_txt += self.__pilot_url(final_character_id, final_blow.get('name'))
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
                if attacker_alli and corporation_id not in tracked_corporation_ids:
                    # Атакующие: (2) из Ragequit Cancel Sub
                    alli: typing.Dict[str, typing.Optional[int]] = attacker_alli[0]
                    attackers_txt += " из "
                    attackers_txt += self.__pilots_group('a', alli['id'], alli.get('name'))
                else:
                    # Атакующие: (2) из Warriors tribe
                    attackers_txt += " из "
                    attackers_txt += self.__pilots_group('c', corporation_id, corp.get('name'))
            elif attacker_corps_len >= 2:
                attacker_corps.sort(key=lambda _: _['pilots'], reverse=True)
                # print(attacker_corps, "-------", attacker_alli)
                if not attacker_alli:
                    # если нет атакующих альянсов, то работаем лишь только со списком
                    # корпораций, в котором 2 или более элемента
                    pilots0: int = attacker_corps[0]['pilots']
                    pilots1: int = attacker_corps[1]['pilots']
                    if pilots0 > pilots1:
                        # Атакующие: (5), основная группа из Warriors tribe
                        g: typing.Dict[str, typing.Any] = attacker_corps[0]
                        attackers_txt += ", основная группа из "
                        attackers_txt += self.__pilots_group('c', g['id'], g.get('name'), pilots0)
                    elif pilots0 == pilots1:
                        num: int = 2
                        while num < attacker_corps_len:
                            if pilots0 != attacker_corps[num]['pilots']:
                                break
                            num += 1
                        attackers_rest: str = ""
                        if pilots0 == 1:
                            # Атакующие: (2), пилоты из Warriors tribe и Phoenix Tag.
                            attackers_txt += ", пилоты из "
                            if attacker_corps_len > num:
                                attackers_rest = ".."
                        elif num == attacker_corps_len:
                            # Атакующие: (6) группы из Warriors tribe (2) и R Initiative (2), и Phoenix Tag. (2)
                            attackers_txt += ", группы из "
                        else:
                            # Атакующие: (7), основные группы из G.T.U. (2) и Compi's (2), и lolshto (2)
                            attackers_txt += ", основные группы из "
                            if attacker_corps_len > num:
                                attackers_rest = ".."
                        for i in range(min(3, num)):
                            g: typing.Dict[str, typing.Any] = attacker_corps[i]
                            attackers_txt += "" if i == 0 else (" и " if i == 1 else ", и ")
                            attackers_txt += self.__pilots_group('c', g['id'], g.get('name'), pilots0)
                        attackers_txt += attackers_rest
                else:
                    # если есть атакующие альянсы, то работать придётся с двумя списками, в каждом из которых может
                    # быть различная ситуация по накопленным данным, поэтому ищем паттерны
                    if use_corporation_instead_alliance and \
                       next((1 for _ in attacker_corps if _['id'] in tracked_corporation_ids), None):
                        # если группа атакующих из отслеживаемой корпорации, то в соответствии с указанными настройками
                        # удалить альянс и оставить только корпорацию
                        corps: typing.List[typing.Dict[str, typing.Any]] = [
                            _ for _ in attacker_corps
                            if _['alli'] is None or _['id'] in tracked_corporation_ids]
                        alli: typing.List[typing.Dict[str, typing.Any]] = attacker_alli[:]
                        # перебор отслеживаемых корпораций и удаление либо корпы, либо альянса, в зависимости от
                        # количества пилотов в группах
                        for corporation_id in tracked_corporation_ids:
                            # поиск корпорации
                            tracked_corp: typing.Optional[typing.Dict[str, typing.Any]] = \
                                next((_ for _ in corps if _['id'] == corporation_id), None)
                            # если отслеживаемая корпорация не найдена, или она не в альянсе, то выход
                            if not tracked_corp or tracked_corp['alli'] is None:
                                continue
                            # поиск альянса
                            alliance_id: int = tracked_corp['alli']
                            tracked_alli: typing.Optional[typing.Dict[str, typing.Any]] = \
                                next((_ for _ in alli if _['id'] == alliance_id), None)
                            # следующее условие вырожденное, альянс есть всегда, но проверим на всякий случай
                            if not tracked_alli:
                                continue
                            # удаляем либо корпорацию, либо альянс
                            if tracked_corp['pilots'] < tracked_alli['pilots']:
                                # удаляем корпорацию
                                corps: typing.List[typing.Dict[str, typing.Any]] = \
                                    [_ for _ in corps if _['id'] != corporation_id]
                            else:
                                # удаляем альянс
                                alli: typing.List[typing.Dict[str, typing.Any]] = \
                                    [_ for _ in alli if _['id'] != alliance_id]
                        # объединение списков в которых есть либо отслеживаемые корпорации, либо альянсы
                        ordered_groups: typing.List[typing.Tuple[str, typing.Dict[str, typing.Optional[int]]]] = \
                            [('c', _) for _ in corps] + \
                            [('a', _) for _ in alli]
                    else:
                        # среди атакующих корпораций нет тех, которые отслеживаются
                        ordered_groups: typing.List[typing.Tuple[str, typing.Dict[str, typing.Optional[int]]]] = \
                            [('c', _) for _ in attacker_corps if _['alli'] is None] + \
                            [('a', _) for _ in attacker_alli]
                    # print(ordered_groups)
                    # суммарно в объединённом списке может быть меньше 2х элементов (2 корпы из одного альянса удалятся)
                    if len(ordered_groups) == 1:
                        # Атакующие: (2) из C A M E L O T
                        g: typing.Dict[str, typing.Optional[int]] = ordered_groups[0][1]
                        attackers_txt += " из "
                        attackers_txt += self.__pilots_group('a', g['id'], g.get('name'))
                    else:
                        ordered_groups.sort(key=lambda _: _[1]['pilots'], reverse=True)
                        pilots0: int = ordered_groups[0][1]['pilots']
                        pilots1: int = ordered_groups[1][1]['pilots']
                        if pilots0 > pilots1:
                            # Атакующие: (5), основная группа из Warriors tribe
                            t: str = ordered_groups[0][0]
                            g: typing.Dict[str, typing.Any] = ordered_groups[0][1]
                            attackers_txt += ", основная группа из "
                            attackers_txt += self.__pilots_group(t, g['id'], g.get('name'), pilots0)
                        elif pilots0 == pilots1:
                            num: int = 2
                            sz: int = len(ordered_groups)
                            while num < sz:
                                if pilots0 != ordered_groups[num][1]['pilots']:
                                    break
                                num += 1
                            attackers_rest: str = ""
                            if pilots0 == 1:
                                # Атакующие: (2), пилоты из Warriors tribe и Phoenix Tag.
                                attackers_txt += ", пилоты из "
                                if sz > num:
                                    attackers_rest = ".."
                            elif num == sz:
                                # Атакующие: (6) группы из Warriors tribe (2) и R Initiative (2), и Phoenix Tag. (2)
                                attackers_txt += ", группы из "
                            else:
                                # Атакующие: (7), основные группы из G.T.U. (2) и Compi's (2), и lolshto (2)
                                attackers_txt += ", основные группы из "
                                if sz > num:
                                    attackers_rest = ".."
                            for i in range(num):
                                t: str = ordered_groups[i][0]
                                g: typing.Dict[str, typing.Any] = ordered_groups[i][1]
                                attackers_txt += "" if i == 0 else (" и " if i == 1 else ", и ")
                                attackers_txt += self.__pilots_group(t, g['id'], g.get('name'), g['pilots'])
                            attackers_txt += attackers_rest
            attackers_txt += "."

        # Blood Khanid (Warriors tribe)
        victim_character_id: typing.Optional[int] = victim.get('character_id')
        victim_corporation_id: typing.Optional[int] = victim.get('corporation_id')
        victim_alliance_id: typing.Optional[int] = victim.get('alliance_id')
        if victim_character_id:
            victim_txt: str = self.__pilot_url(victim_character_id, victim.get('character_name'))
        else:
            victim_txt: str = ""
        if victim_corporation_id:
            victim_txt += f" ({self.__pilots_group('c', victim_corporation_id, victim.get('corporation_name'))})"

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
        if loss and use_corporation_instead_alliance and victim_corporation_id:
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
