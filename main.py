from fastapi import FastAPI, HTTPException, BackgroundTasks
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
import logging


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


driver_queue = asyncio.Queue()

class URLRequest(BaseModel):
    url: str


N_WORKERS = 10
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
    for _ in range(N_WORKERS):
        driver = SeleniumWorker(proxy=get_proxy())  
        await driver_queue.put(driver)
    yield
    await yeet_all_drivers()
    
app = FastAPI(lifespan=startup)


async def scrape_task(driver, url):
    html, blocked = await asyncio.to_thread(driver.fetch, url)  
    return html, blocked


async def cancel_task(task, driver):
    logger.info(f"Attempting to cancel task {task}")
    task.cancel()  

    if driver and driver.is_stale():
        driver.restart(new_proxy=get_proxy())
    await driver_queue.put(driver)  


@app.post("/scrape")
async def render(url: URLRequest, background_tasks: BackgroundTasks):
    driver = await driver_queue.get()
    loop = asyncio.get_event_loop()
    task = loop.create_task(scrape_task(driver, url.url))
    
    background_tasks.add_task(cancel_task, task, driver)

    try:
        html, blocked = await task
        return {"html": html, "blocked": blocked}
    except asyncio.CancelledError:
        logger.info(f"Task for URL {url.url} was cancelled.")
        return {"html": None, "blocked": True}
    except Exception as e:
        logger.error(f"Exception scraping {url.url}: {e}")
        driver.restart(new_proxy=get_proxy())
        return {"html": None, "blocked": True}
    finally:
        await driver_queue.put(driver)


async def yeet_all_drivers():
    for x in range(N_WORKERS):
        driver = await driver_queue.get()
        driver.quit()
        
    
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            name = proc.info['name']
            cmdline = ' '.join(proc.info.get('cmdline') or [])
            if name and ('chrome' in name.lower() or 'chromedriver' in name.lower() or "uc_driver" in name.lower()):
                logging.info(f"[KILL] Killing chromedriver PID: {proc.pid}")
                proc.kill()
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    logging.info("All drivers killed and chromedrivers yeeted.")


