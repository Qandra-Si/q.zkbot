# Q.ZKBot Discord bot
[![GitHub issues](https://img.shields.io/github/issues/Qandra-Si/q.zkbot)](https://github.com/Qandra-Si/q.zkbot/issues)
[![GitHub forks](https://img.shields.io/github/forks/Qandra-Si/q.zkbot)](https://github.com/Qandra-Si/q.zkbot/network)
[![GitHub stars](https://img.shields.io/github/stars/Qandra-Si/q.zkbot)](https://github.com/Qandra-Si/q.zkbot/stargazers)
[![GitHub license](https://img.shields.io/github/license/Qandra-Si/q.zkbot)](https://github.com/Qandra-Si/q.zkbot/blob/master/LICENSE)

Discord-бот для публикации looses и wins с zkillboard.

Создать своё discord-приложение тут: https://discordapp.com/developers/applications/

Создать своё esi-приложение тут: https://developers.eveonline.com/applications

Установка:

```bash
mkdir ~/q_zkbot
cd ~/q_zkbot
git clone git@github.com:Qandra-Si/q.zkbot.git .
git submodule init
git submodule update --recursive

cp q_settings.py.template q_settings.py
# edit q_settings.py

python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```
