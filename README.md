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
sudo apt install postgresql

mkdir ~/q_zkbot
cd ~/q_zkbot
git clone https://github.com/Qandra-Si/q.zkbot.git .
git submodule init
git submodule update --recursive

# выполни скрипты настройки БД в директории database
# при переключении на новую версию программы выполни update-скрипты

cp q_settings.py.template q_settings.py
# отредактируй q_settings.py

python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt

# запустить однократно указав имя пилота с директорской ролью (не должность, а роль)
.venv/bin/python3 q_loader.py --pilot="Qandra Si" --online
```

Добавить в `crontab -e` команду:

```bash
*/5 * * * * /usr/bin/flock -w 0 /tmp/qzkbot-fast.lockfile /home/user/q_zkbot/run-5minutes.sh >> /tmp/tmp-qz.cron 2>&1
```

Запустить в `screen` команду:

```bash
.venv/bin/python3 q_discord.py
```
