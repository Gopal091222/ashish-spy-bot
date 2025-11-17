import os
import requests
import logging
from collections import defaultdict
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from flask import Flask
from threading import Thread

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Flask app for uptime
app = Flask('')

@app.route('/')
def home():
    return "🔥 Ashish Spy Bot is Running! 🔥"

def run_flask():
    app.run(host='0.0.0.0', port=8080)

# Start Flask in background
Thread(target=run_flask, daemon=True).start()

# FIXED: Direct token - no environment variable issue
TELEGRAM_TOKEN = "8423614103:AAEifyco3Cv4Zg9H1veUeMhVDjHKz8USx-A"
NUMBER_API_URL = "https://flipcartstore.serv00.net/PHONE/1.php?api_key=cyberGen123&mobile={}"

# TERA TELEGRAM ID
ADMIN_IDS = [5928833993]  # ASHISH KA ID

# Rate limiting storage
user_requests = defaultdict(list)

# ==========================
# 🔧 UTILITY FUNCTIONS
# ==========================
def is_rate_limited(user_id: int) -> bool:
    """Check if user exceeded rate limit"""
    now = datetime.now()
    user_requests[user_id] = [
        req_time for req_time in user_requests[user_id] 
        if now - req_time < timedelta(hours=1)
    ]
    
    if len(user_requests[user_id]) >= 10:
        return True
        
    user_requests[user_id].append(now)
    return False

def format_response(data) -> str:
    """Format API response beautifully"""
    if not data:
        return "❌ No records found for this number!"
    
    response = ""
    
    for i, rec in enumerate(data[:3], 1):
        mobile = rec.get("mobile", "N/A")
        name = rec.get("name", "N/A")
        fname = rec.get("fname", "N/A")
        address = rec.get("address", "N/A").replace("!", ", ")[:80] + "..." if len(rec.get("address", "")) > 80 else rec.get("address", "N/A")
        alt = rec.get("alt", "N/A")
        circle = rec.get("circle", "N/A")
        _id = rec.get("id", "N/A")

        response += f"""
🟥⚡ A S H I S H   S P Y   V1.0 ⚡🟥
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📞 **MOBILE**        : `{mobile}`
👤 **NAME**          : {name}
👨‍👦 **FATHER**        : {fname}

🏠 **ADDRESS**       : {address}
📱 **ALT NUMBER**    : {alt}
🌐 **ISP / CIRCLE**  : {circle}
🆔 **INTERNAL ID**   : {_id}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔥 **OWNER** – **ASHISH SINGH**
"""
        if i < len(data[:3]):
            response += "\n" + "═" * 50 + "\n"
    
    return response

# ==========================
# 🎯 BOT COMMANDS
# ==========================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start command with awesome design"""
    user_id = update.effective_user.id
    username = update.effective_user.username or "UNKNOWN_USER"
    
    welcome = f"""
🟥⚡ A C C E S S   G R A N T E D ⚡🟥
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

👤 **USER**: @{username}
🆔 **ID**: `{user_id}`
🔌 **INITIALIZING ASHISH SPY SYSTEM...**
💀 **LOADING MODULES** ██████████ 100%
📡 **TRACE ENGINE** → ONLINE
🛰 **DATA MATRIX** → ACTIVE

**WELCOME TO**  
🔥 **𝗔𝗦𝗛𝗜𝗦𝗛 𝗦𝗣𝗬 𝗩𝟭.𝟬** 🔥

**Available Commands:**
├─ /start - Start bot
├─ /num <mobile> - Scan number
├─ /help - Help guide
└─ /stats - Your stats

**Usage:** `/num 98XXXXXXX0`

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔻 **OWNER** – **𝗔𝗦𝗛𝗜𝗦𝗛 𝗦𝗜𝗡𝗚𝗛**
"""
    await update.message.reply_text(welcome)

async def num(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Number scanning command"""
    user_id = update.effective_user.id
    
    if is_rate_limited(user_id):
        await update.message.reply_text(
            "❌ **Rate Limit Exceeded!**\n"
            "Please wait 1 hour before making more requests.\n"
            "Limit: 10 requests per hour"
        )
        return
    
    if not context.args:
        await update.message.reply_text(
            "❌ **Invalid Usage!**\n"
            "**Correct Format:** `/num 9812345678`\n"
            "**Example:** `/num 9876543210`"
        )
        return
    
    number = context.args[0].strip()
    
    if not number.isdigit() or len(number) != 10:
        await update.message.reply_text(
            "❌ **Invalid Mobile Number!**\n"
            "• Must be 10 digits\n"
            "• Without +91 or 0\n"
            "**Example:** `9812345678`"
        )
        return
    
    processing_msg = await update.message.reply_text(
        f"🔍 **Scanning Target:** `{number}`\n"
        "⏳ *Please wait while we fetch data...*"
    )
    
    try:
        url = NUMBER_API_URL.format(number)
        response = requests.get(url, timeout=25)
        
        if response.status_code != 200:
            await processing_msg.edit_text(
                "❌ **API Server Error!**\n"
                "Please try again after some time."
            )
            return
            
        data = response.json()
        result = data.get("data", [])
        
        formatted_response = format_response(result)
        await processing_msg.edit_text(formatted_response)
        
    except requests.Timeout:
        await processing_msg.edit_text(
            "⏰ **Request Timeout!**\n"
            "The server is taking too long to respond.\n"
            "Please try again later."
        )
    except Exception as e:
        await processing_msg.edit_text(
            f"❌ **Connection Error!**\n"
            f"Error: {str(e)}\n"
            "Please try again after some time."
        )

async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Help command"""
    help_text = """
🆘 **ASHISH SPY BOT - HELP GUIDE**

**📋 Available Commands:**
├─ /start - Start the bot
├─ /num <number> - Scan mobile number
├─ /help - Show this help guide  
├─ /stats - Show your usage stats
└─ /admin - Admin commands (Owner only)

**🔍 Usage Examples:**
├─ `/num 9812345678`
├─ `/num 9876543210`
└─ `/num 9966554433`

**⚡ Features:**
├─ Real-time number scanning
├─ Fast response time
├─ Rate limiting (10/hour)
├─ Secure and private
└─ 24/7 operational

**📝 Notes:**
├─ Only Indian numbers supported
├─ Use 10 digits without country code
├─ Data accuracy depends on database
└─ For support contact owner

**🔒 Privacy:**
We don't store your search queries or personal data.
"""
    await update.message.reply_text(help_text)

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """User statistics"""
    user_id = update.effective_user.id
    username = update.effective_user.username or "N/A"
    
    total_requests = len(user_requests[user_id])
    recent_requests = [
        req for req in user_requests[user_id] 
        if datetime.now() - req < timedelta(hours=1)
    ]
    requests_this_hour = len(recent_requests)
    
    stats_text = f"""
📊 **USER STATISTICS**

👤 **User:** @{username}
🆔 **ID:** `{user_id}`

📈 **Usage Stats:**
├─ Total Requests: {total_requests}
├─ This Hour: {requests_this_hour}/10
└─ Reset In: 1 hour

💡 **Tips:**
• You can make {10 - requests_this_hour} more requests this hour
• Rate limit resets every hour
• Contact owner for issues
"""
    await update.message.reply_text(stats_text)

async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin commands"""
    user_id = update.effective_user.id
    
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("❌ Access Denied! Admin only command.")
        return
    
    total_users = len(user_requests)
    total_requests = sum(len(requests) for requests in user_requests.values())
    active_today = sum(
        1 for requests in user_requests.values() 
        if any(datetime.now() - req < timedelta(days=1) for req in requests)
    )
    
    admin_text = f"""
🛡 **ADMIN CONTROL PANEL**

📊 **Bot Statistics:**
├─ Total Users: {total_users}
├─ Total Requests: {total_requests}
├─ Active Today: {active_today}
└─ Storage Size: {len(user_requests)} records

⚙️ **Admin Commands:**
├─ /broadcast - Send message to all users
├─ /cleanup - Clear old data
└─ /restart - Restart bot system

🔧 **System Status:**
├─ Bot: ✅ Online
├─ API: ✅ Connected  
└─ Memory: ✅ Stable

👑 **Admin:** Ashish Singh (5928833993)
"""
    await update.message.reply_text(admin_text)

# ==========================
# 🚀 BOT INITIALIZATION
# ==========================
def main():
    """Start the bot"""
    print("🚀 Starting Ashish Spy Bot...")
    print("📞 Token:", TELEGRAM_TOKEN)
    print("👑 Admin ID:", ADMIN_IDS[0])
    
    try:
        application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
        
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("num", num))
        application.add_handler(CommandHandler("help", help))
        application.add_handler(CommandHandler("stats", stats))
        application.add_handler(CommandHandler("admin", admin))
        
        print("✅ Bot started successfully!")
        print("📡 Bot is now running 24/7...")
        
        application.run_polling()
        
    except Exception as e:
        print(f"❌ Error starting bot: {e}")

if __name__ == "__main__":
    main()
