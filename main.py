from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from starlette.types import Lifespan
import uvicorn
import asyncio
from worker import SeleniumWorker
import random
from uuid import uuid4
from contextlib import asynccontextmanager
import psutil
import signal


driver_queue = asyncio.Queue()

scrape_results = {}

class TaskStatus:
    PENDING = "pending"
    COMPLETE = "complete"
    FAILED = "failed"

class URLRequest(BaseModel):
    url: str


N_WORKERS = 2
proxy_list = open('proxies.txt','r',encoding='utf-8').read()
proxy_list = [x for x in proxy_list.split('\n') if x != ""]


def get_proxy():
    pr  = random.choice(proxy_list)
    if len(pr.split(':')) > 2:
        pr = pr.split(':')
        prx = f"{pr[-2]}:{pr[-1]}@{pr[0]}:{pr[1]}"
        return prx
    else:
        return pr
    
    
@asynccontextmanager
async def startup(app: FastAPI):
    # Load the ML model
    for _ in range(N_WORKERS):
        driver = SeleniumWorker(proxy=get_proxy())  
        await driver_queue.put(driver)
    yield
    await yeet_all_drivers()
    
app = FastAPI(lifespan=startup)



@app.post("/scrape")
async def render(url: URLRequest):
    try:
        driver = await driver_queue.get()
        loop = asyncio.get_event_loop()
        html,blocked = await loop.run_in_executor(None, lambda: driver.fetch(url.url))
    
        return {"html": html, "blocked": blocked}
    except Exception as e:
        print(e)
        
    finally:
        if blocked or driver.is_stale():
            driver.restart(new_proxy=get_proxy())
        await driver_queue.put(driver)



async def yeet_all_drivers():
    for x in range(N_WORKERS):
        driver = await driver_queue.get()
        driver.quit()
        
    
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            name = proc.info['name']
            cmdline = ' '.join(proc.info.get('cmdline') or [])
            if name and ('chromedriver' in name.lower() or "uc_driver" in name.lower()):
                print(f"[KILL] Killing chromedriver PID: {proc.pid}")
                proc.kill()
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    print("INFO:     All drivers killed and chromedrivers yeeted.")


