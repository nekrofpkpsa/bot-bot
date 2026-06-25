## WARNING! ALL YOU DO WITH THIS USERBOT ITS ON YOU OWN RISK! IF YOUR ACCOUNT GETS FREEZED/BANNED, I AM NOT RESPONSIBLE FOR IT!

## предупрждение! все что вы делаете с этим юзерботом, это на ваш страх и риск! если ваш аккаунт будет заблокирован/заморожен, я не несу ответственности за это!


import os
import re
import time
import random
import asyncio
import io
import json
from telethon import TelegramClient, events
from telethon.network import connection
from telethon.errors import SessionPasswordNeededError, PhoneCodeInvalidError

## get your own api, how to get it? https://my.telegram.org/auth?to=apps

API_ID = "22566570"
API_HASH = "7fa2e1ee4e929badc6588a877ab758e0"

client = TelegramClient("userbot_session", int(API_ID), API_HASH)

start_time = None
template = []
sessions = {}
pending_session = {}
pending_session_by_message = {}
proxies = {}
active_proxy = None
session_clients = {}
client_states = {}

SESSIONS_FILE = "sessions.json"
PROXIES_FILE = "proxies.json"
TRL3_FILE = "trl3_state.json"
TEMPLATE_FILE = os.path.abspath("template.txt")
VIDEO_URL = "https://x0.at/UsXK.mp4"

def get_client_state(client_id):
    if client_id not in client_states:
        client_states[client_id] = {
            "trl_running": False,
            "trl_task": None,
            "trl2_running": False,
            "trl2_task": None,
            "trl3_state": {"enabled": True, "targets": {}},
            "trl3_last_reply": {},
            "spam_running": False,
            "spam_task": None,
            "trl4_running": False,
            "trl4_task": None,
            "fuck_running": False,
            "fuck_task": None
        }
    return client_states[client_id]

def load_trl3_state(client_id):
    state = get_client_state(client_id)
    trl3_file = f"trl3_state_{client_id}.json"
    if os.path.exists(trl3_file):
        try:
            with open(trl3_file, "r") as f:
                state["trl3_state"] = json.load(f)
        except:
            state["trl3_state"] = {"enabled": True, "targets": {}}

def save_trl3_state(client_id):
    state = get_client_state(client_id)
    trl3_file = f"trl3_state_{client_id}.json"
    with open(trl3_file, "w") as f:
        json.dump(state["trl3_state"], f)


def load_sessions():
    global sessions
    if os.path.exists(SESSIONS_FILE):
        try:
            with open(SESSIONS_FILE, "r") as f:
                sessions = json.load(f)
        except:
            sessions = {}


def save_sessions():
    with open(SESSIONS_FILE, "w") as f:
        json.dump(sessions, f)


def load_proxies():
    global proxies, active_proxy
    if os.path.exists(PROXIES_FILE):
        try:
            with open(PROXIES_FILE, "r") as f:
                data = json.load(f)
                proxies = data.get("proxies", {})
                active_proxy = data.get("active", None)
        except:
            proxies = {}
            active_proxy = None


def save_proxies():
    with open(PROXIES_FILE, "w") as f:
        json.dump({"proxies": proxies, "active": active_proxy}, f)


def load_template():
    global template
    if os.path.exists(TEMPLATE_FILE):
        try:
            with open(TEMPLATE_FILE, "r", encoding="utf-8") as f:
                template = [line.strip() for line in f if line.strip()]
        except Exception:
            template = []


def get_uptime():
    if not start_time:
        return ""
    delta = int(time.time() - start_time)
    days = delta // 86400
    hours = (delta % 86400) // 3600
    minutes = (delta % 3600) // 60

    parts = []
    if days > 0:
        parts.append(f"{days}д")
    if hours > 0:
        parts.append(f"{hours}ч")
    if minutes > 0 or not parts:
        parts.append(f"{minutes}м")

    return "-".join(parts)


def parse_delay(value):
    if not value:
        raise ValueError("Пустая задержка")

    value = value.strip().lower()
    match = re.match(r"^(\d+)([smhd]?)$", value)
    if not match:
        raise ValueError("Задержка должна быть числом или числом с единицей, например 10s, 1m, 2h, 1d")

    amount = int(match.group(1))
    unit = match.group(2)

    if unit == "s" or unit == "":
        return amount
    if unit == "m":
        return amount * 60
    if unit == "h":
        return amount * 3600
    if unit == "d":
        return amount * 86400

    raise ValueError("Неверная единица времени")


def register_handlers(target_client, client_id=None):
    if client_id is None:
        client_id = "main"
    
    state = get_client_state(client_id)
    load_trl3_state(client_id)

    def safe_event(fn):
        async def wrapper(event):
            try:
                await fn(event)
            except asyncio.CancelledError:
                raise
            except Exception as e:
                print(f"Handler error [{fn.__name__}]: {e}")
                try:
                    if getattr(event, 'edit', None):
                        await event.edit("Произошла внутренняя ошибка. Проверь лог.")
                except Exception:
                    pass
        return wrapper

    @target_client.on(events.NewMessage(pattern=r"^\.info$", outgoing=True))
    @safe_event
    async def info_handler(event):
        uptime = get_uptime()
        ping_start = time.time()
        await event.edit("...")
        ping_end = time.time()
        latency_ms = (ping_end - ping_start) * 1000
        
        info_text = f"**SqqBot**\nVersion 1.3 (stable)\n\n"
        info_text += f"**Uptime:** {uptime}\n"
        info_text += f"**Ping:** {latency_ms:.0f}ms\n\n"
        info_text += "Type `.help` for commands."
        
        try:
            await target_client.send_file(event.chat_id, VIDEO_URL, caption=info_text, force_document=False)
            await event.delete()
        except Exception as e:
            print(f"Failed to send info video: {e}")
            await event.edit(info_text)

    @target_client.on(events.NewMessage(pattern=r"^\.help$", outgoing=True))
    @safe_event
    async def help_handler(event):
        commands = [
            "**Основные:**",
            ".info - инфо о боте",
            ".help - список команд",
            ".ping - проверка задержки",
            ".uptime - время работы",
            "",
            "**Сессии:**",
            ".sessions - список сессий",
            ".addsession (номер) - добавить",
            ".removesession (номер) - удалить",
            "",
            "**Прокси:**",
            ".addproxy (ip) (port) (secret)",
            ".proxylist - список",
            ".useproxy (ip) - использовать",
            ".checkproxy (ip) - проверить",
            ".removeproxy (ip) - удалить",
            "",
            "**Спам/TRL:**",
            ".shablon - сохранить шаблон",
            ".trl (задержка) [текст] - спам в чат",
            ".trl2 (задержка) [текст] (id группы)",
            ".trl3 (id) [задержка] - автоответ",
            ".trl3 list/on/off/clear/clearall",
            ".trl4 (задержка) (id) - тег + шаблон",
            ".spam (задержка) (сообщение)",
            ".txt \"текст любого размера\" - сохранить шаблон",
            ".fuck \"юз человека\" <задержка> - отправлять текст + видео",
            "",
            "**Другое:**",
            ".delmenow - удалить свои сообщения"
        ]
        help_text = "\n".join(commands)
        
        try:
            await target_client.send_file(event.chat_id, VIDEO_URL, caption=help_text, force_document=False)
            await event.delete()
        except Exception as e:
            print(f"Failed to send help video: {e}")
            await event.edit(help_text)

    @target_client.on(events.NewMessage(pattern=r"^\.uptime$", outgoing=True))
    @safe_event
    async def uptime_handler(event):
        uptime = get_uptime()
        await event.edit(f"**Uptime:** {uptime}")

    @target_client.on(events.NewMessage(pattern=r"^\.ping$", outgoing=True))
    @safe_event
    async def ping_handler(event):
        ping_start = time.time()
        await event.edit("Pinging...")
        ping_end = time.time()
        latency_ms = (ping_end - ping_start) * 1000
        await event.edit(f"Pong! Latency: {latency_ms:.2f}ms")

    @target_client.on(events.NewMessage(pattern=r"^\.sessions$",
                                        outgoing=True))
    @safe_event
    async def sessions_handler(event):
        load_sessions()
        if not sessions:
            await event.edit("Нет сохранённых сессий.")
            return

        text = "**Сессии:**\n\n"
        for phone, data in sessions.items():
            is_active = phone in session_clients and session_clients[
                phone].is_connected()
            status = "✅" if is_active else "❌"
            text += f"{status} `{phone}`\n"

        await event.edit(text)

    @target_client.on(
        events.NewMessage(pattern=r"^\.addproxy (.+)", outgoing=True))
    @safe_event
    async def addproxy_handler(event):
        global proxies

        args = event.pattern_match.group(1).strip().split()

        if len(args) < 3:
            await event.edit("Формат: .addproxy (ip) (port) (secret)")
            return

        ip = args[0]
        try:
            port = int(args[1])
        except ValueError:
            await event.edit("Порт должен быть числом!")
            return

        secret = args[2]

        load_proxies()
        proxies[ip] = {"ip": ip, "port": port, "secret": secret}
        save_proxies()

        await event.edit(f"✅ Прокси добавлен: `{ip}:{port}`")

    @target_client.on(
        events.NewMessage(pattern=r"^\.proxylist$", outgoing=True))
    @safe_event
    async def proxylist_handler(event):
        load_proxies()

        if not proxies:
            await event.edit("Нет сохранённых прокси.")
            return

        text = "**Прокси:**\n\n"
        for ip, data in proxies.items():
            status = "🟢" if active_proxy == ip else "⚪"
            text += f"{status} `{ip}:{data['port']}`\n"

        if active_proxy:
            text += f"\n**Активный:** `{active_proxy}`"
        else:
            text += "\n**Активный:** нет"

        await event.edit(text)

    @target_client.on(
        events.NewMessage(pattern=r"^\.useproxy (.+)", outgoing=True))
    @safe_event
    async def useproxy_handler(event):
        global active_proxy

        ip = event.pattern_match.group(1).strip()

        load_proxies()

        if ip == "off" or ip == "none":
            active_proxy = None
            save_proxies()
            await event.edit("✅ Прокси отключен")
            return

        if ip not in proxies:
            await event.edit(f"Прокси `{ip}` не найден.")
            return

        active_proxy = ip
        save_proxies()

        await event.edit(f"✅ Активный прокси: `{ip}:{proxies[ip]['port']}`")

    @target_client.on(
        events.NewMessage(pattern=r"^\.removeproxy (.+)", outgoing=True))
    @safe_event
    async def removeproxy_handler(event):
        global proxies, active_proxy

        ip = event.pattern_match.group(1).strip()

        load_proxies()

        if ip not in proxies:
            await event.edit(f"Прокси `{ip}` не найден.")
            return

        del proxies[ip]

        if active_proxy == ip:
            active_proxy = None

        save_proxies()

        await event.edit(f"✅ Прокси `{ip}` удалён.")

    @target_client.on(
        events.NewMessage(pattern=r"^\.checkproxy($| .+)", outgoing=True))
    @safe_event
    async def checkproxy_handler(event):
        args = event.raw_text[12:].strip()

        load_proxies()

        if args:
            ip = args
        elif active_proxy:
            ip = active_proxy
        else:
            await event.edit("Укажи IP или выбери прокси через .useproxy")
            return

        if ip not in proxies:
            await event.edit(f"Прокси `{ip}` не найден.")
            return

        await event.edit(f"Проверяю прокси `{ip}`...")

        proxy_data = proxies[ip]
        proxy = (proxy_data["ip"], proxy_data["port"], proxy_data["secret"])

        test_client = TelegramClient(
            "test_proxy_session",
            int(API_ID),
            API_HASH,
            connection=connection.ConnectionTcpMTProxyRandomizedIntermediate,
            proxy=proxy)

        try:
            await asyncio.wait_for(test_client.connect(), timeout=10)
            await test_client.disconnect()

            if os.path.exists("test_proxy_session.session"):
                os.remove("test_proxy_session.session")

            await event.edit(f"✅ Прокси `{ip}:{proxy_data['port']}` работает!")

        except asyncio.TimeoutError:
            await event.edit(f"❌ Прокси `{ip}` - таймаут (10 сек)")
        except Exception as e:
            await event.edit(f"❌ Прокси `{ip}` не работает: {str(e)[:100]}")

    @target_client.on(
        events.NewMessage(pattern=r"^\.addsession (.+)", outgoing=True))
    @safe_event
    async def addsession_handler(event):
        global pending_session

        phone = event.pattern_match.group(1).strip()

        if not phone:
            await event.edit("Укажи номер: .addsession +79001234567")
            return

        chat_id = event.chat_id

        pending_session[chat_id] = {
            "phone": phone,
            "state": "waiting_code",
            "client": None,
            "phone_code_hash": None
        }

        session_name = f"session_{phone.replace('+', '').replace(' ', '')}"

        load_proxies()

        if active_proxy and active_proxy in proxies:
            proxy_data = proxies[active_proxy]
            proxy = (proxy_data["ip"], proxy_data["port"],
                     proxy_data["secret"])
            new_client = TelegramClient(
                session_name,
                int(API_ID),
                API_HASH,
                connection=connection.
                ConnectionTcpMTProxyRandomizedIntermediate,
                proxy=proxy)
            proxy_info = f" через прокси `{active_proxy}`"
        else:
            new_client = TelegramClient(session_name, int(API_ID), API_HASH)
            proxy_info = ""

        try:
            await new_client.connect()

            result = await new_client.send_code_request(phone)
            pending_session[chat_id]["client"] = new_client
            pending_session[chat_id][
                "phone_code_hash"] = result.phone_code_hash

            prompt_msg = await event.edit(
                f"Код отправлен на {phone}{proxy_info}\n\n**Код:**")
            pending_session[chat_id]["prompt_msg_id"] = prompt_msg.id
            pending_session_by_message[prompt_msg.id] = chat_id

        except Exception as e:
            await event.edit(f"Ошибка: {str(e)}")
            if new_client:
                try:
                    await new_client.disconnect()
                except:
                    pass
            if chat_id in pending_session:
                del pending_session[chat_id]

    @target_client.on(events.NewMessage(outgoing=True))
    @safe_event
    async def code_handler(event):
        global pending_session, session_clients

        chat_id = event.chat_id
        session_data = pending_session.get(chat_id)

        if not session_data and event.reply_to_msg_id:
            prev_chat_id = pending_session_by_message.get(event.reply_to_msg_id)
            if prev_chat_id:
                session_data = pending_session.get(prev_chat_id)
                chat_id = prev_chat_id

        if not session_data:
            return
        text = event.raw_text.strip()

        if text.startswith("."):
            return

        if session_data["state"] == "waiting_code":
            code = text.replace(" ", "").replace("-", "")

            if not code.isdigit():
                return

            new_client = session_data["client"]
            phone = session_data["phone"]
            phone_code_hash = session_data["phone_code_hash"]
            try:
                result = await new_client.sign_in(
                    phone, code, phone_code_hash=phone_code_hash)

                if result:
                    me = await new_client.get_me()

                    load_sessions()
                    sessions[phone] = {
                        "active": True,
                        "session_name":
                        f"session_{phone.replace('+', '').replace(' ', '')}",
                        "user_id": me.id,
                        "username": me.username,
                        "first_name": me.first_name
                    }
                    save_sessions()

                    register_handlers(new_client)
                    session_clients[phone] = new_client

                    await event.edit(
                        f"✅ Сессия добавлена и запущена!\n\nАккаунт: {me.first_name} (@{me.username})"
                    )

                    prompt_id = session_data.get("prompt_msg_id")
                    if prompt_id:
                        pending_session_by_message.pop(prompt_id, None)
                    del pending_session[chat_id]

            except SessionPasswordNeededError:
                pending_session[chat_id]["state"] = "waiting_2fa"
                await event.edit("Требуется 2FA\n\n**Пароль:**")

            except PhoneCodeInvalidError:
                await event.edit("Неверный код! Попробуй ещё раз.\n\n**Код:**")

            except Exception as e:
                error_msg = str(e)
                if "password" in error_msg.lower() or "2fa" in error_msg.lower(
                ):
                    pending_session[chat_id]["state"] = "waiting_2fa"
                    await event.edit("Требуется 2FA\n\n**Пароль:**")
                else:
                    await event.edit(f"Ошибка: {error_msg}")
                    if new_client:
                        await new_client.disconnect()
                    prompt_id = session_data.get("prompt_msg_id")
                    if prompt_id:
                        pending_session_by_message.pop(prompt_id, None)
                    if chat_id in pending_session:
                        del pending_session[chat_id]

        elif session_data["state"] == "waiting_2fa":
            password = text
            new_client = session_data["client"]
            phone = session_data["phone"]

            try:
                await new_client.sign_in(password=password)

                me = await new_client.get_me()

                load_sessions()
                sessions[phone] = {
                    "active": True,
                    "session_name":
                    f"session_{phone.replace('+', '').replace(' ', '')}",
                    "user_id": me.id,
                    "username": me.username,
                    "first_name": me.first_name
                }
                save_sessions()

                register_handlers(new_client)
                session_clients[phone] = new_client

                await event.edit(
                    f"✅ Сессия добавлена и запущена!\n\nАккаунт: {me.first_name} (@{me.username})"
                )

                del pending_session[chat_id]

            except Exception as e:
                await event.edit(
                    f"Неверный пароль. Попробуй ещё.\n\n**Пароль:**")

    @target_client.on(
        events.NewMessage(pattern=r"^\.removesession (.+)", outgoing=True))
    @safe_event
    async def removesession_handler(event):
        global session_clients

        phone = event.pattern_match.group(1).strip()

        load_sessions()

        if phone not in sessions:
            await event.edit(f"Сессия `{phone}` не найдена.")
            return

        session_name = sessions[phone].get("session_name", "")

        if phone in session_clients:
            try:
                await session_clients[phone].disconnect()
            except:
                pass
            del session_clients[phone]

        del sessions[phone]
        save_sessions()

        session_file = f"{session_name}.session"
        if os.path.exists(session_file):
            try:
                os.remove(session_file)
            except:
                pass

        await event.edit(f"✅ Сессия `{phone}` удалена и остановлена.")

    @target_client.on(events.NewMessage(pattern=r"^\.shablon$", outgoing=True))
    @safe_event
    async def shablon_handler(event):
        global template
        reply = await event.get_reply_message()

        if not reply or not reply.document:
            await event.edit("Реплай на .txt файл!")
            return

        if reply.document.mime_type != "text/plain":
            await event.edit("Только .txt файлы!")
            return

        file = io.BytesIO()
        await reply.download_media(file=file)
        text = file.getvalue().decode("utf-8")
        template = [line.strip() for line in text.splitlines() if line.strip()]

        try:
            with open(TEMPLATE_FILE, "w", encoding="utf-8") as f:
                f.write(text)
        except Exception:
            pass

        if template:
            await event.edit(f"Шаблон сохранён! ({len(template)} строк)")
        else:
            await event.edit("Пустой шаблон!")

    @target_client.on(events.NewMessage(pattern=r"^\.txt($| .+)", outgoing=True))
    @safe_event
    async def txt_handler(event):
        text = event.raw_text[5:].strip()
        if not text:
            await event.edit("Введите текст в кавычках: .txt \"текст любого размера\"")
            return

        if text.startswith('"') and text.endswith('"') and len(text) >= 2:
            text = text[1:-1]

        try:
            with open(TEMPLATE_FILE, "w", encoding="utf-8") as f:
                f.write(text)
            load_template()
            await event.edit(f"✅ Шаблон сохранён в {TEMPLATE_FILE}")
        except Exception as e:
            await event.edit(f"❌ Ошибка сохранения шаблона: {e}")

    async def trl_loop(chat_id, delay, prefix=""):
        while state["trl_running"]:
            if not template:
                break
            line = random.choice(template)
            text = f"{prefix} {line}".strip() if prefix else line
            try:
                await target_client.send_message(chat_id, text)
            except Exception:
                pass
            await asyncio.sleep(delay)

    async def fuck_loop(chat_id, delay, user_text):
        while state["fuck_running"]:
            if not os.path.exists(TEMPLATE_FILE):
                break

            try:
                with open(TEMPLATE_FILE, "r", encoding="utf-8") as f:
                    lines = [line.strip() for line in f if line.strip()]
                if not lines:
                    break
                message_line = random.choice(lines)
                text = f"{user_text}\n{message_line}"
                await target_client.send_file(chat_id, VIDEO_URL, caption=text)
            except Exception as e:
                print(f"fuck_loop error: {e}")
            await asyncio.sleep(delay)

    @target_client.on(
        events.NewMessage(pattern=r"^\.fuck($| .+)", outgoing=True))
    @safe_event
    async def fuck_handler(event):
        load_template()
        if state["fuck_running"]:
            state["fuck_running"] = False
            if state["fuck_task"]:
                state["fuck_task"].cancel()
            await event.edit(".fuck остановлен.")
            return

        args = event.raw_text[6:].strip()
        if not args:
            await event.edit("Формат: .fuck \"юз человека\" <задержка>")
            return

        match = re.match(r'^"([^"]+)"\s+(.+)$', args)
        if match:
            user_text = match.group(1)
            try:
                delay = parse_delay(match.group(2))
            except ValueError:
                await event.edit("Формат: .fuck \"юз человека\" <задержка> (например 1s, 1m, 1h)")
                return
        else:
            parts = args.rsplit(" ", 1)
            if len(parts) != 2:
                await event.edit("Формат: .fuck \"юз человека\" <задержка> (например 1s, 1m, 1h)")
                return
            user_text = parts[0]
            try:
                delay = parse_delay(parts[1])
            except ValueError:
                await event.edit("Формат: .fuck \"юз человека\" <задержка> (например 1s, 1m, 1h)")
                return

        if not template:
            await event.edit(f"Файл шаблона не найден или пуст. Напиши .txt и сохрани шаблон.")
            return

        state["fuck_running"] = True
        await event.edit(".fuck запущен!")
        state["fuck_task"] = asyncio.create_task(
            fuck_loop(event.chat_id, delay, user_text))

    @target_client.on(
        events.NewMessage(pattern=r"^\.trl($| .+)", outgoing=True))
    @safe_event
    async def trl_handler(event):
        load_template()
        if state["trl_running"]:
            state["trl_running"] = False
            if state["trl_task"]:
                state["trl_task"].cancel()
            await event.edit("Остановлено.")
            return

        args = event.raw_text[4:].strip().split()

        if not args:
            await event.edit("Укажи задержку: .trl <задержка> [доп текст]")
            return

        try:
            delay = parse_delay(args[0])
        except ValueError:
            await event.edit("Задержка должна быть числом или иметь единицу: 1s, 1m, 1h, 1d")
            return

        prefix = " ".join(args[1:]) if len(args) > 1 else ""

        if not template:
            await event.edit("Сначала сохрани шаблон через .shablon или .txt")
            return

        state["trl_running"] = True
        await event.edit("Запущено!")
        state["trl_task"] = asyncio.create_task(trl_loop(event.chat_id, delay, prefix))

    async def trl2_loop(chat_id, delay, prefix=""):
        while state["trl2_running"]:
            if not template:
                break
            line = random.choice(template)
            text = f"{prefix} {line}".strip() if prefix else line
            try:
                await target_client.send_message(chat_id, text)
            except Exception:
                pass
            await asyncio.sleep(delay)

    @target_client.on(
        events.NewMessage(pattern=r"^\.trl2($| .+)", outgoing=True))
    @safe_event
    async def trl2_handler(event):
        if state["trl2_running"]:
            state["trl2_running"] = False
            if state["trl2_task"]:
                state["trl2_task"].cancel()
            await event.edit("Остановлено.")
            return

        args = event.raw_text[5:].strip()

        if not args:
            await event.edit("Формат: .trl2 <задержка> [доп текст] <group_id>")
            return

        parts = args.rsplit(" ", 1)
        if len(parts) < 2:
            await event.edit("Формат: .trl2 <задержка> [доп текст] <group_id>")
            return

        try:
            group_id = int(parts[1])
        except ValueError:
            await event.edit("Неверный ID группы!")
            return

        rest = parts[0].split(" ", 1)
        try:
            delay = parse_delay(rest[0])
        except ValueError:
            await event.edit("Задержка должна быть числом или иметь единицу: 1s, 1m, 1h")
            return

        prefix = rest[1] if len(rest) > 1 else ""

        if not template:
            await event.edit("Сначала сохрани шаблон через .shablon")
            return

        state["trl2_running"] = True
        await event.edit("Запущено!")
        state["trl2_task"] = asyncio.create_task(trl2_loop(group_id, delay, prefix))

    @target_client.on(
        events.NewMessage(pattern=r"^\.trl3($| .+)", outgoing=True))
    @safe_event
    async def trl3_handler(event):
        args = event.raw_text[5:].strip().split()
        load_trl3_state(client_id)
        trl3_state = state["trl3_state"]

        if not args:
            await event.edit("Формат:\n.trl3 (id) [задержка] - добавить\n.trl3 list - список\n.trl3 on/off - вкл/выкл\n.trl3 clear (id) - убрать\n.trl3 clearall - очистить")
            return

        cmd = args[0].lower()

        if cmd == "list":
            if not trl3_state["targets"]:
                await event.edit("Список автоответчика пуст.")
                return
            status = "✅ ВКЛ" if trl3_state["enabled"] else "❌ ВЫКЛ"
            text = f"**Автоответчик:** {status}\n\n"
            for uid, data in trl3_state["targets"].items():
                delay = data.get("delay", 0)
                text += f"• ID: `{uid}` (задержка: {delay}с)\n"
            await event.edit(text)
            return

        if cmd == "on":
            trl3_state["enabled"] = True
            save_trl3_state(client_id)
            await event.edit("✅ Автоответчик включен")
            return

        if cmd == "off":
            trl3_state["enabled"] = False
            save_trl3_state(client_id)
            await event.edit("❌ Автоответчик выключен")
            return

        if cmd == "clear":
            if len(args) < 2:
                await event.edit("Укажи ID: .trl3 clear (id)")
                return
            uid = args[1]
            if uid in trl3_state["targets"]:
                del trl3_state["targets"][uid]
                if uid in state["trl3_last_reply"]:
                    del state["trl3_last_reply"][uid]
                save_trl3_state(client_id)
                await event.edit(f"✅ ID `{uid}` убран из списка")
            else:
                await event.edit(f"ID `{uid}` не найден в списке")
            return

        if cmd == "clearall":
            trl3_state["targets"] = {}
            state["trl3_last_reply"] = {}
            save_trl3_state(client_id)
            await event.edit("✅ Список автоответчика очищен")
            return

        try:
            user_id = int(args[0])
        except ValueError:
            await event.edit("ID должен быть числом!")
            return

        delay = 0
        if len(args) > 1:
            try:
                delay = parse_delay(args[1])
            except ValueError:
                await event.edit("Задержка должна быть числом или иметь единицу: 1s, 1m, 1h, 1d")
                return

        if not template:
            await event.edit("Сначала сохрани шаблон через .shablon")
            return

        trl3_state["targets"][str(user_id)] = {"delay": delay}
        save_trl3_state(client_id)
        await event.edit(f"✅ Добавлен в автоответчик: `{user_id}` (задержка: {delay}с)")

    @target_client.on(events.NewMessage(incoming=True))
    @safe_event
    async def trl3_watcher(event):
        load_trl3_state(client_id)
        trl3_state = state["trl3_state"]

        if not trl3_state["enabled"] or not trl3_state["targets"] or not template:
            return

        sender_id = str(event.sender_id)
        if sender_id not in trl3_state["targets"]:
            return

        target_data = trl3_state["targets"][sender_id]
        delay = target_data.get("delay", 0)

        current_time = time.time()
        last_time = state["trl3_last_reply"].get(sender_id, 0)
        if current_time - last_time < delay:
            return

        line = random.choice(template)
        try:
            await event.reply(line)
            state["trl3_last_reply"][sender_id] = current_time
        except Exception:
            pass

    @target_client.on(events.NewMessage(pattern=r"^\.delmenow$",
                                        outgoing=True))
    @safe_event
    async def delmenow_handler(event):
        me = await target_client.get_me()
        async for msg in target_client.iter_messages(event.chat_id,
                                                     from_user=me.id):
            try:
                await msg.delete()
            except Exception:
                pass

    async def spam_loop(chat_id, delay, message):
        while state["spam_running"]:
            try:
                await target_client.send_message(chat_id, message)
            except Exception:
                pass
            await asyncio.sleep(delay)

    @target_client.on(
        events.NewMessage(pattern=r"^\.spam($| .+)", outgoing=True))
    @safe_event
    async def spam_handler(event):
        if state["spam_running"]:
            state["spam_running"] = False
            if state["spam_task"]:
                state["spam_task"].cancel()
            await event.edit("Остановлено.")
            return

        args = event.raw_text[5:].strip().split(" ", 1)

        if len(args) < 2:
            await event.edit("Формат: .spam <задержка> <сообщение>")
            return

        try:
            delay = parse_delay(args[0])
        except ValueError:
            await event.edit("Задержка должна быть числом или иметь единицу: 1s, 1m, 1h, 1d")
            return

        message = args[1]

        state["spam_running"] = True
        await event.edit("Спам запущен!")
        state["spam_task"] = asyncio.create_task(
            spam_loop(event.chat_id, delay, message))

    async def trl4_loop(chat_id, delay, user_id, user_entity):
        while state["trl4_running"]:
            if not template:
                break
            line = random.choice(template)
            try:
                if user_entity.username:
                    mention = f"@{user_entity.username}"
                    text = f"{mention} {line}"
                    await target_client.send_message(chat_id, text)
                else:
                    first_name = user_entity.first_name or "User"
                    mention = f"[{first_name}](tg://user?id={user_id})"
                    text = f"{mention} {line}"
                    await target_client.send_message(chat_id, text, parse_mode='md')
            except Exception as e:
                print(f"trl4 error: {e}")
            await asyncio.sleep(delay)

    @target_client.on(
        events.NewMessage(pattern=r"^\.trl4($| .+)", outgoing=True))
    @safe_event
    async def trl4_handler(event):
        if state["trl4_running"]:
            state["trl4_running"] = False
            if state["trl4_task"]:
                state["trl4_task"].cancel()
            await event.edit("Остановлено.")
            return

        args = event.raw_text[5:].strip().split()

        if len(args) < 2:
            await event.edit("Формат: .trl4 <задержка> <id юзера>")
            return

        try:
            delay = parse_delay(args[0])
        except ValueError:
            await event.edit("Задержка должна быть числом или иметь единицу: 1s, 1m, 1h")
            return

        try:
            user_id = int(args[1])
        except ValueError:
            await event.edit("ID должен быть числом!")
            return

        if not template:
            await event.edit("Сначала сохрани шаблон через .shablon")
            return

        try:
            user_entity = await target_client.get_entity(user_id)
        except Exception as e:
            await event.edit(f"Не удалось найти юзера: {e}")
            return

        state["trl4_running"] = True
        await event.edit("Запущено!")
        state["trl4_task"] = asyncio.create_task(
            trl4_loop(event.chat_id, delay, user_id, user_entity))


register_handlers(client, "main")


async def start_saved_sessions():
    global session_clients
    load_sessions()
    load_proxies()

    for phone, data in sessions.items():
        if not data.get("active"):
            continue

        session_name = data.get("session_name")
        if not session_name:
            continue

        session_file = f"{session_name}.session"
        if not os.path.exists(session_file):
            continue

        try:
            if active_proxy and active_proxy in proxies:
                proxy_data = proxies[active_proxy]
                proxy = (proxy_data["ip"], proxy_data["port"],
                         proxy_data["secret"])
                session_client = TelegramClient(
                    session_name,
                    int(API_ID),
                    API_HASH,
                    connection=connection.
                    ConnectionTcpMTProxyRandomizedIntermediate,
                    proxy=proxy)
            else:
                session_client = TelegramClient(session_name, int(API_ID),
                                                API_HASH)

            await session_client.connect()

            if await session_client.is_user_authorized():
                register_handlers(session_client, phone)
                session_clients[phone] = session_client
                me = await session_client.get_me()
                print(
                    f"Session started: {me.first_name} (@{me.username}) - {phone}"
                )
            else:
                await session_client.disconnect()
                print(f"Session {phone} is not authorized, skipping")

        except Exception as e:
            print(f"Failed to start session {phone}: {e}")


async def main():
    global start_time
    print("Starting Telegram Userbot...")
    load_sessions()
    load_proxies()
    await client.start()
    start_time = time.time()
    me = await client.get_me()
    print(f"Logged in as: {me.first_name} (@{me.username})")

    await start_saved_sessions()

    print("Userbot is running!")
    print(
        "type .info for commands"
    )
    await client.run_until_disconnected()


if __name__ == "__main__":
    asyncio.run(main())
