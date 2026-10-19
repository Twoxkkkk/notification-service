import os
from fastapi import FastAPI, BackgroundTasks
from uvicorn import run
from re import match
import httpx
import os
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.responses import PlainTextResponse

app = FastAPI()

BOT_TOKEN = os.getenv("BOT_TOKEN", "")

WHITELIST = [int(uid.strip()) for uid in os.getenv("WHITELIST", "987654321,111111111").split(",") if uid.strip()]

async def send_telegram_notification(data: str):
    async with httpx.AsyncClient() as client:
        for user_id in WHITELIST:
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
            
            text = f"🔔 Получена ссылка на файл!\n\n{data}" 

            payload = {
                "chat_id": user_id,
                "text": text,
                "parse_mode": "Markdown"
            }
            try:
                
                response = await client.post(url, json=payload)
                if response.status_code != 200:
                    print(f"Ошибка отправки пользователю {user_id}: {response.text}")
            except Exception as e:
                print(f"Не удалось связаться с API Telegram для {user_id}: {e}")

@app.get("/send/{data}")
async def send(data: str, background_tasks: BackgroundTasks):
    
    await send_telegram_notification(data)
    
    return {"status": "success", "message": "Данные приняты, уведомление отправляется"}


@app.get("/get/{file}", response_class=PlainTextResponse)
async def getData(file: str, v: str = None):
    
    if not v:
        raise HTTPException(status_code=400, detail="Параметр 'v' (номер варианта) обязателен")
        
    
    base_dir = Path("variants") / f"src{v}"
    
    
    if not base_dir.exists() or not base_dir.is_dir():
        raise HTTPException(status_code=404, detail=f"Папка для варианта {v} не найдена")

    
    
    found_files = list(base_dir.rglob(file))
    
    if not found_files:
        raise HTTPException(status_code=404, detail=f"Файл {file} не найден в варианте {v}")
    
    
    target_file = found_files[0]
    
    
    try:
        content = target_file.read_text(encoding="utf-8")
        return content
    except Exception as e:
        raise HTTPException(status_code=500, detail="Ошибка при чтении файла")

if __name__ == "__main__":
    run(app=app, host="0.0.0.0", port=8080)