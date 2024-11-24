import typing
import json
import http.client
import discord
from discord.ext import tasks

import postgresql_interface as db
import q_settings
import q_killmail_formatter as fmt


def is_killmail_ready_on_zkillboard(killmail_id: int) -> typing.Tuple[bool, int, str]:
    conn = http.client.HTTPSConnection("zkillboard.com")
    conn.request("GET", f"/kill/{killmail_id}/")
    res = conn.getresponse()
    return res.status != 404, res.status, res.reason  # если всё что угодно, но не "404 Not Found", то публикуем


class MyClient(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def setup_hook(self) -> None:
        # start the task to run in the background
        self.my_background_task.start()

    async def on_ready(self):
        print(f'Logged in as {self.user} (ID: {self.user.id})')

    @tasks.loop(seconds=30)
    async def my_background_task(self):
        channel = self.get_channel(q_settings.q_discord_channel)
        if channel:
            # подключение к БД
            qzdb: db.QZKBotDatabase = db.QZKBotDatabase(debug=False)
            qzdb.connect(q_settings.g_database)
            qzm: db.QZKBotMethods = db.QZKBotMethods(qzdb)
            non_published: typing.List[typing.Dict[str, typing.Any]] = qzm.get_all_non_published_killmails()
            if non_published:
                is_any_ready: bool = False
                for killmail_data in non_published:
                    killmail_id: int = killmail_data['id']
                    ready, status, reason = is_killmail_ready_on_zkillboard(killmail_id)
                    if not ready:
                        print(f'Can\'t publish killmail {killmail_id}: {status} {reason}')
                        continue
                    worth: typing.Optional[float] = killmail_data.get('worth')
                    print(f'Publishing killmail {killmail_id} (worth: {worth})')

                    killmail_attackers: typing.List[typing.Dict[str, typing.Any]] = \
                        qzm.get_attackers_groups_by_killmail(killmail_id)
                    killmail_solo_attacker: typing.Optional[typing.Dict[str, typing.Any]] = None
                    if len(killmail_attackers) == 1 and killmail_attackers[0]['corp']['pilots'] == 1:
                        killmail_solo_attacker = qzm.get_solo_attacker_by_killmail(killmail_id)

                    fdm: fmt.FormattedDiscordMessage = fmt.FormattedDiscordMessage(
                        killmail_id,
                        killmail_data,
                        killmail_attackers,
                        killmail_solo_attacker,
                        q_settings.q_tracked_corporations)
                    if fdm.contents and fdm.embed:
                        await channel.send(content=fdm.contents, embed=fdm.embed)
                    else:
                        await channel.send(f"https://zkillboard.com/kill/{killmail_id}/")
                    del fdm
                    qzm.mark_killmail_as_published(killmail_id)
                    is_any_ready = True
                if is_any_ready:
                    qzdb.commit()
            del qzm
            qzdb.disconnect()
            del qzdb
        else:
            print(f'There are no access to channel {q_settings.q_discord_channel}')

    @my_background_task.before_loop
    async def before_my_task(self):
        await self.wait_until_ready()


client = MyClient(intents=discord.Intents.default())
client.run(q_settings.g_discord_token)