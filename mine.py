# В начале файла добавить:
from quests import (
    init_user_quests, 
    track_reaction,
    track_warn_given,
    track_punishment_received,
    get_user_quests_display,
    check_quest_completion
)

# В функции join_callback добавить:
users[user_id]["quests"] = init_user_quests(user_id)

# В функциях heart_xp, like_xp, nerd_xp добавить:
user_quests = user.get("quests", {})
if user_quests:
    # Отслеживаем реакцию для заданий
    if xp_type == "heart":
        user_quests = track_reaction(user_quests, "heart")
    elif xp_type == "like":
        user_quests = track_reaction(user_quests, "like")
    elif xp_type == "nerd":
        user_quests = track_reaction(user_quests, "nerd")
    
    user["quests"] = user_quests
    
    # Проверяем выполнение заданий
    updated_quests, rewards = check_quest_completion(user_quests, user["xp"])
    if rewards["xp"] > 0:
        user["xp"] += rewards["xp"]
        user["quests"] = updated_quests
        # Можно показать уведомление о наградах

# В функции warn_cmd (когда выдается варн) добавить:
# Проверяем варн от админа (ранг 4+)
if user["xp"] >= 300:  # Ранг 4 и выше
    user_quests = user.get("quests", {})
    if user_quests:
        user_quests = track_warn_given(user_quests)
        user["quests"] = user_quests

# Добавить новые команды:
async def quests_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    
    if user_id not in users:
        await update.message.reply_text("Сначала присоединитесь через /start")
        return
    
    user = users[user_id]
    user_quests = user.get("quests", {})
    
    if not user_quests:
        user_quests = init_user_quests(user_id, user["xp"])
        users[user_id]["quests"] = user_quests
        save_data()
    
    display_text = get_user_quests_display(user_quests, user["xp"])
    
    await update.message.reply_text(
        display_text,
        parse_mode="Markdown"
    )

async def claim_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    
    if user_id not in users:
        await update.message.reply_text("Сначала присоединитесь через /start")
        return
    
    user = users[user_id]
    user_quests = user.get("quests", {})
    
    if not user_quests:
        await update.message.reply_text("У вас нет заданий для проверки")
        return
    
    # Проверяем выполнение заданий
    updated_quests, rewards = check_quest_completion(user_quests, user["xp"])
    
    if rewards["completed"]:
        # Выдаем награды
        user["xp"] += rewards["xp"]
        user["quests"] = updated_quests
        
        save_data()
        
        reward_text = f"🎉 **ВЫ ПОЛУЧИЛИ НАГРАДЫ!**\n\n"
        for completed in rewards["completed"]:
            reward_text += f"✅ {completed['name']}: +{completed['xp']} XP, +{completed['bonus']} BP\n"
        
        reward_text += f"\n📊 Всего: **+{rewards['xp']} XP**, **+{rewards['bonus_points']} BP**"
        
        await update.message.reply_text(reward_text, parse_mode="Markdown")
    else:
        await update.message.reply_text(
            "📭 Пока нет выполненных заданий для получения наград\n"
            "Продолжайте выполнять задания из /quests"
        )

# В main() добавить обработчики:
app.add_handler(CommandHandler("quests", quests_cmd))
app.add_handler(CommandHandler("claim", claim_cmd))
