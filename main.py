from fastapi import FastAPI,Request

from fastapi.templating import Jinja2Templates

from fastapi.staticfiles import StaticFiles
app=FastAPI()
app.mount("/static",StaticFiles(directory='static'),name="static")

templates=Jinja2Templates(directory="templates")

posts:list[dict]=[
  {
    "id": 101,
    "title": "Getting Started with FastAPI",
    "author": "Divas Sharma",
    "published": True,
    "views": 1245
  },
  {
    "id": 102,
    "title": "Understanding REST APIs",
    "author": "John Doe",
    "published": False,
    "views": 350
  },
  {
    "id": 103,
    "title": "Python Tips for Beginners",
    "author": "Jane Smith",
    "published": True,
    "views": 2890
  }
]
#decoraters
@app.get("/",response_class=HTMLResponse,include_in_schema=False)
@app.get("/posts",response_class=HTMLResponse,include_in_schema=False)

def home():
   return f"<h1>{posts[0]["title"]}</h1>"

@app.get("/api/posts")
def get_posts():
   return posts


