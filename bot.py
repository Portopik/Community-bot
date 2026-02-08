import json
import os
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# ========== НАСТРОЙКИ ==========
# ⚠️ ВАЖНО: Получите токен у @BotFather и вставьте его ниже
TOKEN = "8533919423:AAEmkagykEzeRorF-MzkQSIrrITwcpQRtP8"  # <-- ЗАМЕНИТЕ ЭТО!

# Секретный код разработчика
DEVELOPER_CODE = "ndjskom900nwykmsyint8mdyuume7kz7o3nd7knstghnn"

# Ссылки
RULES_LINK = "https://t.me/+-yBQzgebofs2MWUy"  # Правила
CHAT_LINK = "https://t.me/+xvWIFeupCAtkZDgy"   # Чат

# Ранги
RANKS = [
    {"symbol": "?", "name": "Луркер 🕶️", "xp": 0},
    {"symbol": "??", "name": "Ньюфаг 🐣", "xp": 50},
    {"symbol": "???", "name": "Контактёр 📡", "xp": 150},
    {"symbol": "????", "name": "Мемолог 🎭", "xp": 300},
    {"symbol": "?????", "name": "Гуру 🧠", "xp": 500},
    {"symbol": "??????", "name": "Криэйтор ✨", "xp": 800},
    {"symbol": "???????", "name": "Модератор ⚖️", "xp": 1200},
    {"symbol": "????????", "name": "Интегратор 🔗", "xp": 1700},
    {"symbol": "?????????", "name": "Легенда 🏆", "xp": 2300},
    {"symbol": "??????????", "name": "ОГ (Original G) 👑", "xp": 3000}
]

# Данные
users = {}
sticker_tracker = {}
developers = {}

# ========== ФУНКЦИИ СОХРАНЕНИЯ ==========
def save_data():
    """Сохранить данные в файл"""
    data = {
        "users": users,
        "last_reset": datetime.now().isoformat()
    }
    with open("bot_data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_data():
    """Загрузить данные из файла"""
    global users
    if os.path.exists("bot_data.json"):
        try:
            with open("bot_data.json", "r", encoding="utf-8") as f:
                data = json.load(f)
                users = data.get("users", {})
                # Сброс дневных счетчиков если прошло больше дня
                last_reset_str = data.get("last_reset")
                if last_reset_str:
                    last_reset = datetime.fromisoformat(last_reset_str)
                    if (datetime.now() - last_reset).days >= 1:
                        reset_daily_counts()
        except:
            users = {}

def load_developers():
    """Загрузить разработчиков"""
    global developers
    if os.path.exists("developers.json"):
        try:
            with open("developers.json", "r", encoding="utf-8") as f:
                developers = json.load(f)
        except:
            developers = {}

def save_developers():
    """Сохранить разработчиков"""
    with open("developers.json", "w", encoding="utf-8") as f:
        json.dump(developers, f, ensure_ascii=False, indent=2)

def reset_daily_counts():
    """Сбросить дневные счетчики"""
    for user_id, user in users.items():
        user["hearts_today"] = 0
        user["likes_today"] = 0
        user["nerds_today"] = 0
    save_data()

# ========== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ==========
def get_rank_info(xp):
    """Получить информацию о ранге по XP"""
    for rank in reversed(RANKS):
        if xp >= rank["xp"]:
            return rank["symbol"], rank["name"]
    return RANKS[0]["symbol"], RANKS[0]["name"]

def can_add_xp(user_data, xp_type):
    """Проверить можно ли добавить XP"""
    now = datetime.now()
    
    if xp_type == "heart":
        if user_data.get("hearts_today", 0) >= 10:
            return False, "Лимит: 10 ❤️ в день"
        
        last_time = user_data.get("last_heart")
        if last_time:
            last = datetime.fromisoformat(last_time)
            if (now - last).seconds < 60:
                return False, "Ждите 60 секунд"
        
        return True, ""
    
    elif xp_type == "like":
        if user_data["xp"] < 150:
            return False, "👍 доступно с 3 ранга (150 XP)"
        
        if user_data.get("likes_today", 0) >= 2:
            return False, "Лимит: 2 👍 в день"
        
        last_time = user_data.get("last_like")
        if last_time:
            last = datetime.fromisoformat(last_time)
            if (now - last).seconds < 300:
                return False, "Ждите 5 минут"
        
        return True, ""
    
    elif xp_type == "nerd":
        if user_data["xp"] < 1200:
            return False, "🤓 доступно с 7 ранга (1200 XP)"
        
        last_time = user_data.get("last_nerd")
        if last_time and datetime.fromisoformat(last_time).date() == now.date():
            return False, "Лимит: 1 🤓 в день"
        
        return True, ""
    
    return False, "Неизвестный тип"

def add_xp(user_id, amount, xp_type):
    """Добавить XP пользователю"""
    if user_id not in users:
        return False, "Пользователь не найден"
    
    user = users[user_id]
    user["xp"] += amount
    
    # Обновляем время последнего действия
    now = datetime.now()
    if xp_type == "heart":
        user["last_heart"] = now.isoformat()
        user["hearts_today"] = user.get("hearts_today", 0) + 1
    elif xp_type == "like":
        user["last_like"] = now.isoformat()
        user["likes_today"] = user.get("likes_today", 0) + 1
    elif xp_type == "nerd":
        user["last_nerd"] = now.isoformat()
        user["nerds_today"] = user.get("nerds_today", 0) + 1
    
    # Проверяем повышение ранга
    old_symbol = user.get("rank_symbol", "?")
    new_symbol, new_name = get_rank_info(user["xp"])
    
    rank_up = old_symbol != new_symbol
    
    if rank_up:
        user["rank_symbol"] = new_symbol
        user["rank_name"] = new_name
    
    save_data()
    return rank_up, new_name

def is_developer(user_id):
    """Проверка является ли пользователь разработчиком"""
    return str(user_id) in developers

# ========== ОСНОВНЫЕ КОМАНДЫ ==========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начало работы с ботом"""
    keyboard = [[InlineKeyboardButton("🎯 ПРИСОЕДИНИТЬСЯ", callback_data="join")]]
    
    await update.message.reply_text(
        "Приветствуем вас в боте комьюнити «?»!\n"
        "Нажмите кнопку ниже чтобы официально присоединиться",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def join_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка присоединения"""
    query = update.callback_query
    await query.answer()
    
    user = query.from_user
    user_id = str(user.id)
    
    if user_id in users:
        await query.edit_message_text("Вы уже в комьюнити! Используйте /profile")
        return
    
    # Создаем нового пользователя
    users[user_id] = {
        "id": user.id,
        "username": user.username or "",
        "first_name": user.first_name,
        "xp": 0,
        "rank_symbol": "?",
        "rank_name": "Луркер 🕶️",
        "joined": datetime.now().isoformat(),
        "last_heart": None,
        "hearts_today": 0,
        "last_like": None,
        "likes_today": 0,
        "last_nerd": None,
        "nerds_today": 0,
        "warns": []
    }
    
    save_data()
    
    message = f"""🎉🎉 ПОЗДРАВЛЯЕМ, ВЫ ОФИЦИАЛЬНО ПРИСОЕДИНИЛИСЬ 🎉🎉

🎴 Ваша карточка:
👤 Имя: {user.first_name}
🏷️ Ранг: ? — Луркер 🕶️
⭐ Опыт: 0 XP

Чтобы повысить ранг, присоединяйтесь в чат и изучите правила:
{RULES_LINK}"""
    
    keyboard = [[InlineKeyboardButton("📜 Правила", url=RULES_LINK)]]
    
    await query.edit_message_text(
        text=message,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать профиль"""
    user_id = str(update.effective_user.id)
    
    if user_id not in users:
        await update.message.reply_text("Сначала присоединитесь через /start")
        return
    
    user = users[user_id]
    
    next_rank = None
    for rank in RANKS:
        if rank["xp"] > user["xp"]:
            next_rank = rank
            break
    
    needed_xp = next_rank["xp"] - user["xp"] if next_rank else "МАКС"
    
    message = f"""🎴 ВАША КАРТОЧКА:

👤 Имя: {user['first_name']}
🏷️ Ранг: {user['rank_symbol']} — {user['rank_name']}
⭐ Опыт: {user['xp']} XP
📈 До след. ранга: {needed_xp} XP
📅 В комьюнити с: {datetime.fromisoformat(user['joined']).strftime('%d.%m.%Y')}
⚠️ Варнов: {len(user['warns'])}"""
    
    await update.message.reply_text(message)

async def heart_xp(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка ❤️"""
    user_id = str(update.effective_user.id)
    
    if user_id not in users:
        await update.message.reply_text("Сначала /start")
        return
    
    can, error = can_add_xp(users[user_id], "heart")
    if not can:
        await update.message.reply_text(f"❌ {error}")
        return
    
    rank_up, new_rank = add_xp(user_id, 1, "heart")
    
    response = f"❤️ +1 XP!\nВсего XP: {users[user_id]['xp']}"
    
    if rank_up:
        response = f"🎉 ПОЗДРАВЛЯЕМ! Новый ранг: {new_rank}\n" + response
    
    await update.message.reply_text(response)

async def like_xp(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка 👍"""
    user_id = str(update.effective_user.id)
    
    if user_id not in users:
        await update.message.reply_text("Сначала /start")
        return
    
    can, error = can_add_xp(users[user_id], "like")
    if not can:
        await update.message.reply_text(f"❌ {error}")
        return
    
    rank_up, new_rank = add_xp(user_id, 5, "like")
    
    response = f"👍 +5 XP!\nВсего XP: {users[user_id]['xp']}"
    
    if rank_up:
        response = f"🎉 ПОЗДРАВЛЯЕМ! Новый ранг: {new_rank}\n" + response
    
    await update.message.reply_text(response)

async def nerd_xp(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка 🤓"""
    user_id = str(update.effective_user.id)
    
    if user_id not in users:
        await update.message.reply_text("Сначала /start")
        return
    
    can, error = can_add_xp(users[user_id], "nerd")
    if not can:
        await update.message.reply_text(f"❌ {error}")
        return
    
    rank_up, new_rank = add_xp(user_id, 10, "nerd")
    
    response = f"🤓 +10 XP!\nВсего XP: {users[user_id]['xp']}"
    
    if rank_up:
        response = f"🎉 ПОЗДРАВЛЯЕМ! Новый ранг: {new_rank}\n" + response
    
    await update.message.reply_text(response)

async def rules_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать правила"""
    await update.message.reply_text(
        f"📜 Правила нашего комьюнити:\n\n"
        f"1. Уважайте друг друга\n"
        f"2. Не спамьте\n"
        f"3. Соблюдайте тематику\n"
        f"4. Администрация имеет последнее слово\n\n"
        f"Полные правила: {RULES_LINK}"
    )

async def helpadmin_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Позвать администратора"""
    user_id = str(update.effective_user.id)
    
    if user_id not in users:
        await update.message.reply_text("Сначала /start")
        return
    
    user = users[user_id]
    
    # Только для рангов 1-7
    if user["xp"] >= 1200:
        await update.message.reply_text("Вы администратор! Можете помогать другим.")
        return
    
    await update.message.reply_text(
        f"🆘 Ваш запрос отправлен администраторам!\n"
        f"Ожидайте ответа в чате: {CHAT_LINK}"
    )

async def mute_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Мут пользователя"""
    user_id = str(update.effective_user.id)
    
    if user_id not in users:
        await update.message.reply_text("Сначала /start")
        return
    
    user = users[user_id]
    
    # Определяем время мута в зависимости от ранга
    if user["xp"] < 300:  # Ранги 1-3
        time_str = "5 минут"
    elif user["xp"] < 1700:  # Ранги 4-7
        time_str = "30 минут"
    else:  # Ранги 8+
        time_str = "7 дней"
    
    if not context.args:
        await update.message.reply_text(f"Использование: /mute @username причина\nВы можете мутить на: {time_str}")
        return
    
    await update.message.reply_text(f"🔇 Мут выдан на {time_str}")

async def warn_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Выдать предупреждение"""
    user_id = str(update.effective_user.id)
    
    if user_id not in users:
        await update.message.reply_text("Сначала /start")
        return
    
    user = users[user_id]
    
    # Только с 4 ранга
    if user["xp"] < 300:
        await update.message.reply_text("⚠️ Доступно с 4 ранга (Мемолог)")
        return
    
    if not context.args:
        await update.message.reply_text("Использование: /warn @username причина")
        return
    
    await update.message.reply_text("⚠️ Предупреждение выдано")

async def ban_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Бан пользователя"""
    user_id = str(update.effective_user.id)
    
    if user_id not in users:
        await update.message.reply_text("Сначала /start")
        return
    
    user = users[user_id]
    
    # Только с 8 ранга
    if user["xp"] < 1700:
        await update.message.reply_text("🔨 Доступно с 8 ранга (Интегратор)")
        return
    
    if not context.args:
        await update.message.reply_text("Использование: /ban @username причина")
        return
    
    await update.message.reply_text("🔨 Бан на 30 дней")

async def chat_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Ссылка на чат"""
    await update.message.reply_text(
        f"💬 Основной чат комьюнити:\n{CHAT_LINK}\n\n"
        f"📜 Правила:\n{RULES_LINK}"
    )

# ========== КОМАНДЫ РАЗРАБОТЧИКА ==========
async def razrab_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда разработчика"""
    user_id = str(update.effective_user.id)
    
    if not context.args:
        await update.message.reply_text(
            "🔐 Ты разработчик?\n"
            "Тогда введи секретный код:\n"
            "/razrab [код]"
        )
        return
    
    code = context.args[0]
    
    if code == DEVELOPER_CODE:
        # Добавляем пользователя в разработчики
        developers[user_id] = {
            "id": update.effective_user.id,
            "username": update.effective_user.username or "",
            "first_name": update.effective_user.first_name,
            "activated": datetime.now().isoformat(),
            "access_level": "developer"
        }
        save_developers()
        
        await update.message.reply_text(
            "✅ Доступ разработчика активирован!\n\n"
            "🛠️ Доступные команды:\n"
            "/dev_stats - статистика бота\n"
            "/dev_users - список пользователей\n"
            "/dev_givexp @user количество - выдать XP\n"
            "/dev_setrank @user номер_ранга - установить ранг\n"
            "/dev_warn @user причина - выдать варн\n"
            "/dev_unwarn @user - снять варн\n"
            "/dev_mute @user время причина - мут\n"
            "/dev_unmute @user - размут\n"
            "/dev_reset - сброс дневных счетчиков\n"
        )
    else:
        await update.message.reply_text("❌ Неверный код!")

async def dev_stats_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Статистика бота"""
    user_id = str(update.effective_user.id)
    
    if not is_developer(user_id):
        await update.message.reply_text("❌ Требуется доступ разработчика!")
        return
    
    # Собираем статистику
    total_users = len(users)
    total_developers = len(developers)
    
    # Распределение по рангам
    rank_counts = {}
    for rank in RANKS:
        rank_counts[rank["name"]] = 0
    
    for user in users.values():
        rank_symbol = user.get("rank_symbol", "?")
        for rank in RANKS:
            if rank["symbol"] == rank_symbol:
                rank_counts[rank["name"]] += 1
                break
    
    # Статистика варнов
    total_warns = 0
    for user in users.values():
        total_warns += len(user.get("warns", []))
    
    # XP статистика
    total_xp = sum(user.get("xp", 0) for user in users.values())
    avg_xp = total_xp / total_users if total_users > 0 else 0
    
    message = (
        "📊 СТАТИСТИКА БОТА\n\n"
        f"👥 Пользователей: {total_users}\n"
        f"🛠️ Разработчиков: {total_developers}\n"
        f"⭐ Всего XP: {total_xp}\n"
        f"📈 Средний XP: {avg_xp:.1f}\n"
        f"⚠️ Всего варнов: {total_warns}\n\n"
        "📋 Распределение по рангам:\n"
    )
    
    for rank_name, count in rank_counts.items():
        if count > 0:
            percentage = (count / total_users * 100) if total_users > 0 else 0
            message += f"{rank_name}: {count} ({percentage:.1f}%)\n"
    
    await update.message.reply_text(message)

async def dev_users_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Список пользователей"""
    user_id = str(update.effective_user.id)
    
    if not is_developer(user_id):
        await update.message.reply_text("❌ Требуется доступ разработчика!")
        return
    
    if not users:
        await update.message.reply_text("📭 Нет пользователей")
        return
    
    # Сортировка по XP
    sorted_users = sorted(users.items(), key=lambda x: x[1].get("xp", 0), reverse=True)
    
    message = "👥 ТОП-20 ПОЛЬЗОВАТЕЛЕЙ:\n\n"
    
    for i, (uid, user) in enumerate(sorted_users[:20], 1):
        username = user.get("username", "без username")
        first_name = user.get("first_name", "NoName")
        xp = user.get("xp", 0)
        rank_name = user.get("rank_name", "Луркер 🕶️")
        warns = len(user.get("warns", []))
        
        message += f"{i}. {first_name} (@{username})\n"
        message += f"   ⭐ {xp} XP | {rank_name} | ⚠️ {warns}\n"
    
    await update.message.reply_text(message)

async def dev_givexp_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Выдать XP пользователю"""
    user_id = str(update.effective_user.id)
    
    if not is_developer(user_id):
        await update.message.reply_text("❌ Требуется доступ разработчика!")
        return
    
    if len(context.args) < 2:
        await update.message.reply_text("Использование: /dev_givexp @user количество")
        return
    
    target_username = context.args[0].replace("@", "")
    try:
        xp_amount = int(context.args[1])
    except ValueError:
        await update.message.reply_text("❌ Количество должно быть числом!")
        return
    
    if xp_amount <= 0:
        await update.message.reply_text("❌ Количество должно быть положительным!")
        return
    
    # Поиск пользователя
    target_user = None
    target_user_id = None
    
    for uid, user in users.items():
        if user.get("username") == target_username:
            target_user = user
            target_user_id = uid
            break
    
    if not target_user:
        await update.message.reply_text("❌ Пользователь не найден!")
        return
    
    # Выдаем XP
    old_xp = target_user.get("xp", 0)
    old_rank = target_user.get("rank_name", "")
    
    target_user["xp"] += xp_amount
    
    # Проверяем повышение ранга
    new_symbol, new_name = get_rank_info(target_user["xp"])
    rank_up = target_user.get("rank_symbol", "?") != new_symbol
    
    if rank_up:
        target_user["rank_symbol"] = new_symbol
        target_user["rank_name"] = new_name
    
    save_data()
    
    message = (
        f"✅ Выдано {xp_amount} XP пользователю @{target_username}\n\n"
        f"📊 До: {old_xp} XP ({old_rank})\n"
        f"📊 После: {target_user['xp']} XP ({new_name})"
    )
    
    if rank_up:
        message += f"\n🎉 Повышение ранга: {new_name}"
    
    await update.message.reply_text(message)

async def dev_setrank_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Установить ранг пользователю"""
    user_id = str(update.effective_user.id)
    
    if not is_developer(user_id):
        await update.message.reply_text("❌ Требуется доступ разработчика!")
        return
    
    if len(context.args) < 2:
        ranks_list = "\n".join([f"{i+1}. {r['symbol']} — {r['name']}" for i, r in enumerate(RANKS)])
        await update.message.reply_text(
            f"Использование: /dev_setrank @user номер_ранга\n\n"
            f"Доступные ранги:\n{ranks_list}"
        )
        return
    
    target_username = context.args[0].replace("@", "")
    try:
        rank_num = int(context.args[1]) - 1
    except ValueError:
        await update.message.reply_text("❌ Номер ранга должен быть числом!")
        return
    
    if rank_num < 0 or rank_num >= len(RANKS):
        await update.message.reply_text(f"❌ Номер ранга должен быть от 1 до {len(RANKS)}")
        return
    
    # Поиск пользователя
    target_user = None
    for uid, user in users.items():
        if user.get("username") == target_username:
            target_user = user
            break
    
    if not target_user:
        await update.message.reply_text("❌ Пользователь не найден!")
        return
    
    # Устанавливаем ранг
    rank = RANKS[rank_num]
    old_rank = target_user.get("rank_name", "")
    
    target_user["rank_symbol"] = rank["symbol"]
    target_user["rank_name"] = rank["name"]
    target_user["xp"] = rank["xp"]  # Устанавливаем XP соответствующие рангу
    
    save_data()
    
    await update.message.reply_text(
        f"✅ Установлен ранг {rank['symbol']} — {rank['name']} для @{target_username}\n"
        f"📊 XP установлено: {rank['xp']}"
    )

async def dev_warn_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Выдать варн (разработчик)"""
    user_id = str(update.effective_user.id)
    
    if not is_developer(user_id):
        await update.message.reply_text("❌ Требуется доступ разработчика!")
        return
    
    if len(context.args) < 2:
        await update.message.reply_text("Использование: /dev_warn @user причина")
        return
    
    target_username = context.args[0].replace("@", "")
    reason = " ".join(context.args[1:])
    
    # Поиск пользователя
    target_user = None
    target_user_id = None
    
    for uid, user in users.items():
        if user.get("username") == target_username:
            target_user = user
            target_user_id = uid
            break
    
    if not target_user:
        await update.message.reply_text("❌ Пользователь не найден!")
        return
    
    # Добавляем варн
    warn_data = {
        "reason": reason,
        "time": datetime.now().isoformat(),
        "admin": f"dev:{update.effective_user.username}",
        "type": "developer"
    }
    
    target_user.setdefault("warns", []).append(warn_data)
    save_data()
    
    total_warns = len(target_user.get("warns", []))
    
    await update.message.reply_text(
        f"⚠️ Выдан варн пользователю @{target_username}\n"
        f"📝 Причина: {reason}\n"
        f"📊 Всего варнов: {total_warns}"
    )

async def dev_unwarn_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Снять варн"""
    user_id = str(update.effective_user.id)
    
    if not is_developer(user_id):
        await update.message.reply_text("❌ Требуется доступ разработчика!")
        return
    
    if len(context.args) < 1:
        await update.message.reply_text("Использование: /dev_unwarn @user")
        return
    
    target_username = context.args[0].replace("@", "")
    
    # Поиск пользователя
    target_user = None
    for uid, user in users.items():
        if user.get("username") == target_username:
            target_user = user
            break
    
    if not target_user:
        await update.message.reply_text("❌ Пользователь не найден!")
        return
    
    if not target_user.get("warns"):
        await update.message.reply_text(f"✅ У @{target_username} нет варнов")
        return
    
    # Удаляем последний варн
    removed_warn = target_user["warns"].pop()
    save_data()
    
    remaining_warns = len(target_user.get("warns", []))
    
    await update.message.reply_text(
        f"✅ Снят варн с @{target_username}\n"
        f"📝 Причина варна: {removed_warn.get('reason', 'не указана')}\n"
        f"📊 Осталось варнов: {remaining_warns}"
    )

async def dev_mute_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Мут пользователя (разработчик)"""
    user_id = str(update.effective_user.id)
    
    if not is_developer(user_id):
        await update.message.reply_text("❌ Требуется доступ разработчика!")
        return
    
    if len(context.args) < 3:
        await update.message.reply_text("Использование: /dev_mute @user время причина\nПример: /dev_mute @user 60 Спам")
        return
    
    target_username = context.args[0].replace("@", "")
    try:
        mute_minutes = int(context.args[1])
    except ValueError:
        await update.message.reply_text("❌ Время должно быть числом (минуты)!")
        return
    
    reason = " ".join(context.args[2:])
    
    # Поиск пользователя
    target_user = None
    for uid, user in users.items():
        if user.get("username") == target_username:
            target_user = user
            break
    
    if not target_user:
        await update.message.reply_text("❌ Пользователь не найден!")
        return
    
    # Устанавливаем мут
    mute_until = datetime.now() + timedelta(minutes=mute_minutes)
    target_user["muted_until"] = mute_until.isoformat()
    save_data()
    
    await update.message.reply_text(
        f"🔇 Мут пользователю @{target_username}\n"
        f"⏰ На: {mute_minutes} минут\n"
        f"📝 Причина: {reason}\n"
        f"🕒 До: {mute_until.strftime('%d.%m.%Y %H:%M')}"
    )

async def dev_unmute_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Размут пользователя"""
    user_id = str(update.effective_user.id)
    
    if not is_developer(user_id):
        await update.message.reply_text("❌ Требуется доступ разработчика!")
        return
    
    if len(context.args) < 1:
        await update.message.reply_text("Использование: /dev_unmute @user")
        return
    
    target_username = context.args[0].replace("@", "")
    
    # Поиск пользователя
    target_user = None
    for uid, user in users.items():
        if user.get("username") == target_username:
            target_user = user
            break
    
    if not target_user:
        await update.message.reply_text("❌ Пользователь не найден!")
        return
    
    if not target_user.get("muted_until"):
        await update.message.reply_text(f"✅ @{target_username} не в муте")
        return
    
    # Снимаем мут
    old_mute = target_user.pop("muted_until", None)
    save_data()
    
    await update.message.reply_text(f"✅ Пользователь @{target_username} размучен")

async def dev_reset_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Сброс дневных счетчиков"""
    user_id = str(update.effective_user.id)
    
    if not is_developer(user_id):
        await update.message.reply_text("❌ Требуется доступ разработчика!")
        return
    
    reset_daily_counts()
    
    await update.message.reply_text("✅ Дневные счетчики сброшены!")

async def sticker_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка стикеров - антиспам"""
    user_id = str(update.effective_user.id)
    now = datetime.now()
    
    if user_id not in sticker_tracker:
        sticker_tracker[user_id] = {"count": 0, "time": now}
    
    data = sticker_tracker[user_id]
    
    # Если прошла минута, сбрасываем счетчик
    if (now - data["time"]).seconds > 60:
        data["count"] = 1
        data["time"] = now
    else:
        data["count"] += 1
    
    # Если 5 стикеров в минуту - выдать варн
    if data["count"] >= 5 and user_id in users:
        warn_data = {
            "reason": "Спам стикерами (5+ в минуту)",
            "time": now.isoformat(),
            "admin": "SYSTEM"
        }
        
        users[user_id]["warns"].append(warn_data)
        save_data()
        
        await update.message.reply_text(
            f"⚠️ @{update.effective_user.username or 'Пользователь'} "
            f"получил предупреждение за спам стикерами!"
        )
        
        # Сбрасываем счетчик
        data["count"] = 0

# ========== ЗАПУСК БОТА ==========
def main():
    """Основная функция запуска бота"""
    # Загружаем данные
    load_data()
    load_developers()
    
    # Создаем приложение
    app = Application.builder().token(TOKEN).build()
    
    # Добавляем обработчики команд
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("profile", profile))
    app.add_handler(CommandHandler("rules", rules_cmd))
    app.add_handler(CommandHandler("chat", chat_cmd))
    app.add_handler(CommandHandler("helpadmin", helpadmin_cmd))
    app.add_handler(CommandHandler("mute", mute_cmd))
    app.add_handler(CommandHandler("warn", warn_cmd))
    app.add_handler(CommandHandler("ban", ban_cmd))
    
    # Команды разработчика
    app.add_handler(CommandHandler("razrab", razrab_cmd))
    app.add_handler(CommandHandler("dev_stats", dev_stats_cmd))
    app.add_handler(CommandHandler("dev_users", dev_users_cmd))
    app.add_handler(CommandHandler("dev_givexp", dev_givexp_cmd))
    app.add_handler(CommandHandler("dev_setrank", dev_setrank_cmd))
    app.add_handler(CommandHandler("dev_warn", dev_warn_cmd))
    app.add_handler(CommandHandler("dev_unwarn", dev_unwarn_cmd))
    app.add_handler(CommandHandler("dev_mute", dev_mute_cmd))
    app.add_handler(CommandHandler("dev_unmute", dev_unmute_cmd))
    app.add_handler(CommandHandler("dev_reset", dev_reset_cmd))
    
    # Обработчики реакций (эмодзи)
    app.add_handler(MessageHandler(filters.Regex("❤️"), heart_xp))
    app.add_handler(MessageHandler(filters.Regex("👍"), like_xp))
    app.add_handler(MessageHandler(filters.Regex("🤓"), nerd_xp))
    
    # Обработчик стикеров
    app.add_handler(MessageHandler(filters.Sticker.ALL, sticker_handler))
    
    # Callback запросы
    app.add_handler(CallbackQueryHandler(join_callback, pattern="^join$"))
    
    print("🤖 Бот запущен! Нажмите Ctrl+C для остановки.")
    
    # Запускаем бота
    app.run_polling()

if __name__ == "__main__":
    main()
