from fastapi import FastAPI,Request,HTTPException,status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as starletteHTTPException
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
@app.get("/",include_in_schema=False,name="home")#include in schema keeps our page route out of api documentation
@app.get("/posts",include_in_schema=False,name="posts")

def home(request:Request):#parameter needed for jinja2 to work properly 
   return templates.TemplateResponse(
      "home.html",
      {
         "request": request,
         "posts": posts,'title':'Home'
      }
   )

@app.get("/posts/{id}",include_in_schema=False)
def get_post(request:Request,id: int ):
  for post in posts:
     if post.get("id")==id:
      title=post['title'][:50]
      return templates.TemplateResponse(
     
      "post.html",
      {
         "request": request,
         "post": post,'title':title
      }
   )
  raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Post Not Found")


@app.get("/api/posts")
def get_posts():
   return posts

@app.get("/api/posts/{id}")#id inside get is a path parameteter that tells fast api this is part of the url and that is a variable 
def get_post_api(id: int ):
  for post in posts:
     if post.get("id")==id:
        return post 
     
  raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Post Not Found")

     

