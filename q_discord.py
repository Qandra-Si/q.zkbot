import typing
import json
import http.client
import discord
from discord.ext import tasks

import postgresql_interface as db
import q_settings
import q_killmail_formatter as fmt


def is_killmail_ready_on_zkillboard(killmail_id: int) -> bool:
    conn = http.client.HTTPSConnection("zkillboard.com")
    conn.request("GET", f"/kill/{killmail_id}/")
    res = conn.getresponse()
    return res.status != 404  # если всё что угодно, но не "404 Not Found", то публикуем


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
            non_published: typing.List[typing.Tuple[int, str]] = qzm.get_all_non_published_killmails()
            if non_published:
                is_any_ready: bool = False
                for killmail_id, killmail_hash in non_published:
                    if is_killmail_ready_on_zkillboard(killmail_id):
                        fdm: fmt.FormattedDiscordMessage = fmt.FormattedDiscordMessage(
                            killmail_id,
                            killmail_hash,
                            q_settings.q_tracked_corporations,
                            ".q_zkbot/esi_cache")
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