from contextlib import asynccontextmanager
from typing import Optional
import operator as op 

from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from datetime import datetime
import re 

import sqlite3
db_con = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    db_con = sqlite3.connect("qavabooru.db")
    cursor = db_con.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Posts (
    id INTEGER PRIMARY KEY,
    title TEXT,
    image TEXT NOT NULL,
    tags TEXT NOT NULL,
    tags_count INTEGER NOT NULL
    )
    """)
    db_con.commit()
    yield
    db_con.close()

app  = FastAPI(lifespan=lifespan)
app.mount("/static", StaticFiles(directory="static"))
templates = Jinja2Templates(directory="templates")

posts_db = [
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
    },
    {
        "id": 4,
        "title": "1 girl,frog hat,gray hair,atmosphere background,cyan eyes,white shirt,portrait,aesthetic,hipster clothes,",
        "image": "http://127.0.0.1:8000/static/img/4.jpg",
        "tags":"1_girl frog_hat gray_hair atmosphere_background cyan_eyes white_shirt portrait aesthetic hipster_clothes"
    },
    {
        "id": 5,
        "title": "02111-428668394-1 girl,dress with a flower pattern,rim light,chromatic aberation,(rough sketch_1.2),gradient hair,blue hair tone,pink hair tone,.jpg",
        "image": "http://127.0.0.1:8000/static/img/5.jpg",
        "tags":"1_girl dress_with_a_flower_pattern rim_light chromatic_aberation (rough_sketch_1.2) gradient_hair blue_hair_tone pink_hair_tone"
    }
]
@app.get("/")
@app.get("/posts")
async def get_posts(request: Request, tags: Optional[str] = None, page: Optional[int] = 1):
    con = sqlite3.connect("qavabooru.db")
    cursor = con.cursor()
    posts_on_page = 20
    pagintaion=[posts_on_page*page-posts_on_page, posts_on_page*page]

    posts_data_raw = cursor.execute("SELECT * FROM Posts").fetchall()
    posts_data = []
    for post in posts_data_raw:
        posts_data.append({"id":post[0], "title":post[1], "image":post[2], "tags":post[3]})
    con.close()
    
    grouped_tags = []

    for post in posts_data[pagintaion[0]:pagintaion[1]]:
        for tag in post["tags"].split(" "):
            grouped_tags.append(tag)

    grouped_tags = list(set(grouped_tags))
    print(f"{posts_data=}")
    if tags:
        print(f"{tags=}")
        
        pos_tags = list(set([tag for tag in tags.strip().split(" ") if not tag.startswith("-")]))
        neg_tags = [tag[1:] for tag in tags.split(" ") if tag.startswith("-")]

        print(f"{pos_tags=}\n{neg_tags=}")
        filtered = []
        for item in posts_data[pagintaion[0]:pagintaion[1]]: # Проходимся по всему массиву
            filter_flag = True # Задаем, что пост проходит по фильтру
            for tag in pos_tags: # Проходимся по каждому тегу запроса
                if tag not in item["tags"].split(" "): #
                    filter_flag = False

            if filter_flag:
                filtered.append(item)

        for item in filtered:
            for tag in neg_tags:
                if tag in item["tags"]:
                    filtered.remove(item)

        grouped_tags = []

        for post in filtered:
            for tag in post["tags"].split(" "):
                grouped_tags.append(tag)
        grouped_tags = list(set(grouped_tags))

        return templates.TemplateResponse(request, name="posts.html", context={"posts": filtered, "grouped_tags": grouped_tags})

    return templates.TemplateResponse(request, name="posts.html", context={"posts": posts_data[pagintaion[0]:pagintaion[1]], "grouped_tags": grouped_tags})

@app.get("/posts.json")
async def get_posts(request: Request, tags: Optional[str] = None, page: Optional[int]=1):
    con = sqlite3.connect("qavabooru.db")
    cursor = con.cursor()
    posts_on_page = 3
    pagintaion=[posts_on_page*page-posts_on_page, posts_on_page*page]

    posts_data_raw = cursor.execute("SELECT * FROM Posts").fetchall()
    posts_data = []
    for post in posts_data_raw:
        posts_data.append({"id":post[0], "title":post[1], "image":post[2], "tags":post[3]})
    con.close()
    
    print(f"{posts_data=}")
    if tags:
        print(f"{tags=}")
        pos_tags = [tag for tag in tags.split(" ") if (not tag.startswith("-")) ]
        neg_tags = [tag[1:] for tag in tags.split(" ") if tag.startswith("-")]
        print(f"{pos_tags=}\n{neg_tags=}")
        filtered = []
        for item in posts_data[pagintaion[0]:pagintaion[1]]: # Проходимся по всему массиву
            filter_flag = True # Задаем, что пост проходит по фильтру
            for tag in pos_tags: # Проходимся по каждому тегу запроса
                if tag not in item["tags"].split(" "): #
                    filter_flag = False

            if filter_flag:
                filtered.append(item)

        for item in filtered:
            for tag in neg_tags:
                if tag in item["tags"]:
                    filtered.remove(item)

        return {"posts": filtered}

    return {"posts": posts_data[pagintaion[0]:pagintaion[1]]}


@app.get("/posts/{post_msg}")
async def get_posts_by_id(request: Request, post_msg: str):
    print(post_msg)
    match = re.match(r"(\d+)(\.[a-z]+)?", post_msg)
    if not match:
        raise HTTPException(status_code=400, detail="Invalid format")
    post_id = int(match.group(1))
    post_format = match.group(2)

    con = sqlite3.connect("qavabooru.db")
    cursor = con.cursor()

    posts_data_raw = cursor.execute("SELECT * FROM Posts").fetchall()
    posts_data = []
    for post in posts_data_raw:
        posts_data.append({"id":post[0], "title":post[1], "image":post[2], "tags":post[3]})
    con.close()
    if not post_format:
        return templates.TemplateResponse(request, name="post.html", context={"post":posts_data[post_id-1]})
    elif post_format == ".json":
        return {
            "post":posts_data[post_id-1]
        }


