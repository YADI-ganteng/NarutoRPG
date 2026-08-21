import os
import json
import random
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler, filters,
    ContextTypes, ConversationHandler, CallbackQueryHandler
)
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ==================== KONFIGURASI ====================
TOKEN = os.getenv('BOT_TOKEN', 'YOUR_BOT_TOKEN_HERE')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', 'YOUR_OPENAI_KEY_HERE')  # Optional

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ==================== DATABASE SEDERHANA ====================
class Database:
    def __init__(self, filename='user_data.json'):
        self.filename = filename
        self.data = self.load_data()
    
    def load_data(self):
        try:
            with open(self.filename, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {'users': {}, 'chats': {}, 'stats': {}}
    
    def save_data(self):
        with open(self.filename, 'w') as f:
            json.dump(self.data, f, indent=2)
    
    def get_user(self, user_id):
        user_id = str(user_id)
        if user_id not in self.data['users']:
            self.data['users'][user_id] = {
                'username': '',
                'first_name': '',
                'last_seen': datetime.now().isoformat(),
                'messages_count': 0,
                'last_message': '',
                'mood': 'netral',
                'interests': [],
                'points': 0,
                'level': 1,
                'warnings': 0
            }
        return self.data['users'][user_id]
    
    def update_user(self, user_id, updates):
        user_id = str(user_id)
        user = self.get_user(user_id)
        user.update(updates)
        self.save_data()
        return user

db = Database()

# ==================== AI CHAT (SEDERHANA) ====================
class SimpleAI:
    def __init__(self):
        self.responses = {
            'halo': [
                'Halo! Apa kabar? 😊',
                'Hai! Senang bertemu denganmu!',
                'Hello! Ada yang bisa saya bantu?'
            ],
            'apa kabar': [
                'Kabar baik! Kamu sendiri gimana?',
                'Alhamdulillah baik. Kamu?',
                'Baik banget! Semangat terus ya!'
            ],
            'nama': [
                'Nama saya adalah bot pintar! Kamu bisa panggil saya dengan /nama',
                'Saya bot AI yang siap membantu kamu!'
            ],
            'umur': [
                'Saya masih muda kok, baru saja dibuat!',
                'Umur saya tidak penting, yang penting saya bisa bantu kamu!'
            ],
            'terima kasih': [
                'Sama-sama! 😊',
                'Anytime! Senang bisa membantu!',
                'Siap! Kalau butuh bantuan lagi, panggil aja ya!'
            ],
            'pintar': [
                'Terima kasih! Saya memang dirancang untuk membantu!',
                'Hehe, makasih! Kamu juga pintar!'
            ]
        }
        
        self.questions = {
            'kamu siapa': 'Saya adalah bot Telegram yang dibuat menggunakan Python! Saya bisa diajak ngobrol, main game, dan banyak lagi!',
            'bisa apa aja': 'Saya bisa:\n• Ngobrol santai\n• Main game (/game)\n• Kasih info (/info)\n• Cek cuaca (/cuaca)\n• Dan masih banyak lagi!'
        }
    
    def get_response(self, message, user_data):
        message = message.lower()
        
        # Check exact matches in questions
        for question, answer in self.questions.items():
            if question in message:
                return answer
        
        # Check keyword matches
        for keyword, responses in self.responses.items():
            if keyword in message:
                return random.choice(responses)
        
        # Context-aware responses based on user mood
        if user_data.get('mood') == 'sedih':
            return 'Jangan sedih! Ada yang bisa saya bantu? 😊'
        
        # Default responses
        default_responses = [
            'Menarik! Ceritakan lebih lanjut!',
            'Oh begitu... Lalu?',
            'Saya paham. Ada hal lain yang ingin dibicarakan?',
            'Hmm, itu menarik! 🤔',
            'Boleh saya tahu lebih detail?',
            'Wah, saya jadi penasaran!',
            'Terus gimana kelanjutannya?',
            'Kamu tau, itu mengingatkan saya pada sesuatu!'
        ]
        return random.choice(default_responses)

ai = SimpleAI()

# ==================== COMMAND HANDLERS ====================
# Command: /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_data = db.get_user(user.id)
    
    # Update user info
    db.update_user(user.id, {
        'username': user.username or '',
        'first_name': user.first_name,
        'last_seen': datetime.now().isoformat()
    })
    
    # Welcome message
    welcome_text = f"""
👋 *Halo {user.first_name}!*

Selamat datang di *Si Pintar Bot*!

Saya adalah bot yang bisa:
• 💬 Ngobrol santai denganmu
• 🎮 Main game seru
• 📊 Info menarik
• 🌤️ Cek cuaca
• 🎯 Dan masih banyak lagi!

Ketik /help untuk melihat semua perintah.
Ketik /menu untuk menu interaktif.

*Yuk mulai ngobrol!*
"""
    
    # Create inline keyboard
    keyboard = [
        [InlineKeyboardButton("🎮 Main Game", callback_data='menu_game')],
        [InlineKeyboardButton("📋 Lihat Menu", callback_data='menu_help')],
        [InlineKeyboardButton("ℹ️ Tentang Saya", callback_data='menu_about')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(welcome_text, parse_mode='Markdown', reply_markup=reply_markup)

# Command: /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = """
📚 *DAFTAR PERINTAH BOT*

*💬 Chat & Interaksi*
• /start - Mulai bot
• /help - Lihat bantuan
• /menu - Menu interaktif
• /about - Tentang bot
• /nama - Tanya nama bot
• /creator - Info pembuat

*🎮 Game & Hiburan*
• /game - Main game
• /tebakangka - Game tebak angka
• /kuis - Kuis pengetahuan
• /jokes - Dapatkan jokes lucu
• /fakta - Fakta menarik

*📊 Informasi*
• /info - Info pengguna
• /stats - Statistik kamu
• /cuaca [kota] - Cek cuaca
• /waktu - Waktu saat ini
• /tanggal - Tanggal hari ini

*⚙️ Fitur Lainnya*
• /points - Lihat poin kamu
• /level - Level kamu
• /mood [sedih/senang/bosan] - Set mood
• /feedback [pesan] - Kirim feedback
• /settings - Pengaturan

Ketik perintah di atas untuk menggunakannya!
"""
    await update.message.reply_text(help_text, parse_mode='Markdown')

# Command: /menu
async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🎮 Game", callback_data='menu_game'),
         InlineKeyboardButton("📊 Info", callback_data='menu_info')],
        [InlineKeyboardButton("😂 Jokes", callback_data='menu_jokes'),
         InlineKeyboardButton("🎯 Kuis", callback_data='menu_quiz')],
        [InlineKeyboardButton("ℹ️ About", callback_data='menu_about'),
         InlineKeyboardButton("⚙️ Settings", callback_data='menu_settings')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "📋 *MENU UTAMA*\n\nPilih menu di bawah ini:",
        parse_mode='Markdown',
        reply_markup=reply_markup
    )

# Command: /about
async def about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    about_text = """
🤖 *TENTANG SI PINTAR BOT*

*Versi:* 2.0
*Dibuat dengan:* Python & python-telegram-bot
*Fitur:* AI chat, game, info, dan banyak lagi!

*Kemampuan:*
• Memahami bahasa Indonesia
• Merespon dengan natural
• Belajar dari interaksi
• Menyimpan data pengguna

*Developer:* @your_username
*GitHub:* github.com/yourrepo

Terima kasih sudah menggunakan bot ini! 🙏
"""
    await update.message.reply_text(about_text, parse_mode='Markdown')

# Command: /nama
async def nama(update: Update, context: ContextTypes.DEFAULT_TYPE):
    responses = [
        "Nama saya *Si Pintar Bot*! Tapi kamu bisa panggil saya *Pintar* aja 😊",
        "Saya *Si Pintar*, bot yang siap membantu kamu!",
        "Orang-orang memanggil saya *Si Pintar*. Keren kan namanya? 😎"
    ]
    await update.message.reply_text(random.choice(responses), parse_mode='Markdown')

# Command: /creator
async def creator(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👨‍💻 *PEMBUAT BOT*\n\n"
        "Bot ini dibuat oleh seorang developer yang passionate dengan AI dan teknologi.\n\n"
        "Kontak: @your_username\n"
        "Email: your.email@example.com\n\n"
        "Jangan ragu untuk memberikan feedback! 🙏",
        parse_mode='Markdown'
    )

# Command: /game
async def game_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🎲 Tebak Angka", callback_data='game_tebakangka')],
        [InlineKeyboardButton("🎯 Kuis", callback_data='game_kuis')],
        [InlineKeyboardButton("✊ Batu Gunting Kertas", callback_data='game_suit')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "🎮 *PILIH GAME*\n\nMau main game apa?",
        parse_mode='Markdown',
        reply_markup=reply_markup
    )

# Command: /tebakangka
async def tebak_angka(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Generate random number
    number = random.randint(1, 10)
    context.user_data['game_number'] = number
    context.user_data['attempts'] = 0
    
    await update.message.reply_text(
        "🎲 *GAME TEBAK ANGKA*\n\n"
        "Saya sudah memilih angka 1-10.\n"
        "Ketik angka tebakanmu sekarang!\n\n"
        "Ketik /stop untuk berhenti.",
        parse_mode='Markdown'
    )

# Command: /kuis
async def kuis(update: Update, context: ContextTypes.DEFAULT_TYPE):
    questions = [
        {
            'question': 'Apa ibukota Indonesia?',
            'answer': 'Jakarta',
            'options': ['Jakarta', 'Bandung', 'Surabaya', 'Medan']
        },
        {
            'question': 'Berapa 2 + 2 × 2?',
            'answer': '6',
            'options': ['4', '6', '8', '10']
        },
        {
            'question': 'Siapa penemu lampu?',
            'answer': 'Thomas Edison',
            'options': ['Nikola Tesla', 'Thomas Edison', 'Albert Einstein', 'Isaac Newton']
        }
    ]
    
    question = random.choice(questions)
    context.user_data['quiz_answer'] = question['answer']
    
    await update.message.reply_text(
        f"🎯 *KUIS*\n\n{question['question']}\n\n"
        f"Jawab dengan mengetik jawabanmu!\n"
        f"Ketik /stop untuk berhenti.",
        parse_mode='Markdown'
    )

# Command: /jokes
async def jokes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    jokes_list = [
        "Kenapa ayam menyebrang jalan? Karena mau ke seberang! 🐔",
        "Kenapa programmer bingung? Karena dia tidak bisa menemukan bug-nya! 💻",
        "Apa bedanya kamu sama jam 12? Jam 12 kesiangan, kamu kesayangan! 😊",
        "Kenapa buku matematika sedih? Karena punya banyak masalah! 📚",
        "Ikan apa yang bisa terbang? Ikan Lele-lawar! 🐟",
        "Kenapa komputer dingin? Karena punya banyak kipas! ❄️",
        "Apa persamaan uang dan rahasia? Sama-sama susah dipegang! 💰",
        "Kenapa orang botak senang? Karena rambutnya tidak pernah bercabang! 👨‍🦲"
    ]
    
    await update.message.reply_text(f"😂 *JOKES*\n\n{random.choice(jokes_list)}", parse_mode='Markdown')

# Command: /fakta
async def fakta(update: Update, context: ContextTypes.DEFAULT_TYPE):
    facts = [
        "🐝 Lebah bisa mengenali wajah manusia!",
        "🌍 Bumi berputar dengan kecepatan 1.600 km/jam!",
        "🧠 Otak manusia menghasilkan listrik yang cukup untuk menyalakan lampu!",
        "🐙 Gurita punya 3 jantung!",
        "🌸 Bunga matahari bisa membersihkan tanah dari radiasi!",
        "🦋 Kupu-kupu merasakan dengan kakinya!",
        "🌊 Lautan mengandung 20 juta ton emas!",
        "🐘 Gajah adalah satu-satunya mamalia yang tidak bisa melompat!"
    ]
    
    await update.message.reply_text(f"🤯 *FAKTA MENARIK*\n\n{random.choice(facts)}", parse_mode='Markdown')

# Command: /info
async def info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_data = db.get_user(user.id)
    
    info_text = f"""
📊 *INFO PENGGUNA*

*Nama:* {user.first_name}
*Username:* @{user.username or 'Tidak ada'}
*User ID:* {user.id}
*Level:* {user_data.get('level', 1)}
*Points:* {user_data.get('points', 0)}
*Mood:* {user_data.get('mood', 'netral')}
*Pesan terkirim:* {user_data.get('messages_count', 0)}
*Terakhir aktif:* {user_data.get('last_seen', 'Unknown')}
"""
    await update.message.reply_text(info_text, parse_mode='Markdown')

# Command: /stats
async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_data = db.get_user(user.id)
    
    stats_text = f"""
📈 *STATISTIK KAMU*

*Level:* {user_data.get('level', 1)}
*Points:* {user_data.get('points', 0)}
*Total pesan:* {user_data.get('messages_count', 0)}
*Game dimainkan:* {user_data.get('games_played', 0)}
*Kuis dijawab:* {user_data.get('quizzes_answered', 0)}
*Jokes diterima:* {user_data.get('jokes_received', 0)}
"""
    await update.message.reply_text(stats_text, parse_mode='Markdown')

# Command: /cuaca
async def cuaca(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text(
            "🌤️ *CEK CUACA*\n\n"
            "Gunakan format: /cuaca [nama kota]\n"
            "Contoh: /cuaca Jakarta",
            parse_mode='Markdown'
        )
        return
    
    city = ' '.join(context.args)
    
    # Simulate weather (bisa diganti dengan API cuaca sungguhan)
    weather_data = {
        'cerah': '☀️ Cerah',
        'hujan': '🌧️ Hujan',
        'berawan': '☁️ Berawan',
        'mendung': '🌥️ Mendung'
    }
    
    weather = random.choice(list(weather_data.values()))
    temperature = random.randint(20, 35)
    
    await update.message.reply_text(
        f"🌤️ *CUACA {city.upper()}*\n\n"
        f"Kondisi: {weather}\n"
        f"Suhu: {temperature}°C\n\n"
        f"*Tips:* Jangan lupa bawa payung! ☔",
        parse_mode='Markdown'
    )

# Command: /waktu
async def waktu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    now = datetime.now()
    await update.message.reply_text(
        f"🕐 *WAKTU SEKARANG*\n\n"
        f"📅 Tanggal: {now.strftime('%d %B %Y')}\n"
        f"⏰ Jam: {now.strftime('%H:%M:%S')}\n"
        f"📆 Hari: {now.strftime('%A')}",
        parse_mode='Markdown'
    )

# Command: /tanggal
async def tanggal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    now = datetime.now()
    await update.message.reply_text(
        f"📅 Hari ini: *{now.strftime('%A, %d %B %Y')}*",
        parse_mode='Markdown'
    )

# Command: /points
async def points(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_data = db.get_user(user.id)
    
    await update.message.reply_text(
        f"💰 *POIN KAMU*\n\n"
        f"Total poin: *{user_data.get('points', 0)}*\n"
        f"Level: *{user_data.get('level', 1)}*\n\n"
        f"Dapatkan poin dengan:\n"
        f"• Chat dengan bot (+1 poin)\n"
        f"• Main game (+5 poin)\n"
        f"• Jawab kuis (+10 poin)\n"
        f"• Minta jokes (+2 poin)",
        parse_mode='Markdown'
    )

# Command: /level
async def level(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_data = db.get_user(user.id)
    level = user_data.get('level', 1)
    points = user_data.get('points', 0)
    points_needed = level * 100
    
    progress = (points % 100) / 100 * 10  # 10 bar progress
    
    progress_bar = '█' * int(progress) + '░' * (10 - int(progress))
    
    await update.message.reply_text(
        f"⭐ *LEVEL KAMU*\n\n"
        f"Level: *{level}*\n"
        f"Poin: *{points}*\n"
        f"Poin ke level berikutnya: *{points_needed - (points % 100)}*\n\n"
        f"Progress: {progress_bar}\n"
        f"{points % 100}/{points_needed}",
        parse_mode='Markdown'
    )

# Command: /mood
async def mood(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text(
            "😊 *SET MOOD*\n\n"
            "Gunakan: /mood [senang/sedih/bosan]\n"
            "Contoh: /mood senang",
            parse_mode='Markdown'
        )
        return
    
    mood = context.args[0].lower()
    valid_moods = ['senang', 'sedih', 'bosan', 'netral']
    
    if mood not in valid_moods:
        await update.message.reply_text("Mood tidak valid! Gunakan: senang, sedih, bosan, atau netral.")
        return
    
    user = update.effective_user
    db.update_user(user.id, {'mood': mood})
    
    mood_responses = {
        'senang': 'Yeay! Senang mendengarnya! 😊',
        'sedih': 'Jangan sedih! Ada yang bisa saya bantu? 🤗',
        'bosan': 'Yuk main game biar tidak bosan! Ketik /game 🎮',
        'netral': 'Oke, mood kamu netral 👍'
    }
    
    await update.message.reply_text(mood_responses[mood])

# Command: /feedback
async def feedback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text(
            "📝 *FEEDBACK*\n\n"
            "Gunakan: /feedback [pesan kamu]\n"
            "Contoh: /feedback Bot ini keren!",
            parse_mode='Markdown'
        )
        return
    
    feedback_text = ' '.join(context.args)
    user = update.effective_user
    
    # Simpan feedback
    if 'feedback' not in db.data:
        db.data['feedback'] = []
    db.data['feedback'].append({
        'user_id': user.id,
        'username': user.username,
        'feedback': feedback_text,
        'timestamp': datetime.now().isoformat()
    })
    db.save_data()
    
    await update.message.reply_text(
        "✅ *FEEDBACK TERKIRIM*\n\n"
        "Terima kasih atas feedback kamu! 🙏\n"
        "Feedback kamu sangat berarti untuk pengembangan bot ini.",
        parse_mode='Markdown'
    )

# Command: /settings
async def settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("😊 Set Mood", callback_data='set_mood')],
        [InlineKeyboardButton("🔔 Notifikasi", callback_data='set_notif')],
        [InlineKeyboardButton("🌐 Bahasa", callback_data='set_language')],
        [InlineKeyboardButton("ℹ️ Info Akun", callback_data='account_info')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "⚙️ *PENGATURAN*\n\nPilih pengaturan yang ingin diubah:",
        parse_mode='Markdown',
        reply_markup=reply_markup
    )

# ==================== MESSAGE HANDLER ====================
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message.text
    user = update.effective_user
    user_data = db.get_user(user.id)
    
    # Update user stats
    updates = {
        'messages_count': user_data.get('messages_count', 0) + 1,
        'last_message': message,
        'last_seen': datetime.now().isoformat()
    }
    
    # Add points for chatting
    updates['points'] = user_data.get('points', 0) + 1
    
    # Check for game in progress
    if 'game_number' in context.user_data:
        try:
            guess = int(message)
            target = context.user_data['game_number']
            attempts = context.user_data.get('attempts', 0) + 1
            context.user_data['attempts'] = attempts
            
            if guess == target:
                points_earned = 10
                updates['points'] = updates['points'] + points_earned
                updates['games_played'] = user_data.get('games_played', 0) + 1
                
                await update.message.reply_text(
                    f"🎉 *BENAR!*\n\n"
                    f"Kamu berhasil menebak angka {target} dalam {attempts} percobaan!\n"
                    f"Poin +{points_earned} 💰",
                    parse_mode='Markdown'
                )
                del context.user_data['game_number']
                del context.user_data['attempts']
            elif guess < target:
                await update.message.reply_text("📈 Terlalu kecil! Coba angka yang lebih besar.")
            else:
                await update.message.reply_text("📉 Terlalu besar! Coba angka yang lebih kecil.")
        except ValueError:
            await update.message.reply_text("Masukkan angka yang valid!")
        
        db.update_user(user.id, updates)
        return
    
    # Check for quiz in progress
    if 'quiz_answer' in context.user_data:
        answer = context.user_data['quiz_answer']
        
        if message.lower() == answer.lower():
            points_earned = 15
            updates['points'] = updates['points'] + points_earned
            updates['quizzes_answered'] = user_data.get('quizzes_answered', 0) + 1
            
            await update.message.reply_text(
                f"🎉 *JAWABAN BENAR!*\n\n"
                f"Kamu menjawab: {answer}\n"
                f"Poin +{points_earned} 💰",
                parse_mode='Markdown'
            )
        else:
            await update.message.reply_text(
                f"❌ *JAWABAN SALAH*\n\n"
                f"Jawaban yang benar: {answer}\n"
                f"Jangan menyerah, coba lagi!",
                parse_mode='Markdown'
            )
        
        del context.user_data['quiz_answer']
        db.update_user(user.id, updates)
        return
    
    # Get AI response
    response = ai.get_response(message, user_data)
    
    # Add some personality
    if user_data.get('mood') == 'senang':
        response += "\n\nBTW, senang ngobrol denganmu! 😊"
    elif user_data.get('mood') == 'sedih':
        response += "\n\nSemoga harimu menyenangkan! 🤗"
    
    # Check for level up
    current_points = updates['points']
    new_level = current_points // 100 + 1
    if new_level > user_data.get('level', 1):
        updates['level'] = new_level
        response += f"\n\n🎊 *LEVEL UP!* Kamu naik ke level {new_level}!"
    
    await update.message.reply_text(response, parse_mode='Markdown')
    
    # Save updates
    db.update_user(user.id, updates)

# ==================== CALLBACK HANDLERS ====================
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    callback_data = query.data
    
    if callback_data == 'menu_game':
        keyboard = [
            [InlineKeyboardButton("🎲 Tebak Angka", callback_data='game_tebakangka')],
            [InlineKeyboardButton("🎯 Kuis", callback_data='game_kuis')],
            [InlineKeyboardButton("✊ Batu Gunting Kertas", callback_data='game_suit')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            "🎮 *PILIH GAME*\n\nMau main game apa?",
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    
    elif callback_data == 'menu_help':
        help_text = "Ketik /help untuk melihat semua perintah!"
        await query.edit_message_text(help_text, parse_mode='Markdown')
    
    elif callback_data == 'menu_about':
        about_text = "🤖 *Si Pintar Bot* v2.0\n\nBot pintar yang bisa diajak ngobrol!"
        await query.edit_message_text(about_text, parse_mode='Markdown')
    
    elif callback_data == 'menu_info':
        await query.edit_message_text("Ketik /info untuk melihat info kamu!", parse_mode='Markdown')
    
    elif callback_data == 'menu_jokes':
        jokes_list = [
            "Kenapa ayam menyebrang jalan? Karena mau ke seberang! 🐔",
            "Kenapa programmer bingung? Karena dia tidak bisa menemukan bug-nya! 💻"
        ]
        await query.edit_message_text(f"😂 {random.choice(jokes_list)}", parse_mode='Markdown')
    
    elif callback_data == 'menu_quiz':
        await query.edit_message_text("Ketik /kuis untuk mulai kuis!", parse_mode='Markdown')
    
    elif callback_data == 'menu_settings':
        await query.edit_message_text("Ketik /settings untuk pengaturan!", parse_mode='Markdown')
    
    elif callback_data == 'game_tebakangka':
        number = random.randint(1, 10)
        context.user_data['game_number'] = number
        context.user_data['attempts'] = 0
        await query.edit_message_text(
            "🎲 *TEBAK ANGKA*\n\n"
            "Saya sudah memilih angka 1-10.\n"
            "Ketik angka tebakanmu!",
            parse_mode='Markdown'
        )
    
    elif callback_data == 'game_kuis':
        questions = [
            {
                'question': 'Apa ibukota Indonesia?',
                'answer': 'Jakarta'
            },
            {
                'question': 'Berapa 2 + 2 × 2?',
                'answer': '6'
            }
        ]
        question = random.choice(questions)
        context.user_data['quiz_answer'] = question['answer']
        await query.edit_message_text(
            f"🎯 *KUIS*\n\n{question['question']}\n\n"
            f"Ketik jawabanmu!",
            parse_mode='Markdown'
        )
    
    elif callback_data == 'game_suit':
        keyboard = [
            [InlineKeyboardButton("✊ Batu", callback_data='suit_batu')],
            [InlineKeyboardButton("✌️ Gunting", callback_data='suit_gunting')],
            [InlineKeyboardButton("✋ Kertas", callback_data='suit_kertas')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            "✊✌️✋ *BATU GUNTING KERTAS*\n\nPilih salah satu:",
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    
    elif callback_data in ['suit_batu', 'suit_gunting', 'suit_kertas']:
        choices = {
            'suit_batu': '✊ Batu',
            'suit_gunting': '✌️ Gunting',
            'suit_kertas': '✋ Kertas'
        }
        bot_choice = random.choice(list(choices.values()))
        user_choice = choices[callback_data]
        
        # Determine winner
        if user_choice == bot_choice:
            result = "🤝 Seri!"
        elif (user_choice == '✊ Batu' and bot_choice == '✌️ Gunting') or \
             (user_choice == '✌️ Gunting' and bot_choice == '✋ Kertas') or \
             (user_choice == '✋ Kertas' and bot_choice == '✊ Batu'):
            result = "🎉 Kamu menang!"
        else:
            result = "😅 Kamu kalah!"
        
        await query.edit_message_text(
            f"✊✌️✋ *HASIL*\n\n"
            f"Kamu: {user_choice}\n"
            f"Bot: {bot_choice}\n\n"
            f"{result}",
            parse_mode='Markdown'
        )
    
    elif callback_data == 'set_mood':
        keyboard = [
            [InlineKeyboardButton("😊 Senang", callback_data='mood_senang')],
            [InlineKeyboardButton("😢 Sedih", callback_data='mood_sedih')],
            [InlineKeyboardButton("😴 Bosan", callback_data='mood_bosan')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            "Pilih mood kamu:",
            reply_markup=reply_markup
        )
    
    elif callback_data.startswith('mood_'):
        mood = callback_data.replace('mood_', '')
        user = update.effective_user
        db.update_user(user.id, {'mood': mood})
        await query.edit_message_text(f"Mood kamu diubah menjadi {mood}! ✅")

# ==================== ERROR HANDLER ====================
async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Update {update} caused error {context.error}")
    
    if update and update.effective_message:
        await update.effective_message.reply_text(
            "❌ *ERROR*\n\nMaaf, terjadi kesalahan. Silakan coba lagi nanti.",
            parse_mode='Markdown'
        )

# ==================== MAIN FUNCTION ====================
def main():
    # Create application
    app = Application.builder().token(TOKEN).build()
    
    # Add command handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("menu", menu))
    app.add_handler(CommandHandler("about", about))
    app.add_handler(CommandHandler("nama", nama))
    app.add_handler(CommandHandler("creator", creator))
    app.add_handler(CommandHandler("game", game_menu))
    app.add_handler(CommandHandler("tebakangka", tebak_angka))
    app.add_handler(CommandHandler("kuis", kuis))
    app.add_handler(CommandHandler("jokes", jokes))
    app.add_handler(CommandHandler("fakta", fakta))
    app.add_handler(CommandHandler("info", info))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(CommandHandler("cuaca", cuaca))
    app.add_handler(CommandHandler("waktu", waktu))
    app.add_handler(CommandHandler("tanggal", tanggal))
    app.add_handler(CommandHandler("points", points))
    app.add_handler(CommandHandler("level", level))
    app.add_handler(CommandHandler("mood", mood))
    app.add_handler(CommandHandler("feedback", feedback))
    app.add_handler(CommandHandler("settings", settings))
    
    # Add callback handler
    app.add_handler(CallbackQueryHandler(button_callback))
    
    # Add message handler (for chat)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Add error handler
    app.add_error_handler(error_handler)
    
    # Start bot
    print("Bot started! Press Ctrl+C to stop.")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()