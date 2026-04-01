from typing import Optional

from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from datetime import datetime
import re 

app  = FastAPI()
app.mount("/static", StaticFiles(directory="static"))
templates = Jinja2Templates(directory="templates")

posts_db = [
    {
        "id": 1,
        "title": "Castoria",
        "content": "Это содержание первого поста.",
        "author": "KateFox",
        "created_at": "2023-10-01 10:00:00",
        "image": "http://127.0.0.1:8000/static/img/1.png",
        "tags":"girl purple hsr honka_star_rail flowers moon butterfly sycle kate_fox",
    },
    {
        "id": 2,
        "title": "Blue eyes girl",
        "content": "Это содержание второго поста.",
        "author": "Пётр Петров",
        "created_at": "2023-10-02 15:30:00",
        "image": "http://127.0.0.1:8000/static/img/2.png",
        "tags":"girl white_shirt blue_eyes long_hair",
    },
    {
        "id": 3,
        "title": "Bloody Forest",
        "content": "Это содержание второго поста.",
        "author": "Qawerz",
        "created_at": "2023-10-02 15:30:00",
        "image": "http://127.0.0.1:8000/static/img/3.png",
        "tags":"girl blask_shirt skirt short_hair red forest foggy school_uniform",
    }
]
@app.get("/")
@app.get("/posts")
async def get_posts(request: Request, tags: Optional[str] = None):
    # print(tags)
    if tags:
        filtered = []
        for item in posts_db:
            if tags in item["tags"]:
                filtered.append(item)
        return templates.TemplateResponse(request, name="posts.html", context={"posts": filtered})
    
    return templates.TemplateResponse(request, name="posts.html", context={"posts": posts_db})

@app.get("/posts.json")
async def get_posts(request: Request, tags: Optional[str] = None):
    if tags:
        filtered = []
        for item in posts_db:
            if tags in item["tags"]:
                filtered.append(item)
        return {"posts": filtered}

    return {"posts": posts_db}

@app.get("/posts/{post_msg}")
async def get_posts_by_id(request: Request, post_msg: str):
    print(post_msg)
    match = re.match(r"(\d+)(\.[a-z]+)?", post_msg)
    if not match:
        raise HTTPException(status_code=400, detail="Invalid format")
    post_id = int(match.group(1))
    post_format = match.group(2)
    if not post_format:
        return templates.TemplateResponse(request, name="post.html", context={"post":posts_db[post_id-1]})
    elif post_format == ".json":
        return {
            "post":posts_db[post_id-1]
        }

