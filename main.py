from fastapi import FastAPI,Request,HTTPException,status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles



app=FastAPI()

app.mount("/static",StaticFiles(directory='static'),name="static")

templates=Jinja2Templates(directory="templates")

posts: list[dict] = [
    {
        "id": 101,
        "title": "Getting Started with FastAPI",
        "author": "Divas Sharma",
        "date_posted": "August 1, 2026",
        "content": "FastAPI is a modern, fast (high-performance), web framework for building APIs with Python 3.8+ based on standard Python type hints.",
        "published": True,
        "views": 1245,
    },
    {
        "id": 102,
        "title": "Understanding REST APIs",
        "author": "John Doe",
        "date_posted": "August 2, 2026",
        "content": "RESTful APIs allow systems to communicate over HTTP using standard request methods like GET, POST, PUT, and DELETE.",
        "published": False,
        "views": 350,
    },
    {
        "id": 103,
        "title": "Python Tips for Beginners",
        "author": "Jane Smith",
        "date_posted": "August 3, 2026",
        "content": "Here are some valuable Python tips and best practices for beginners looking to write cleaner, more efficient code.",
        "published": True,
        "views": 2890,
    },
]

# decoraters
@app.get("/", include_in_schema=False, name="home")  # include in schema keeps our page route out of api documentation
@app.get("/posts", include_in_schema=False, name="posts")
def home(request: Request):  # parameter needed for jinja2 to work properly
    return templates.TemplateResponse(
        request=request,
        name="home.html",
        context={
            "posts": posts,
            "title": "Home",
        },
    )


@app.get("/posts/{id}", include_in_schema=False)
def get_post(request: Request, id: int):
    for post in posts:
        if post.get("id") == id:
            title = post["title"][:50]
            return templates.TemplateResponse(
                request=request,
                name="post.html",
                context={
                    "post": post,
                    "title": title,
                },
            )
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post Not Found")


@app.get("/api/posts")
def get_posts():
   return posts

@app.get("/api/posts/{id}")#id inside get is a path parameteter that tells fast api this is part of the url and that is a variable 
def get_post_api(id: int ):
  for post in posts:
     if post.get("id")==id:
        return post 
     
  raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Post Not Found")

     

     
## StarletteHTTPException Handler
@app.exception_handler(StarletteHTTPException)
def general_http_exception_handler(request: Request, exception: StarletteHTTPException):
    message = (
        exception.detail
        if exception.detail
        else "An error occurred. Please check your request and try again."
    )

    if request.url.path.startswith("/api"):
        return JSONResponse(
            status_code=exception.status_code,
            content={"detail": message},
        )

    return templates.TemplateResponse(
        request=request,
        name="error.html",
        context={
            "request": request,
            "status_code": exception.status_code,
            "title": exception.status_code,
            "message": message,
        },
        status_code=exception.status_code,
    )


### RequestValidationError Handler
@app.exception_handler(RequestValidationError)
def validation_exception_handler(request: Request, exception: RequestValidationError):
    if request.url.path.startswith("/api"):
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            content={"detail": exception.errors()},
        )

    return templates.TemplateResponse(
        request=request,
        name="error.html",
        context={
            "request": request,
            "status_code": status.HTTP_422_UNPROCESSABLE_CONTENT,
            "title": status.HTTP_422_UNPROCESSABLE_CONTENT,
            "message": "Invalid request. Please check your input and try again.",
        },
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
    )

