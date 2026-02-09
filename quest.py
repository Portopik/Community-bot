import json
import os
from datetime import datetime, timedelta

# ========== КОНФИГУРАЦИЯ ЗАДАНИЙ ==========
QUEST_CONFIG = {
    # Ежедневные задания для рангов 1-3 (? до ???)
    "daily_rank_1_3": [
        {
            "id": "daily_chat_top3",
            "name": "Общительный 💬",
            "description": "Занять ТОП-3 по сообщениям за день",
            "goal": 3,  # место в топе
            "reward_xp": 30,
            "reward_bonus": 10,
            "type": "chat_ranking",
            "required_rank_min": 0,    # от ? ранга
            "required_rank_max": 150,  # до ??? ранга (150 XP)
            "icon": "💬"
        },
        {
            "id": "daily_heart_giver",
            "name": "Оценщик ❤️",
            "description": "Отправить 3 реакции ❤️ другим пользователям",
            "goal": 3,
            "reward_xp": 25,
            "reward_bonus": 8,
            "type": "hearts_given",
            "required_rank_min": 0,
            "required_rank_max": 150,
            "icon": "❤️"
        },
        {
            "id": "daily_good_behavior",
            "name": "Послушатель 😇",
            "description": "Не получать наказаний целый день",
            "goal": 1,
            "reward_xp": 20,
            "reward_bonus": 5,
            "type": "no_punishment",
            "required_rank_min": 0,
            "required_rank_max": 150,
            "icon": "😇"
        }
    ],
    
    # Ежедневные задания для рангов 4-7 (???? до ???????)
    "daily_rank_4_7": [
        {
            "id": "daily_like_giver",
            "name": "Добряк 👍",
            "description": "Отправить 1 реакцию 👍 пользователю",
            "goal": 1,
            "reward_xp": 40,
            "reward_bonus": 15,
            "type": "likes_given",
            "required_rank_min": 300,   # от ???? ранга
            "required_rank_max": 1200,  # до ??????? ранга
            "icon": "👍"
        },
        {
            "id": "daily_warn_giver",
            "name": "Надзиратель ⚠️",
            "description": "Выдать варн за нарушение правил",
            "goal": 1,
            "reward_xp": 50,
            "reward_bonus": 20,
            "type": "warns_given",
            "required_rank_min": 300,
            "required_rank_max": 1200,
            "icon": "⚠️"
        },
        {
            "id": "daily_help_newbies",
            "name": "Наставник 👨‍🏫",
            "description": "Помочь 2 новичкам (ответить на вопросы)",
            "goal": 2,
            "reward_xp": 45,
            "reward_bonus": 18,
            "type": "help_given",
            "required_rank_min": 300,
            "required_rank_max": 1200,
            "icon": "👨‍🏫"
        }
    ],
    
    # Ежедневные задания для рангов 7-9 (??????? до ?????????)
    "daily_rank_7_9": [
        {
            "id": "daily_nerd_giver",
            "name": "Мудрец 🤓",
            "description": "Отправить реакцию 🤓 пользователю",
            "goal": 1,
            "reward_xp": 60,
            "reward_bonus": 25,
            "type": "nerds_given",
            "required_rank_min": 1200,   # от ??????? ранга
            "required_rank_max": 2300,   # до ????????? ранга
            "icon": "🤓"
        },
        {
            "id": "daily_content_creator",
            "name": "Контент-мейкер 🎨",
            "description": "Создать полезный контент для сообщества",
            "goal": 1,
            "reward_xp": 70,
            "reward_bonus": 30,
            "type": "content_created",
            "required_rank_min": 1200,
            "required_rank_max": 2300,
            "icon": "🎨"
        },
        {
            "id": "daily_community_leader",
            "name": "Лидер сообщества 👑",
            "description": "Провести мини-ивент или активность",
            "goal": 1,
            "reward_xp": 80,
            "reward_bonus": 35,
            "type": "event_hosted",
            "required_rank_min": 1200,
            "required_rank_max": 2300,
            "icon": "👑"
        },
        {
            "id": "daily_conflict_resolver",
            "name": "Миротворец 🕊️",
            "description": "Урегулировать конфликт в чате",
            "goal": 1,
            "reward_xp": 65,
            "reward_bonus": 28,
            "type": "conflicts_resolved",
            "required_rank_min": 1200,
            "required_rank_max": 2300,
            "icon": "🕊️"
        },
        {
            "id": "daily_idea_generator",
            "name": "Иноватор 💡",
            "description": "Предложить улучшение для сообщества",
            "goal": 1,
            "reward_xp": 55,
            "reward_bonus": 22,
            "type": "ideas_suggested",
            "required_rank_min": 1200,
            "required_rank_max": 2300,
            "icon": "💡"
        }
    ],
    
    # Ежедневные задания для ранга 10 (??????????)
    "daily_rank_10": [
        {
            "id": "daily_legend_activity",
            "name": "Легенда дня 🌟",
            "description": "Быть самым активным ОГ за день",
            "goal": 1,
            "reward_xp": 100,
            "reward_bonus": 50,
            "type": "top_og",
            "required_rank_min": 3000,  # от ?????????? ранга
            "required_rank_max": 10000,
            "icon": "🌟"
        },
        {
            "id": "daily_community_builder",
            "name": "Строитель сообщества 🏗️",
            "description": "Пригласить 3 новых активных участников",
            "goal": 3,
            "reward_xp": 120,
            "reward_bonus": 60,
            "type": "invites_sent",
            "required_rank_min": 3000,
            "required_rank_max": 10000,
            "icon": "🏗️"
        },
        {
            "id": "daily_strategist",
            "name": "Стратег ♟️",
            "description": "Разработать стратегию развития",
            "goal": 1,
            "reward_xp": 150,
            "reward_bonus": 75,
            "type": "strategy_created",
            "required_rank_min": 3000,
            "required_rank_max": 10000,
            "icon": "♟️"
        }
    ]
}

# ========== ФУНКЦИИ ДЛЯ РАБОТЫ С ЗАДАНИЯМИ ==========
def init_user_quests(user_id, xp=0):
    """Инициализировать задания для нового пользователя"""
    return {
        "daily_progress": {
            "hearts_given": 0,      # ❤️ отправленные
            "likes_given": 0,       # 👍 отправленные
            "nerds_given": 0,       # 🤓 отправленные
            "warns_given": 0,       # ⚠️ выданные
            "help_given": 0,        # помощь новичкам
            "content_created": 0,   # созданный контент
            "event_hosted": 0,      # проведенные ивенты
            "conflicts_resolved": 0,# разрешенные конфликты
            "ideas_suggested": 0,   # предложенные идеи
            "invites_sent": 0,      # отправленные приглашения
            "strategy_created": 0,  # созданные стратегии
            "messages_today": 0,    # сообщений сегодня
            "punishments_received": 0 # полученные наказания
        },
        "daily_completed": [],      # выполненные сегодня задания
        "total_completed": [],      # всего выполненных заданий
        "last_daily_reset": datetime.now().isoformat(),
        "bonus_points": 0,
        "total_xp_from_quests": 0,
        "rank_when_joined": xp
    }

def save_quests_data(data, filename="data/quests_data.json"):
    """Сохранить данные заданий"""
    os.makedirs("data", exist_ok=True)
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_quests_data(filename="data/quests_data.json"):
    """Загрузить данные заданий"""
    if os.path.exists(filename):
        try:
            with open(filename, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {}
    return {}

def get_quests_for_rank(xp):
    """Получить доступные задания для ранга пользователя"""
    available_quests = []
    
    # Определяем группу заданий по XP
    if xp < 300:  # Ранги 1-3
        quest_groups = ["daily_rank_1_3"]
    elif xp < 1200:  # Ранги 4-7
        quest_groups = ["daily_rank_1_3", "daily_rank_4_7"]
    elif xp < 3000:  # Ранги 7-9
        quest_groups = ["daily_rank_1_3", "daily_rank_4_7", "daily_rank_7_9"]
    else:  # Ранг 10
        quest_groups = ["daily_rank_1_3", "daily_rank_4_7", "daily_rank_7_9", "daily_rank_10"]
    
    # Собираем все доступные задания
    for group in quest_groups:
        available_quests.extend(QUEST_CONFIG.get(group, []))
    
    return available_quests

def check_daily_reset(user_quests):
    """Проверить и сбросить ежедневные задания если нужно"""
    last_reset_str = user_quests.get("last_daily_reset")
    if last_reset_str:
        last_reset = datetime.fromisoformat(last_reset_str)
        if (datetime.now() - last_reset).days >= 1:
            # Сброс ежедневного прогресса
            user_quests["daily_progress"] = {
                "hearts_given": 0,
                "likes_given": 0,
                "nerds_given": 0,
                "warns_given": 0,
                "help_given": 0,
                "content_created": 0,
                "event_hosted": 0,
                "conflicts_resolved": 0,
                "ideas_suggested": 0,
                "invites_sent": 0,
                "strategy_created": 0,
                "messages_today": 0,
                "punishments_received": 0
            }
            user_quests["daily_completed"] = []
            user_quests["last_daily_reset"] = datetime.now().isoformat()
    
    return user_quests

def update_quest_progress(user_quests, progress_type, amount=1):
    """Обновить прогресс заданий"""
    if progress_type in user_quests["daily_progress"]:
        user_quests["daily_progress"][progress_type] += amount
    
    return user_quests

def check_quest_completion(user_quests, user_xp, daily_messages_rank=None):
    """Проверить выполнение заданий и выдать награды"""
    rewards = {"xp": 0, "bonus_points": 0, "completed": []}
    
    # Получаем доступные задания для ранга
    available_quests = get_quests_for_rank(user_xp)
    
    for quest in available_quests:
        # Пропускаем уже выполненные сегодня
        if quest["id"] in user_quests.get("daily_completed", []):
            continue
        
        # Проверяем выполнение по типу задания
        completed = False
        progress = 0
        
        if quest["type"] == "hearts_given":
            progress = user_quests["daily_progress"].get("hearts_given", 0)
            completed = progress >= quest["goal"]
        
        elif quest["type"] == "likes_given":
            progress = user_quests["daily_progress"].get("likes_given", 0)
            completed = progress >= quest["goal"]
        
        elif quest["type"] == "nerds_given":
            progress = user_quests["daily_progress"].get("nerds_given", 0)
            completed = progress >= quest["goal"]
        
        elif quest["type"] == "warns_given":
            progress = user_quests["daily_progress"].get("warns_given", 0)
            completed = progress >= quest["goal"]
        
        elif quest["type"] == "help_given":
            progress = user_quests["daily_progress"].get("help_given", 0)
            completed = progress >= quest["goal"]
        
        elif quest["type"] == "content_created":
            progress = user_quests["daily_progress"].get("content_created", 0)
            completed = progress >= quest["goal"]
        
        elif quest["type"] == "event_hosted":
            progress = user_quests["daily_progress"].get("event_hosted", 0)
            completed = progress >= quest["goal"]
        
        elif quest["type"] == "conflicts_resolved":
            progress = user_quests["daily_progress"].get("conflicts_resolved", 0)
            completed = progress >= quest["goal"]
        
        elif quest["type"] == "ideas_suggested":
            progress = user_quests["daily_progress"].get("ideas_suggested", 0)
            completed = progress >= quest["goal"]
        
        elif quest["type"] == "invites_sent":
            progress = user_quests["daily_progress"].get("invites_sent", 0)
            completed = progress >= quest["goal"]
        
        elif quest["type"] == "strategy_created":
            progress = user_quests["daily_progress"].get("strategy_created", 0)
            completed = progress >= quest["goal"]
        
        elif quest["type"] == "no_punishment":
            progress = user_quests["daily_progress"].get("punishments_received", 0)
            completed = progress == 0  # Ни одного наказания
        
        elif quest["type"] == "chat_ranking":
            # Для этого задания нужны данные о ранге по сообщениям
            if daily_messages_rank and daily_messages_rank <= quest["goal"]:
                completed = True
        
        elif quest["type"] == "top_og":
            # Для ОГ - быть самым активным среди ОГ
            # Здесь нужна дополнительная логика отслеживания активности ОГ
            completed = False  # Заглушка
        
        if completed:
            # Выдаем награды
            rewards["xp"] += quest["reward_xp"]
            rewards["bonus_points"] += quest["reward_bonus"]
            rewards["completed"].append({
                "id": quest["id"],
                "name": quest["name"],
                "xp": quest["reward_xp"],
                "bonus": quest["reward_bonus"]
            })
            
            # Добавляем в список выполненных
            if "daily_completed" not in user_quests:
                user_quests["daily_completed"] = []
            user_quests["daily_completed"].append(quest["id"])
            
            # Общий счетчик выполненных
            if "total_completed" not in user_quests:
                user_quests["total_completed"] = []
            if quest["id"] not in user_quests["total_completed"]:
                user_quests["total_completed"].append(quest["id"])
    
    # Обновляем общие счетчики
    user_quests["bonus_points"] = user_quests.get("bonus_points", 0) + rewards["bonus_points"]
    user_quests["total_xp_from_quests"] = user_quests.get("total_xp_from_quests", 0) + rewards["xp"]
    
    return user_quests, rewards

def get_user_quests_display(user_quests, user_xp):
    """Получить текстовое представление заданий пользователя"""
    if not user_quests:
        return "🎯 Задания не инициализированы. Используйте /start"
    
    # Проверяем сброс
    user_quests = check_daily_reset(user_quests)
    
    # Получаем доступные задания
    available_quests = get_quests_for_rank(user_xp)
    
    # Группируем задания по рангам
    quests_by_rank = {
        "1-3": [q for q in available_quests if q["required_rank_max"] <= 150],
        "4-7": [q for q in available_quests if 300 <= q["required_rank_max"] <= 1200],
        "7-9": [q for q in available_quests if 1200 <= q["required_rank_max"] <= 2300],
        "10": [q for q in available_quests if q["required_rank_min"] >= 3000]
    }
    
    text = "🎯 **ЕЖЕДНЕВНЫЕ ЗАДАНИЯ**\n\n"
    
    # Определяем текущую группу рангов
    if user_xp < 300:
        current_group = "1-3"
        rank_name = "Ранги 1-3"
    elif user_xp < 1200:
        current_group = "4-7"
        rank_name = "Ранги 4-7"
    elif user_xp < 3000:
        current_group = "7-9"
        rank_name = "Ранги 7-9"
    else:
        current_group = "10"
        rank_name = "Ранг 10"
    
    text += f"📊 **Ваша группа:** {rank_name}\n"
    text += f"⏰ **Сброс через:** {get_time_until_reset(user_quests)}\n\n"
    
    # Показываем задания для текущей группы
    quests_to_show = quests_by_rank.get(current_group, [])
    
    if not quests_to_show:
        text += "📭 Нет доступных заданий для вашего ранга\n"
    else:
        for quest in quests_to_show:
            completed = quest["id"] in user_quests.get("daily_completed", [])
            
            if completed:
                text += f"✅ **{quest['icon']} {quest['name']}**\n"
            else:
                progress = user_quests["daily_progress"].get(quest["type"], 0)
                
                # Особые случаи отображения прогресса
                if quest["type"] == "no_punishment":
                    if user_quests["daily_progress"].get("punishments_received", 0) == 0:
                        status = "✅ Нет наказаний"
                    else:
                        status = "❌ Были наказания"
                    text += f"⏳ **{quest['icon']} {quest['name']}** - {status}\n"
                
                elif quest["type"] == "chat_ranking":
                    text += f"⏳ **{quest['icon']} {quest['name']}**\n"
                    text += f"   _{quest['description']}_\n"
                
                else:
                    text += f"⏳ **{quest['icon']} {quest['name']}** - {progress}/{quest['goal']}\n"
                    text += f"   _{quest['description']}_\n"
                
                text += f"   🎁 **{quest['reward_xp']} XP** + **{quest['reward_bonus']} BP**\n"
            
            text += "\n"
    
    # Статистика
    completed_today = len(user_quests.get("daily_completed", []))
    total_completed = len(user_quests.get("total_completed", []))
    bonus_points = user_quests.get("bonus_points", 0)
    
    text += "📈 **СТАТИСТИКА:**\n"
    text += f"✅ Выполнено сегодня: **{completed_today}**\n"
    text += f"🏆 Всего выполнено: **{total_completed}**\n"
    text += f"💎 Бонусных очков: **{bonus_points} BP**\n"
    text += f"⭐ Всего XP с заданий: **{user_quests.get('total_xp_from_quests', 0)}**"
    
    return text

def get_time_until_reset(user_quests):
    """Получить время до сброса заданий"""
    last_reset_str = user_quests.get("last_daily_reset")
    if not last_reset_str:
        return "Ошибка времени"
    
    last_reset = datetime.fromisoformat(last_reset_str)
    next_reset = last_reset + timedelta(days=1)
    time_left = next_reset - datetime.now()
    
    if time_left.total_seconds() <= 0:
        return "Скоро сброс!"
    
    hours = time_left.seconds // 3600
    minutes = (time_left.seconds % 3600) // 60
    
    return f"{hours}ч {minutes}м"

# ========== ИНТЕГРАЦИЯ С ОСНОВНЫМ БОТОМ ==========
def track_reaction(user_quests, reaction_type):
    """Отслеживание отправленных реакций"""
    if reaction_type == "heart":
        user_quests = update_quest_progress(user_quests, "hearts_given")
    elif reaction_type == "like":
        user_quests = update_quest_progress(user_quests, "likes_given")
    elif reaction_type == "nerd":
        user_quests = update_quest_progress(user_quests, "nerds_given")
    
    return user_quests

def track_warn_given(user_quests):
    """Отслеживание выданных варнов"""
    user_quests = update_quest_progress(user_quests, "warns_given")
    return user_quests

def track_punishment_received(user_quests):
    """Отслеживание полученных наказаний"""
    user_quests = update_quest_progress(user_quests, "punishments_received")
    return user_quests

def track_help_given(user_quests):
    """Отслеживание помощи новичкам"""
    user_quests = update_quest_progress(user_quests, "help_given")
    return user_quests

def track_content_created(user_quests):
    """Отслеживание созданного контента"""
    user_quests = update_quest_progress(user_quests, "content_created")
    return user_quests

def get_quest_commands():
    """Возвращает команды для заданий"""
    return {
        "quests": "Показать задания",
        "claim": "Получить награды",
        "queststats": "Статистика заданий"
}
