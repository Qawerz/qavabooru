from typing import Optional
import operator as op 

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
async def get_posts(request: Request, tags: Optional[str] = None):
    if tags:
        print(f"{tags=}")
        pos_tags = list(set([tag for tag in tags.strip().split(" ") if not tag.startswith("-")]))
        neg_tags = [tag[1:] for tag in tags.split(" ") if tag.startswith("-")]
        for t in pos_tags:
            print(type(t))
        print(f"{pos_tags=}\n{neg_tags=}")
        filtered = []
        for item in posts_db: # Проходимся по всему массиву
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

        return templates.TemplateResponse(request, name="posts.html", context={"posts": filtered})

    return templates.TemplateResponse(request, name="posts.html", context={"posts": posts_db})

@app.get("/posts.json")
async def get_posts(request: Request, tags: Optional[str] = None):
    if tags:
        print(f"{tags=}")
        pos_tags = [tag for tag in tags.split(" ") if (not tag.startswith("-")) ]
        neg_tags = [tag[1:] for tag in tags.split(" ") if tag.startswith("-")]
        print(f"{pos_tags=}\n{neg_tags=}")
        filtered = []
        for item in posts_db: # Проходимся по всему массиву
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

