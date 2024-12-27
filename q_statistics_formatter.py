import typing
import datetime
import discord


class FormattedDiscordStatisticsMessage:
    def __init__(self,
                 period_from: datetime.datetime,
                 period_to: datetime.datetime,
                 stat: typing.Dict[str, typing.Dict[str, int]]):
        self.contents: typing.Optional[str] = None
        self.embed: typing.Optional[discord.Embed] = None
        self.__period_from: datetime.datetime = period_from
        self.__period_to: datetime.datetime = period_to
        self.__stat: typing.Dict[str, typing.Dict[str, int]] = stat
        self.format()

    def format(self) -> None:
        if not self.__stat: return

        # await channel.send(contents=text, embed=embed)
        self.contents = "**Статистика подъехала**"

        paginator = discord.ext.commands.Paginator(prefix='', suffix='')
        for key, data in self.__stat:
            paginator.add_line(key)
