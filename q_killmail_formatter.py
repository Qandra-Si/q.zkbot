import typing
import json
import discord


class FormattedDiscordMessage:
    def __init__(self,
                 killmail_id: int,
                 killmail_hash: str,
                 zkb_data: typing.Dict[str, typing.Any],
                 tracked_corporation_ids: typing.List[int],
                 cache_dir: str = ".q_zkbot/esi_cache"):
        self.contents: typing.Optional[str] = None
        self.embed: typing.Optional[discord.Embed] = None
        # загружаем данные
        self.__filename: str = f"{cache_dir}/.cache_killmails_{killmail_id}_{killmail_hash}.json"
        with open(self.__filename, 'r', encoding='utf8') as f:
            s: str = f.read()
            self.__killmail = json.loads(s)
            f.close()
            if 'json' in self.__killmail:
                self.format(self.__killmail['json'], zkb_data, tracked_corporation_ids)
            # os.remove(self.__filename)

    def format(self,
               km,
               zkb_data: typing.Dict[str, typing.Any],
               tracked_corporation_ids: typing.List[int]) -> None:
        attackers: typing.List[typing.Dict[str, typing.Any]] = km['attackers']
        victim: typing.Dict[str, typing.Any] = km['victim']
        killmail_id: int = int(km['killmail_id'])

        loss: bool = victim.get('corporation_id', 0) in tracked_corporation_ids
        attacker_pilots: typing.List[typing.Dict[str, typing.Any]] = [_ for _ in attackers if 'character_id' in _]
        attacker_pilots_len: int = len(attacker_pilots)
        solo: bool = attacker_pilots_len == 1
        solo_attacker_id: typing.Optional[int] = None if not solo else attacker_pilots[0]['character_id']
        final_character_id: typing.Optional[int] = None
        final_ship_type_id: typing.Optional[int] = None
        final_blow_attacker: typing.Optional[typing.Dict[str, typing.Any]] = \
            next((_ for _ in attackers if _['final_blow']), None)
        if final_blow_attacker:
            final_character_id = final_blow_attacker.get('character_id')
            final_ship_type_id = final_blow_attacker.get('ship_type_id')

        # см. про расположение элементов в embed-е тут: https://guide.disnake.dev/popular-topics/embeds
        if solo:
            solo_attacker_name: str = str(solo_attacker_id)  # TODO:
            attackers_txt: str = \
                f"Окончательный удар в соло нанёс" \
                f" [{solo_attacker_name}](https://zkillboard.com/character/{solo_attacker_id}/)"
        else:
            attackers_txt: str = "Окончательный удар нанёс"
            if final_blow_attacker is None:
                attackers_txt += "? "
            elif final_character_id:
                final_character_name: str = str(final_character_id)  # TODO:
                attackers_txt += f" [{final_character_name}](https://zkillboard.com/character/{final_character_id}/)"

        if final_ship_type_id:
            ship_type_name: str = str(final_ship_type_id)  # TODO:
            if solo or final_character_id is not None:
                # Окончательный удар в соло нанёс Qandra Si на Tristan
                # Окончательный удар нанёс Qandra Si на Tristan
                attackers_txt += f" на **{ship_type_name}**"
            else:
                # Окончательный удар нанёс Tristan
                attackers_txt += f" **{ship_type_name}**"
        attackers_txt += "."

        if attacker_pilots_len >= 2:
            attackers_txt += f"\nАтакующие: {attacker_pilots_len}"
            corporations: typing.Dict[int, int] = {}
            for a in attacker_pilots:
                corporation_id: typing.Optional[int] = a.get('corporation_id')
                if corporation_id is not None:
                    if corporation_id in corporations:
                        corporations[corporation_id] += 1
                    else:
                        corporations[corporation_id] = 1
            corporations_len: int = len(corporations)
            if corporations_len == 1:
                # Атакующие: (2) из Warriors tribe
                corporation_id: int = list(corporations.keys())[0]
                corporation_name: str = str(corporation_id)  # TODO:
                attackers_txt += f" из [{corporation_name}](https://zkillboard.com/corporation/{corporation_id}/)"
            elif corporations_len >= 2:
                sorted_corporations: typing.List[typing.Tuple[int, int]] = [(_[0], _[1]) for _ in corporations.items()]
                sorted_corporations.sort(key=lambda _: _[1], reverse=True)
                if sorted_corporations[0][1] > sorted_corporations[1][1]:
                    # Атакующие: (5) основная группа из Warriors tribe
                    corporation_id: int = sorted_corporations[0][0]
                    corporation_name: str = str(corporation_id)  # TODO:
                    attackers_txt += \
                        "основная группа из " \
                        f"[{corporation_name}](https://zkillboard.com/corporation/{corporation_id}/) " \
                        f"({sorted_corporations[0][1]})"

        victim_character_id: typing.Optional[int] = victim.get('character_id')
        victim_corporation_id: typing.Optional[int] = victim.get('corporation_id')
        victim_alliance_id: typing.Optional[int] = victim.get('alliance_id')
        if victim_character_id:
            character_name: str = str(victim_character_id)  # TODO:
            victim_txt: str = f"[{character_name}](https://zkillboard.com/character/{victim_character_id}/)"
        else:
            victim_txt: str = ""
        if victim_corporation_id:
            corporation_name: str = str(victim_corporation_id)  # TODO:
            victim_txt += f" ([{corporation_name}](https://zkillboard.com/corporation/{victim_corporation_id}/))"

        victim_ship_type_id: int = victim['ship_type_id']
        victim_ship_type_name: str = str(victim_ship_type_id)  # TODO:
        victim_txt += f" потерял свой **{victim_ship_type_name}**"

        solar_system_id: int = km['solar_system_id']
        solar_system_name: str = str(solar_system_id)  # TODO:
        victim_txt += f" в [{solar_system_name}](https://zkillboard.com/system/{solar_system_id}/)"

        region_name: str = "0000"  # TODO:
        if region_name:
            victim_txt += f" в **{region_name}**"

        worth: typing.Optional[float] = zkb_data.get('worth')
        if worth:
            if worth < 1000000.0:
                victim_txt += f" стоимостью **{worth/1000.0:.2f}k** ISK."  # TODO:
            elif worth < 1000000000.0:
                victim_txt += f" стоимостью **{worth/1000000.0:.2f}m** ISK."  # TODO:
            else:
                victim_txt += f" стоимостью **{worth/1000000000.0:,.2f}b** ISK."  # TODO:

        datetime_txt = f"{km['killmail_time'][:10]} {km['killmail_time'][11:16]}"
        footer_txt: str = datetime_txt
        if zkb_data.get('points', 0):
            footer_txt += f" ● {zkb_data['points']} points"
        if zkb_data.get('solo', False):
            footer_txt += " ● solo"
        if zkb_data.get('npc', False):
            footer_txt += " ● npc"
        if zkb_data.get('awox', False):
            footer_txt += " ● awox"

        # await channel.send(contents=text, embed=embed)
        self.contents = \
            f"[**{solar_system_name} | {victim_ship_type_name}**]" \
            f"(https://zkillboard.com/kill/{killmail_id}/)"
        self.embed = discord.Embed(
            description=victim_txt + "\n" + attackers_txt,
            colour=0xC85C70 if loss else 0x2e6b4d)
        self.embed.set_thumbnail(
            url=f"https://images.evetech.net/types/{victim_ship_type_id}/render?size=64")
        if victim_alliance_id:
            self.embed.set_footer(
                text=footer_txt,
                icon_url=f"https://images.evetech.net/alliances/{victim_alliance_id}/logo?size=32")
        else:
            self.embed.set_footer(text=footer_txt)
