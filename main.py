
from fastapi import FastAPI, Request, HTTPException, status,Depends

from fastapi.exceptions import RequestValidationError

from fastapi.responses import JSONResponse

from starlette.exceptions import HTTPException as StarletteHTTPException

from fastapi.templating import Jinja2Templates

from fastapi.staticfiles import StaticFiles

from schemas import PostCreate,PostResponse

from typing import Annotated
from sqlalchemy import select

from sqlalchemy.orm import Session

import models
from database import Base,engine,get_db
from schemas import (
        PostCreate,
        PostResponse,
        UserCreate,
        UserResponse,
        PostUpdate,
        UserUpdate
    )


Base.metadata.create_all(bind=engine)


app = FastAPI()


app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/media",StaticFiles(directory="media"),name="media")

# Configure Jinja2 templates directory location.
templates = Jinja2Templates(directory="templates")



@app.get("/", include_in_schema=False, name="home")
@app.get("/posts", include_in_schema=False, name="posts")
def home(request: Request, db: Annotated[Session, Depends(get_db)]):
    """
    Renders the main blog homepage (home.html) displaying all posts.
    
    Parameters:
    - request (Request): Incoming HTTP request object (required by Jinja2 for url_for generation).
    
    Returns:
    - TemplateResponse: Renders 'home.html' with the list of blog posts and page title.
    """
    ## home

    result = db.execute(select(models.Post))
    posts = result.scalars().all()
    return templates.TemplateResponse(
        request,
        "home.html",
        {"posts": posts, "title": "Home"},
    )



# Route: Single Post Detail Page
# {id} is a dynamic path parameter. FastAPI automatically converts it to an integer.
## post_page
@app.get("/posts/{post_id}", include_in_schema=False)
def post_page(request: Request, post_id: int, db: Annotated[Session, Depends(get_db)]):
    result = db.execute(select(models.Post).where(models.Post.id == post_id))
    post = result.scalars().first()
    if post:
        title = post.title[:50]
        return templates.TemplateResponse(
            request,
            "post.html",
            {"post": post, "title": title},
        )
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")


## user_posts_page
@app.get("/users/{user_id}/posts", include_in_schema=False, name="user_posts")
def user_posts_page(
    request: Request,
    user_id: int,
    db: Annotated[Session, Depends(get_db)],
):
    result = db.execute(select(models.User).where(models.User.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    result = db.execute(select(models.Post).where(models.Post.user_id == user_id))
    posts = result.scalars().all()
    return templates.TemplateResponse(
        request,
        "user_posts.html",
        {"posts": posts, "user": user, "title": f"{user.username}'s Posts"},
    )


@app.post(
    "/api/users",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def  create_user(user:UserCreate,db:Annotated[Session,Depends(get_db)]):
    result=db.execute(select(models.User).where(models.User.username==user.username),
    )
                      
    existing_user=result.scalars().first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists",
    )
        
    result=db.execute(select(models.User).where(models.User.email==user.email),
    )
                      
    existing_email=result.scalars().first()
    
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already exists",
        )
        
    new_user=models.User(
        username=user.username,
        email=user.email , 
        
    )
    
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user

@app.get("/api/users/{user_id}",response_model=UserResponse)
def get_user(user_id:int,db:Annotated[Session,Depends(get_db)]):
    result=db.execute(
         select(models.User).where(models.User.id==user_id
                                   ),
    )
    user=result.scalars().first()
    
    if user:
        return user
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="User Not Found")

## get_user_posts
@app.get("/api/users/{user_id}/posts", response_model=list[PostResponse])
def get_user_posts(user_id: int, db: Annotated[Session, Depends(get_db)]):
    result = db.execute(select(models.User).where(models.User.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    result = db.execute(select(models.Post).where(models.Post.user_id == user_id))
    posts = result.scalars().all()
    return posts


## update_user

## update_user
@app.patch("/api/users/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    user_update: UserUpdate,
    db: Annotated[Session, Depends(get_db)],
):
    result = db.execute(
        select(models.User).where(models.User.id == user_id)
    )
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Check username uniqueness
    if user_update.username is not None and user_update.username != user.username:
        result = db.execute(
            select(models.User).where(
                models.User.username == user_update.username,
                models.User.id != user_id,
            )
        )

        if result.scalar_one_or_none() is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already exists",
            )

    # Check email uniqueness
    if user_update.email is not None and user_update.email != user.email:
        result = db.execute(
            select(models.User).where(
                models.User.email == user_update.email,
                models.User.id != user_id,
            )
        )

        if result.scalar_one_or_none() is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )

    # Update only fields provided in PATCH request
    update_data = user_update.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(user, field, value)

    db.commit()
    db.refresh(user)

    return user

## delete_user
@app.delete("/api/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Annotated[Session, Depends(get_db)]):
    result = db.execute(select(models.User).where(models.User.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    db.delete(user)
    db.commit()





    
    
    
    


# API Endpoint: Get All Posts
# response_model=list[PostResponse] tells FastAPI:
# "When you send data back, filter it through the PostResponse schema."
# This means fields that are NOT in PostResponse (like 'published', 'views') will be hidden.
# This is called RESPONSE VALIDATION — we control exactly what the client sees.
## get_posts
@app.get("/api/posts", response_model=list[PostResponse])
def get_posts(db: Annotated[Session, Depends(get_db)]):
    result = db.execute(select(models.Post))
    posts = result.scalars().all()
    return posts



# response_model=PostResponse means the single post returned will also be filtered
# through our schema — same idea as above, just for one post instead of a list.
#
# status_code=201 means we send back "201 Created" instead of the default "200 OK".
# This is the correct HTTP status code when a new resource has been created.
## create_post
@app.post(
    "/api/posts",
    response_model=PostResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_post(post: PostCreate, db: Annotated[Session, Depends(get_db)]):
    result = db.execute(select(models.User).where(models.User.id == post.user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    new_post = models.Post(
        title=post.title,
        content=post.content,
        user_id=post.user_id,
    )
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post


# API Endpoint: Get Single Post by ID
# response_model=PostResponse here too — even for a GET by ID, we still filter
# the response so the client only sees the fields defined in PostResponse.
## get_post

@app.get("/api/posts/{post_id}", response_model=PostResponse)
def get_post(post_id: int, db: Annotated[Session, Depends(get_db)]):
    result = db.execute(select(models.Post).where(models.Post.id == post_id))
    post = result.scalars().first()
    if post:
        return post
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")



@app.put("/api/posts/{post_id}", response_model=PostResponse)
def update_post_full(
    post_id: int,
    post_data:PostCreate,
    db: Annotated[Session, Depends(get_db)]):
    
    result = db.execute(select(models.Post).where(models.Post.id == post_id))
    post = result.scalars().first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
        )
            
        if post_data.user_id!=post.user_id:
            result = db.execute(select(models.User).where(models.User.id == post_data.user_id)
        )
            
        user = result.scalars().first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        new_post = models.Post(
            title=post.title,
            content=post.content,
            user_id=post.user_id,
        )
        db.add(new_post)
        db.commit()
        db.refresh(new_post)
        return new_post
    post.title=post_data.title
    post.content=post_data.content
    post.user_id=post_data.user_id
    
    db.commit()
    db.refresh(post)
    return post 



@app.patch("/api/posts/{post_id}", response_model=PostResponse)
def update_post_partial(
    post_id: int,
    post_data:PostUpdate,
    db: Annotated[Session, Depends(get_db)]):
    
    result = db.execute(select(models.Post).where(models.Post.id == post_id))
    post = result.scalars().first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
        )
    
    
    update_data=post_data.model_dump(exclude_unset=True)
    for field,value in update_data.items():
        setattr(post,field,value)
        
        
    db.commit()
    db.refresh(post)
    return post 

@app.delete("/api/posts/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(
    post_id: int,
    db: Annotated[Session, Depends(get_db)]
):
    result = db.execute(
        select(models.Post).where(models.Post.id == post_id)
    )

    post = result.scalars().first()

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )

    db.delete(post)
    db.commit()

    return

# ==============================================================================
# GLOBAL EXCEPTION HANDLERS (Custom Error Handling)
# ==============================================================================

# Exception Handler: Catches all standard Starlette/FastAPI HTTP Exceptions (e.g., 404, 500)
@app.exception_handler(StarletteHTTPException)
def general_http_exception_handler(request: Request, exception: StarletteHTTPException):
    """
    Custom exception handler for HTTP status errors across the application.
    - If request is for an API route (/api/...), returns a JSON error response.
    - If request is for a browser route, renders the friendly error.html template.
    """
    message = (
        exception.detail
        if exception.detail
        else "An error occurred. Please check your request and try again."
    )

    # Return JSON for API calls
    if request.url.path.startswith("/api"):
        return JSONResponse(
            status_code=exception.status_code,
            content={"detail": message},
        )

    # Render HTML page for frontend browser calls
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


# Exception Handler: Catches Request Validation Errors (e.g., passing letters for an integer ID)
@app.exception_handler(RequestValidationError)
def validation_exception_handler(request: Request, exception: RequestValidationError):
    """
    Custom exception handler for request validation failures (e.g. invalid query or path parameters).
    - Returns detailed JSON validation errors for API requests (/api/...).
    - Renders a 422 error page for frontend browser requests.
    """
    # Return JSON validation details for API requests
    if request.url.path.startswith("/api"):
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"detail": exception.errors()},
        )

    # Render HTML error template for browser requests
    return templates.TemplateResponse(
        request=request,
        name="error.html",
        context={
            "request": request,
           "status_code": status.HTTP_422_UNPROCESSABLE_ENTITY,
           "title": status.HTTP_422_UNPROCESSABLE_ENTITY,
            "message": "Invalid request. Please check your input and try again.",
        },
        # HTTP_422_UNPROCESSABLE_ENTITY is the correct constant name in FastAPI/Starlette.
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
    )


