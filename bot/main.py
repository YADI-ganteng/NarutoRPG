#!/usr/bin/env python
"""NarutoRPG Bot - Game RPG Naruto di Telegram"""

import asyncio
import json
import os
import random
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# ==================== CONFIG ====================
BOT_TOKEN = os.getenv('BOT_TOKEN', '8835865194:AAFtF9ZoNCoK1HtlF1_jEx29l75Hjxd1iko')
DATA_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'players.json')

# ==================== DATABASE ====================
def load_data():
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {}

def save_data(data):
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

players = load_data()

# ==================== KARAKTER ====================
characters = {
    'naruto': {'name': 'Naruto Uzumaki', 'emoji': '🍥', 'hp': 150, 'attack': 30, 'defense': 20, 'speed': 25, 'jutsu': 'Rasengan', 'jutsu_damage': 50, 'chakra': 100},
    'sasuke': {'name': 'Sasuke Uchiha', 'emoji': '⚡', 'hp': 140, 'attack': 35, 'defense': 18, 'speed': 30, 'jutsu': 'Chidori', 'jutsu_damage': 55, 'chakra': 90},
    'sakura': {'name': 'Sakura Haruno', 'emoji': '🌸', 'hp': 160, 'attack': 25, 'defense': 25, 'speed': 20, 'jutsu': 'Byakugou', 'jutsu_damage': 45, 'chakra': 110},
    'kakashi': {'name': 'Kakashi Hatake', 'emoji': '📖', 'hp': 145, 'attack': 32, 'defense': 22, 'speed': 28, 'jutsu': 'Chidori', 'jutsu_damage': 52, 'chakra': 95},
    'gaara': {'name': 'Gaara', 'emoji': '🏜️', 'hp': 170, 'attack': 28, 'defense': 30, 'speed': 15, 'jutsu': 'Sand Burial', 'jutsu_damage': 48, 'chakra': 85}
}

# ==================== MUSUH ====================
enemies = [
    {'name': 'Zabuza Momochi', 'emoji': '🗡️', 'hp': 100, 'attack': 20, 'exp': 30, 'coins': 15, 'level': 1},
    {'name': 'Orochimaru', 'emoji': '🐍', 'hp': 120, 'attack': 25, 'exp': 40, 'coins': 20, 'level': 2},
    {'name': 'Itachi Uchiha', 'emoji': '👁️', 'hp': 150, 'attack': 35, 'exp': 60, 'coins': 30, 'level': 3},
    {'name': 'Pain', 'emoji': '💀', 'hp': 180, 'attack': 40, 'exp': 80, 'coins': 40, 'level': 4},
    {'name': 'Madara Uchiha', 'emoji': '🔥', 'hp': 250, 'attack': 50, 'exp': 150, 'coins': 80, 'level': 5},
    {'name': 'Kaguya', 'emoji': '🌙', 'hp': 350, 'attack': 60, 'exp': 300, 'coins': 150, 'level': 6}
]

# ==================== GAME STATE ====================
active_battles = {}

# ==================== HANDLERS ====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    if user_id not in players:
        players[user_id] = {'name': update.effective_user.first_name, 'level': 1, 'exp': 0, 'coins': 100, 'character': None, 'wins': 0, 'losses': 0, 'inventory': []}
        save_data(players)
    
    keyboard = [
        [InlineKeyboardButton("🎭 Pilih Karakter", callback_data='choose_character')],
        [InlineKeyboardButton("⚔️ Battle", callback_data='battle_start')],
        [InlineKeyboardButton("📊 Status", callback_data='status')],
        [InlineKeyboardButton("🏆 Ranking", callback_data='ranking')],
        [InlineKeyboardButton("📜 Cara Main", callback_data='help')]
    ]
    
    await update.message.reply_text(
        f"🍥 *NARUTO RPG*\n\n"
        f"Selamat datang {update.effective_user.first_name}!\n"
        f"Pilih menu untuk mulai petualangan ninja!",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

async def choose_character(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = []
    for key, char in characters.items():
        keyboard.append([InlineKeyboardButton(f"{char['emoji']} {char['name']}", callback_data=f'char_{key}')])
    await query.edit_message_text(
        "🎭 *PILIH KARAKTER*\n\nPilih ninja favoritmu:",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

async def select_character(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    char_key = query.data.replace('char_', '')
    user_id = str(update.effective_user.id)
    if char_key in characters:
        players[user_id]['character'] = char_key
        save_data(players)
        char = characters[char_key]
        await query.edit_message_text(
            f"✅ *KARAKTER DIPILIH*\n\n"
            f"{char['emoji']} {char['name']}\n"
            f"❤️ HP: {char['hp']}\n"
            f"⚔️ Attack: {char['attack']}\n"
            f"🛡️ Defense: {char['defense']}\n"
            f"🌀 Jutsu: {char['jutsu']} ({char['jutsu_damage']} DMG)\n\n"
            f"Siap bertarung!",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("⚔️ Mulai Battle", callback_data='battle_start')],
                [InlineKeyboardButton("🔙 Menu", callback_data='back_menu')]
            ]),
            parse_mode='Markdown'
        )

async def battle_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = str(update.effective_user.id)
    
    if not players[user_id].get('character'):
        await query.edit_message_text(
            "❌ *BELUM PUNYA KARAKTER*\n\nPilih karakter dulu!",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🎭 Pilih Karakter", callback_data='choose_character')]]),
            parse_mode='Markdown'
        )
        return
    
    # Pilih musuh sesuai level
    player_level = players[user_id]['level']
    available_enemies = [e for e in enemies if e['level'] <= player_level + 1]
    if not available_enemies:
        available_enemies = enemies[:1]
    
    enemy = random.choice(available_enemies)
    char = characters[players[user_id]['character']]
    
    active_battles[user_id] = {
        'enemy': enemy,
        'player_hp': char['hp'] + (player_level * 10),
        'enemy_hp': enemy['hp'],
        'player_max_hp': char['hp'] + (player_level * 10),
        'turn': 'player'
    }
    
    keyboard = [
        [InlineKeyboardButton("⚔️ Serangan Biasa", callback_data='battle_attack')],
        [InlineKeyboardButton("🌀 Gunakan Jutsu", callback_data='battle_jutsu')],
        [InlineKeyboardButton("🏃 Kabur", callback_data='battle_flee')]
    ]
    
    await query.edit_message_text(
        f"⚔️ *BATTLE DIMULAI!*\n\n"
        f"Anda vs {enemy['emoji']} {enemy['name']}\n\n"
        f"❤️ HP Anda: {active_battles[user_id]['player_hp']}\n"
        f"❤️ HP Musuh: {enemy['hp']}\n\n"
        f"Giliran Anda!",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

async def battle_attack(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = str(update.effective_user.id)
    battle = active_battles.get(user_id)
    if not battle: return
    
    char = characters[players[user_id]['character']]
    damage = random.randint(max(1, char['attack'] - 5), char['attack'] + 5)
    battle['enemy_hp'] -= damage
    
    if battle['enemy_hp'] <= 0:
        await battle_win(update, context, user_id)
        return
    
    enemy_damage = max(1, random.randint(battle['enemy']['attack'] - 5, battle['enemy']['attack'] + 5) - char['defense'] // 5)
    battle['player_hp'] -= enemy_damage
    
    if battle['player_hp'] <= 0:
        await battle_lose(update, context, user_id)
        return
    
    await update_battle_ui(update, context, user_id, f"⚔️ Anda: {damage} DMG | Musuh: {enemy_damage} DMG")

async def battle_jutsu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = str(update.effective_user.id)
    battle = active_battles.get(user_id)
    if not battle: return
    
    char = characters[players[user_id]['character']]
    damage = char['jutsu_damage'] + random.randint(0, 10)
    battle['enemy_hp'] -= damage
    
    if battle['enemy_hp'] <= 0:
        await battle_win(update, context, user_id)
        return
    
    enemy_damage = max(1, random.randint(battle['enemy']['attack'] - 5, battle['enemy']['attack'] + 5) - char['defense'] // 5)
    battle['player_hp'] -= enemy_damage
    
    if battle['player_hp'] <= 0:
        await battle_lose(update, context, user_id)
        return
    
    await update_battle_ui(update, context, user_id, f"🌀 {char['jutsu']}: {damage} DMG | Musuh: {enemy_damage} DMG")

async def battle_flee(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = str(update.effective_user.id)
    del active_battles[user_id]
    await query.edit_message_text(
        "🏃 *KABUR*\n\nKamu berhasil kabur!",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Menu", callback_data='back_menu')]]),
        parse_mode='Markdown'
    )

async def update_battle_ui(update, context, user_id, message):
    query = update.callback_query
    battle = active_battles.get(user_id)
    if not battle: return
    
    keyboard = [
        [InlineKeyboardButton("⚔️ Serangan", callback_data='battle_attack')],
        [InlineKeyboardButton("🌀 Jutsu", callback_data='battle_jutsu')],
        [InlineKeyboardButton("🏃 Kabur", callback_data='battle_flee')]
    ]
    
    await query.edit_message_text(
        f"⚔️ *BATTLE*\n\n{message}\n\n"
        f"❤️ HP Anda: {max(0, battle['player_hp'])}/{battle['player_max_hp']}\n"
        f"❤️ HP Musuh: {max(0, battle['enemy_hp'])}/{battle['enemy']['hp']}",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

async def battle_win(update, context, user_id):
    query = update.callback_query
    battle = active_battles.get(user_id)
    if not battle: return
    enemy = battle['enemy']
    
    players[user_id]['exp'] += enemy['exp']
    players[user_id]['coins'] += enemy['coins']
    players[user_id]['wins'] += 1
    
    exp_needed = players[user_id]['level'] * 100
    leveled_up = False
    while players[user_id]['exp'] >= exp_needed:
        players[user_id]['exp'] -= exp_needed
        players[user_id]['level'] += 1
        players[user_id]['coins'] += players[user_id]['level'] * 50
        exp_needed = players[user_id]['level'] * 100
        leveled_up = True
    
    save_data(players)
    del active_battles[user_id]
    
    text = f"🎉 *MENANG!*\n\nKamu mengalahkan {enemy['emoji']} {enemy['name']}!\n\n⭐ +{enemy['exp']} EXP\n💰 +{enemy['coins']} Coins"
    if leveled_up:
        text += f"\n\n🎊 *LEVEL UP!* Level {players[user_id]['level']}!"
        text += f"\n💰 Bonus: {players[user_id]['level'] * 50} Coins"
    
    await query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("⚔️ Battle Lagi", callback_data='battle_start')],
            [InlineKeyboardButton("🔙 Menu", callback_data='back_menu')]
        ]),
        parse_mode='Markdown'
    )

async def battle_lose(update, context, user_id):
    query = update.callback_query
    battle = active_battles.get(user_id)
    if not battle: return
    
    players[user_id]['losses'] += 1
    save_data(players)
    del active_battles[user_id]
    
    await query.edit_message_text(
        f"💀 *KALAH*\n\nKamu dikalahkan oleh {battle['enemy']['emoji']} {battle['enemy']['name']}!\n\nCoba lagi!",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("⚔️ Battle Lagi", callback_data='battle_start')],
            [InlineKeyboardButton("🔙 Menu", callback_data='back_menu')]
        ]),
        parse_mode='Markdown'
    )

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = str(update.effective_user.id)
    p = players.get(user_id, {})
    char_key = p.get('character')
    char_info = ""
    if char_key in characters:
        char = characters[char_key]
        char_info = f"\n🎭 Karakter: {char['emoji']} {char['name']}"
    
    await query.edit_message_text(
        f"📊 *STATUS*\n\n"
        f"👤 Nama: {p.get('name', 'Unknown')}\n"
        f"📈 Level: {p.get('level', 1)}\n"
        f"⭐ EXP: {p.get('exp', 0)}/{p.get('level', 1)*100}\n"
        f"💰 Coins: {p.get('coins', 0)}\n"
        f"🏆 Menang: {p.get('wins', 0)}\n"
        f"💀 Kalah: {p.get('losses', 0)}"
        f"{char_info}",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Menu", callback_data='back_menu')]]),
        parse_mode='Markdown'
    )

async def ranking(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    sorted_players = sorted(players.items(), key=lambda x: x[1].get('exp', 0), reverse=True)[:10]
    medals = ['🥇', '🥈', '🥉', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣', '🔟']
    
    if sorted_players:
        text = "🏆 *TOP 10 NINJA*\n\n"
        for i, (uid, p) in enumerate(sorted_players):
            text += f"{medals[i]} {p['name']}: Lv {p.get('level',1)} | {p.get('exp',0)} EXP\n"
    else:
        text = "Belum ada ninja. Ayo main!"
    
    await query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Menu", callback_data='back_menu')]]),
        parse_mode='Markdown'
    )

async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "📜 *CARA MAIN*\n\n"
        "1. Pilih karakter ninja\n"
        "2. Battle melawan musuh\n"
        "3. Gunakan serangan atau jutsu\n"
        "4. Menang dapat EXP & Coins\n"
        "5. Level up jadi lebih kuat!",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Menu", callback_data='back_menu')]]),
        parse_mode='Markdown'
    )

async def back_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = [
        [InlineKeyboardButton("🎭 Pilih Karakter", callback_data='choose_character')],
        [InlineKeyboardButton("⚔️ Battle", callback_data='battle_start')],
        [InlineKeyboardButton("📊 Status", callback_data='status')],
        [InlineKeyboardButton("🏆 Ranking", callback_data='ranking')]
    ]
    await query.edit_message_text(
        "🍥 *NARUTO RPG*\n\nPilih menu:",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

# ==================== MAIN ====================
async def main():
    logging.basicConfig(level=logging.INFO)
    app = Application.builder().token(BOT_TOKEN).build()
    
    app.add_handler(CommandHandler('start', start))
    app.add_handler(CallbackQueryHandler(choose_character, pattern='^choose_character$'))
    app.add_handler(CallbackQueryHandler(select_character, pattern='^char_'))
    app.add_handler(CallbackQueryHandler(battle_start, pattern='^battle_start$'))
    app.add_handler(CallbackQueryHandler(battle_attack, pattern='^battle_attack$'))
    app.add_handler(CallbackQueryHandler(battle_jutsu, pattern='^battle_jutsu$'))
    app.add_handler(CallbackQueryHandler(battle_flee, pattern='^battle_flee$'))
    app.add_handler(CallbackQueryHandler(status, pattern='^status$'))
    app.add_handler(CallbackQueryHandler(ranking, pattern='^ranking$'))
    app.add_handler(CallbackQueryHandler(help, pattern='^help$'))
    app.add_handler(CallbackQueryHandler(back_menu, pattern='^back_menu$'))
    
    print("🍥 NarutoRPG Bot berjalan...")
    await app.run_polling()

if __name__ == '__main__':
    asyncio.run(main())
