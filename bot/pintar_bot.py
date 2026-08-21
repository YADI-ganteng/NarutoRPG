#!/usr/bin/env python
"""Si Pintar Bot - AI Chat Bot"""

import os
import json
import random
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler

TOKEN = "8835865194:AAFtF9ZoNCoK1HtlF1_jEx29l75Hjxd1iko"
DATA_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'users.json')

def load_data():
    try:
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    except:
        return {'users': {}}

def save_data(data):
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def ai_response(message):
    message = message.lower()
    
    responses = {
        'halo': ['Halo! 😊', 'Hai! Apa kabar?', 'Hello!'],
        'hai': ['Hai! Senang bertemu!', 'Hello!'],
        'apa kabar': ['Baik! Kamu?', 'Alhamdulillah baik!'],
        'terima kasih': ['Sama-sama! 😊', 'Anytime!'],
        'makasih': ['Sama-sama!', 'Siap!'],
        'nama': ['Nama saya Si Pintar Bot! 🤖'],
        'pintar': ['Makasih! Kamu juga! 😊'],
        'keren': ['Makasih! 😊'],
        'bisa apa': ['Saya bisa ngobrol, main game, kasih jokes!']
    }
    
    for keyword, replies in responses.items():
        if keyword in message:
            return random.choice(replies)
    
    defaults = [
        'Menarik! Ceritakan lebih lanjut!',
        'Oh begitu... Lalu?',
        'Saya paham.',
        'Hmm, menarik! 🤔',
        'Wah, saya jadi penasaran!',
        'Terus gimana?',
        'Boleh tahu lebih detail?'
    ]
    return random.choice(defaults)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    data = load_data()
    user_id = str(user.id)
    
    if user_id not in data['users']:
        data['users'][user_id] = {
            'name': user.first_name,
            'username': user.username or '',
            'level': 1,
            'points': 0,
            'messages': 0,
            'games_played': 0,
            'quizzes_answered': 0,
            'mood': 'netral',
            'last_seen': datetime.now().isoformat()
        }
        save_data(data)
    
    keyboard = [
        [InlineKeyboardButton("🎮 Main Game", callback_data='menu_game')],
        [InlineKeyboardButton("😂 Jokes", callback_data='menu_jokes')],
        [InlineKeyboardButton("📊 Info Saya", callback_data='menu_info')],
        [InlineKeyboardButton("ℹ️ Tentang Bot", callback_data='menu_about')]
    ]
    
    await update.message.reply_text(
        f"👋 *Halo {user.first_name}!*

"
        f"Selamat datang di *Si Pintar Bot*!

"
        f"💬 Saya bisa diajak ngobrol
"
        f"🎮 Main game seru
"
        f"😂 Kasih jokes lucu
"
        f"📊 Track progress kamu

"
        f"Ketik /help untuk semua perintah.",
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = """
📚 *DAFTAR PERINTAH*

*💬 Chat & Info:*
• /start - Mulai bot
• /help - Bantuan ini
• /menu - Menu interaktif
• /about - Tentang bot
• /info - Info pengguna
• /stats - Statistik kamu

*🎮 Game:*
• /game - Menu game
• /tebakangka - Tebak angka 1-10
• /kuis - Kuis pengetahuan

*😂 Hiburan:*
• /jokes - Jokes lucu
• /fakta - Fakta menarik

*📊 Progression:*
• /points - Lihat poin
• /level - Level kamu
• /mood [senang/sedih/bosan] - Set mood

*🕐 Waktu:*
• /waktu - Jam sekarang
• /tanggal - Tanggal hari ini
"""
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🎮 Game", callback_data='menu_game'), 
         InlineKeyboardButton("😂 Jokes", callback_data='menu_jokes')],
        [InlineKeyboardButton("📊 Info", callback_data='menu_info'), 
         InlineKeyboardButton("ℹ️ About", callback_data='menu_about')],
        [InlineKeyboardButton("🎯 Kuis", callback_data='game_kuis'),
         InlineKeyboardButton("✊ Suit", callback_data='game_suit')]
    ]
    await update.message.reply_text(
        "📋 *MENU UTAMA*

Pilih menu:",
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 *SI PINTAR BOT* v2.0

"
        "Bot AI pintar yang bisa:
"
        "• 💬 Ngobrol natural
"
        "• 🎮 Main game
"
        "• 😂 Hiburan
"
        "• 📊 Track progress

"
        "Dibuat dengan ❤️ menggunakan Python",
        parse_mode='Markdown'
    )

async def game_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🎲 Tebak Angka", callback_data='game_tebakangka')],
        [InlineKeyboardButton("🎯 Kuis", callback_data='game_kuis')],
        [InlineKeyboardButton("✊ Batu Gunting Kertas", callback_data='game_suit')]
    ]
    await update.message.reply_text(
        "🎮 *PILIH GAME*

Mau main apa?",
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def tebak_angka(update: Update, context: ContextTypes.DEFAULT_TYPE):
    number = random.randint(1, 10)
    context.user_data['game_number'] = number
    context.user_data['attempts'] = 0
    await update.message.reply_text(
        "🎲 *TEBAK ANGKA*

"
        "Saya memilih angka 1-10.
"
        "Ketik tebakanmu!",
        parse_mode='Markdown'
    )

async def kuis(update: Update, context: ContextTypes.DEFAULT_TYPE):
    questions = [
        {'question': 'Apa ibukota Indonesia?', 'answer': 'jakarta'},
        {'question': 'Berapa 2 + 2 x 2?', 'answer': '6'},
        {'question': 'Siapa penemu lampu?', 'answer': 'thomas edison'},
        {'question': 'Apa warna langit?', 'answer': 'biru'}
    ]
    q = random.choice(questions)
    context.user_data['quiz_answer'] = q['answer']
    await update.message.reply_text(
        f"🎯 *KUIS*

{q['question']}

Ketik jawabanmu!",
        parse_mode='Markdown'
    )

async def jokes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    jokes_list = [
        "Kenapa ayam menyebrang jalan? Karena mau ke seberang! 🐔",
        "Kenapa programmer bingung? Karena tidak bisa menemukan bug! 💻",
        "Ikan apa yang bisa terbang? Ikan Lele-lawar! 🐟",
        "Kenapa komputer dingin? Karena punya banyak kipas! ❄️"
    ]
    await update.message.reply_text(f"😂 *JOKES*

{random.choice(jokes_list)}", parse_mode='Markdown')

async def fakta(update: Update, context: ContextTypes.DEFAULT_TYPE):
    facts = [
        "🐝 Lebah bisa mengenali wajah manusia!",
        "🐙 Gurita punya 3 jantung!",
        "🦋 Kupu-kupu merasakan dengan kakinya!",
        "🌍 Bumi berputar 1.600 km/jam!"
    ]
    await update.message.reply_text(f"🤯 *FAKTA*

{random.choice(facts)}", parse_mode='Markdown')

async def info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    data = load_data()
    user_data = data['users'].get(str(user.id), {})
    
    await update.message.reply_text(
        f"📊 *INFO*

"
        f"👤 Nama: {user_data.get('name', user.first_name)}
"
        f"📈 Level: {user_data.get('level', 1)}
"
        f"💰 Points: {user_data.get('points', 0)}
"
        f"😊 Mood: {user_data.get('mood', 'netral')}
"
        f"💬 Pesan: {user_data.get('messages', 0)}",
        parse_mode='Markdown'
    )

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    data = load_data()
    user_data = data['users'].get(str(user.id), {})
    
    await update.message.reply_text(
        f"📈 *STATISTIK*

"
        f"⭐ Level: {user_data.get('level', 1)}
"
        f"💰 Points: {user_data.get('points', 0)}
"
        f"💬 Pesan: {user_data.get('messages', 0)}
"
        f"🎮 Game: {user_data.get('games_played', 0)}
"
        f"🎯 Kuis: {user_data.get('quizzes_answered', 0)}",
        parse_mode='Markdown'
    )

async def points(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    data = load_data()
    user_data = data['users'].get(str(user.id), {})
    
    await update.message.reply_text(
        f"💰 *POIN: {user_data.get('points', 0)}*

"
        f"Chat: +1 poin
Game: +10 poin
Kuis: +15 poin",
        parse_mode='Markdown'
    )

async def level(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    data = load_data()
    user_data = data['users'].get(str(user.id), {})
    level = user_data.get('level', 1)
    points = user_data.get('points', 0)
    
    progress = (points % 100) / 100 * 10
    bar = '█' * int(progress) + '░' * (10 - int(progress))
    
    await update.message.reply_text(
        f"⭐ *LEVEL {level}*

"
        f"Poin: {points}
"
        f"Progress: {bar}
"
        f"{points % 100}/100",
        parse_mode='Markdown'
    )

async def mood(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Gunakan: /mood [senang/sedih/bosan/netral]")
        return
    
    mood = context.args[0].lower()
    if mood not in ['senang', 'sedih', 'bosan', 'netral']:
        await update.message.reply_text("Mood tidak valid!")
        return
    
    user = update.effective_user
    data = load_data()
    if str(user.id) in data['users']:
        data['users'][str(user.id)]['mood'] = mood
        save_data(data)
    
    responses = {
        'senang': 'Yeay! 😊',
        'sedih': 'Jangan sedih! 🤗',
        'bosan': 'Yuk main game! /game 🎮',
        'netral': 'Oke 👍'
    }
    await update.message.reply_text(responses[mood])

async def waktu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    now = datetime.now()
    await update.message.reply_text(f"🕐 {now.strftime('%H:%M:%S')}")

async def tanggal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    now = datetime.now()
    await update.message.reply_text(f"📅 {now.strftime('%A, %d %B %Y')}")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message.text
    user = update.effective_user
    data = load_data()
    user_id = str(user.id)
    
    if user_id not in data['users']:
        data['users'][user_id] = {
            'name': user.first_name,
            'level': 1, 'points': 0, 'messages': 0,
            'games_played': 0, 'quizzes_answered': 0, 'mood': 'netral'
        }
    
    data['users'][user_id]['messages'] = data['users'][user_id].get('messages', 0) + 1
    data['users'][user_id]['points'] = data['users'][user_id].get('points', 0) + 1
    
    # Game tebak angka
    if 'game_number' in context.user_data:
        try:
            guess = int(message)
            target = context.user_data['game_number']
            
            if guess == target:
                data['users'][user_id]['points'] += 10
                data['users'][user_id]['games_played'] = data['users'][user_id].get('games_played', 0) + 1
                await update.message.reply_text(f"🎉 *BENAR!* Angka {target}! +10 poin!", parse_mode='Markdown')
            elif guess < target:
                await update.message.reply_text("📈 Terlalu kecil!")
            else:
                await update.message.reply_text("📉 Terlalu besar!")
            
            del context.user_data['game_number']
            save_data(data)
            return
        except ValueError:
            await update.message.reply_text("Masukkan angka!")
            return
    
    # Kuis
    if 'quiz_answer' in context.user_data:
        answer = context.user_data['quiz_answer']
        if message.lower() == answer.lower():
            data['users'][user_id]['points'] += 15
            data['users'][user_id]['quizzes_answered'] = data['users'][user_id].get('quizzes_answered', 0) + 1
            await update.message.reply_text(f"🎉 *BENAR!* +15 poin!", parse_mode='Markdown')
        else:
            await update.message.reply_text(f"❌ Salah! Jawaban: {answer}")
        
        del context.user_data['quiz_answer']
        save_data(data)
        return
    
    # AI response
    response = ai_response(message)
    
    # Level up
    new_level = data['users'][user_id]['points'] // 100 + 1
    if new_level > data['users'][user_id].get('level', 1):
        data['users'][user_id]['level'] = new_level
        response += f"

🎊 *LEVEL UP!* Level {new_level}!"
    
    save_data(data)
    await update.message.reply_text(response, parse_mode='Markdown')

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    
    if data == 'menu_game':
        keyboard = [
            [InlineKeyboardButton("🎲 Tebak Angka", callback_data='game_tebakangka')],
            [InlineKeyboardButton("🎯 Kuis", callback_data='game_kuis')],
            [InlineKeyboardButton("✊ Suit", callback_data='game_suit')]
        ]
        await query.edit_message_text("🎮 *PILIH GAME*", parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))
    
    elif data == 'menu_jokes':
        jokes_list = ["Kenapa ayam menyebrang? 🐔", "Kenapa programmer bingung? 💻"]
        await query.edit_message_text(f"😂 {random.choice(jokes_list)}")
    
    elif data == 'menu_info':
        user = update.effective_user
        data = load_data()
        user_data = data['users'].get(str(user.id), {})
        await query.edit_message_text(f"📊 Level: {user_data.get('level', 1)}, Poin: {user_data.get('points', 0)}")
    
    elif data == 'menu_about':
        await query.edit_message_text("🤖 *Si Pintar Bot* v2.0", parse_mode='Markdown')
    
    elif data == 'game_tebakangka':
        number = random.randint(1, 10)
        context.user_data['game_number'] = number
        await query.edit_message_text("🎲 Ketik angka 1-10!")
    
    elif data == 'game_kuis':
        q = {'question': 'Apa ibukota Indonesia?', 'answer': 'jakarta'}
        context.user_data['quiz_answer'] = q['answer']
        await query.edit_message_text(f"🎯 {q['question']}")
    
    elif data == 'game_suit':
        keyboard = [
            [InlineKeyboardButton("✊ Batu", callback_data='suit_batu')],
            [InlineKeyboardButton("✌️ Gunting", callback_data='suit_gunting')],
            [InlineKeyboardButton("✋ Kertas", callback_data='suit_kertas')]
        ]
        await query.edit_message_text("✊✌️✋ Pilih:", reply_markup=InlineKeyboardMarkup(keyboard))
    
    elif data in ['suit_batu', 'suit_gunting', 'suit_kertas']:
        choices = {'suit_batu': '✊ Batu', 'suit_gunting': '✌️ Gunting', 'suit_kertas': '✋ Kertas'}
        bot = random.choice(list(choices.values()))
        user_choice = choices[data]
        
        if user_choice == bot:
            result = "🤝 Seri!"
        elif (user_choice == '✊ Batu' and bot == '✌️ Gunting') or              (user_choice == '✌️ Gunting' and bot == '✋ Kertas') or              (user_choice == '✋ Kertas' and bot == '✊ Batu'):
            result = "🎉 Menang!"
        else:
            result = "😅 Kalah!"
        
        await query.edit_message_text(f"Kamu: {user_choice}
Bot: {bot}

{result}")

def main():
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("menu", menu))
    app.add_handler(CommandHandler("about", about))
    app.add_handler(CommandHandler("game", game_menu))
    app.add_handler(CommandHandler("tebakangka", tebak_angka))
    app.add_handler(CommandHandler("kuis", kuis))
    app.add_handler(CommandHandler("jokes", jokes))
    app.add_handler(CommandHandler("fakta", fakta))
    app.add_handler(CommandHandler("info", info))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(CommandHandler("points", points))
    app.add_handler(CommandHandler("level", level))
    app.add_handler(CommandHandler("mood", mood))
    app.add_handler(CommandHandler("waktu", waktu))
    app.add_handler(CommandHandler("tanggal", tanggal))
    
    app.add_handler(CallbackQueryHandler(button_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("🤖 Si Pintar Bot berjalan...")
    print(f"📁 Data: {DATA_FILE}")
    app.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    main()
