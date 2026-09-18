from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import FastAPI, Request, HTTPException, status, Depends
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from starlette.exceptions import HTTPException as StarletteHTTPException

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

import models

from database import Base, engine, get_db

from schemas import (
    PostCreate,
    PostResponse,
    UserCreate,
    UserResponse,
    PostUpdate,
    UserUpdate,
)


# ==============================================================================
# DATABASE LIFESPAN
# ==============================================================================

@asynccontextmanager
async def lifespan(_app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    await engine.dispose()


# ==============================================================================
# FASTAPI APP
# ==============================================================================

app = FastAPI(lifespan=lifespan)


# ==============================================================================
# STATIC FILES
# ==============================================================================

app.mount(
    "/static",
    StaticFiles(directory="static"),
    name="static",
)

app.mount(
    "/media",
    StaticFiles(directory="media"),
    name="media",
)


# ==============================================================================
# TEMPLATES
# ==============================================================================

templates = Jinja2Templates(directory="templates")


# ==============================================================================
# FRONTEND / HTML ROUTES
# ==============================================================================


# Home page
@app.get("/", include_in_schema=False, name="home")
@app.get("/posts", include_in_schema=False, name="posts")
async def home(
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    result = await db.execute(
        select(models.Post)
        .options(selectinload(models.Post.author))
    )

    posts = result.scalars().all()

    return templates.TemplateResponse(
        request,
        "home.html",
        {
            "posts": posts,
            "title": "Home",
        },
    )


# Single post page
@app.get("/posts/{post_id}", include_in_schema=False)
async def post_page(
    request: Request,
    post_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    result = await db.execute(
        select(models.Post)
        .options(selectinload(models.Post.author))
        .where(models.Post.id == post_id),
    )

    post = result.scalars().first()

    if post:
        title = post.title[:50]

        return templates.TemplateResponse(
            request,
            "post.html",
            {
                "post": post,
                "title": title,
            },
        )

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Post not found",
    )


# User posts page
@app.get(
    "/users/{user_id}/posts",
    include_in_schema=False,
    name="user_posts",
)
async def user_posts_page(
    request: Request,
    user_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    result = await db.execute(
        select(models.User).where(models.User.id == user_id)
    )

    user = result.scalars().first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    result = await db.execute(
        select(models.Post)
        .options(selectinload(models.Post.author))
        .where(models.Post.user_id == user_id),
    )

    posts = result.scalars().all()

    return templates.TemplateResponse(
        request,
        "user_posts.html",
        {
            "posts": posts,
            "user": user,
            "title": f"{user.username}'s Posts",
        },
    )


# ==============================================================================
# USER CRUD
# ==============================================================================


# CREATE USER
@app.post(
    "/api/users",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_user(
    user: UserCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    # Check username
    result = await db.execute(
        select(models.User).where(
            models.User.username == user.username
        )
    )

    existing_user = result.scalars().first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists",
        )

    # Check email
    result = await db.execute(
        select(models.User).where(
            models.User.email == user.email
        )
    )

    existing_email = result.scalars().first()

    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # Create user
    new_user = models.User(
        username=user.username,
        email=user.email,
    )

    db.add(new_user)

    await db.commit()
    await db.refresh(new_user)

    return new_user


# GET USER
@app.get(
    "/api/users/{user_id}",
    response_model=UserResponse,
)
async def get_user(
    user_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    result = await db.execute(
        select(models.User).where(
            models.User.id == user_id
        )
    )

    user = result.scalars().first()

    if user:
        return user

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="User not found",
    )


# GET USER POSTS
@app.get(
    "/api/users/{user_id}/posts",
    response_model=list[PostResponse],
)
async def get_user_posts(
    user_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    # Check if user exists
    result = await db.execute(
        select(models.User).where(
            models.User.id == user_id
        )
    )

    user = result.scalars().first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Get posts
    result = await db.execute(
        select(models.Post)
        .options(selectinload(models.Post.author))
        .where(models.Post.user_id == user_id),
    )

    posts = result.scalars().all()

    return posts


# UPDATE USER
@app.patch(
    "/api/users/{user_id}",
    response_model=UserResponse,
)
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    # Find user
    result = await db.execute(
        select(models.User).where(
            models.User.id == user_id
        )
    )

    user = result.scalars().first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Check username uniqueness
    if (
        user_update.username is not None
        and user_update.username != user.username
    ):
        result = await db.execute(
            select(models.User).where(
                models.User.username == user_update.username,
                models.User.id != user_id,
            )
        )

        existing_user = result.scalars().first()

        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already exists",
            )

    # Check email uniqueness
    if (
        user_update.email is not None
        and user_update.email != user.email
    ):
        result = await db.execute(
            select(models.User).where(
                models.User.email == user_update.email,
                models.User.id != user_id,
            )
        )

        existing_email = result.scalars().first()

        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )

    # Update fields
    if user_update.username is not None:
        user.username = user_update.username

    if user_update.email is not None:
        user.email = user_update.email

    if user_update.image_file is not None:
        user.image_file = user_update.image_file

    await db.commit()
    await db.refresh(user)

    return user


# DELETE USER
@app.delete(
    "/api/users/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_user(
    user_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    result = await db.execute(
        select(models.User).where(
            models.User.id == user_id
        )
    )

    user = result.scalars().first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    await db.delete(user)

    await db.commit()


# ==============================================================================
# POST CRUD
# ==============================================================================


# GET ALL POSTS
@app.get(
    "/api/posts",
    response_model=list[PostResponse],
)
async def get_posts(
    db: Annotated[AsyncSession, Depends(get_db)],
):
    result = await db.execute(
        select(models.Post)
        .options(selectinload(models.Post.author))
    )

    posts = result.scalars().all()

    return posts


# CREATE POST
@app.post(
    "/api/posts",
    response_model=PostResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_post(
    post: PostCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    # Check whether user exists
    result = await db.execute(
        select(models.User).where(
            models.User.id == post.user_id
        )
    )

    user = result.scalars().first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Create post
    new_post = models.Post(
        title=post.title,
        content=post.content,
        user_id=post.user_id,
    )

    db.add(new_post)

    await db.commit()

    # Load author relationship
    await db.refresh(
        new_post,
        attribute_names=["author"],
    )

    return new_post


# GET SINGLE POST
@app.get(
    "/api/posts/{post_id}",
    response_model=PostResponse,
)
async def get_post(
    post_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    result = await db.execute(
        select(models.Post)
        .options(selectinload(models.Post.author))
        .where(models.Post.id == post_id),
    )

    post = result.scalars().first()

    if post:
        return post

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Post not found",
    )


# FULL UPDATE POST
@app.put(
    "/api/posts/{post_id}",
    response_model=PostResponse,
)
async def update_post_full(
    post_id: int,
    post_data: PostCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    # Find post
    result = await db.execute(
        select(models.Post).where(
            models.Post.id == post_id
        )
    )

    post = result.scalars().first()

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found",
        )

    # Check new user if user_id is changing
    if post_data.user_id != post.user_id:
        result = await db.execute(
            select(models.User).where(
                models.User.id == post_data.user_id
            )
        )

        user = result.scalars().first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

    # Update all fields
    post.title = post_data.title
    post.content = post_data.content
    post.user_id = post_data.user_id

    await db.commit()

    await db.refresh(
        post,
        attribute_names=["author"],
    )

    return post


# PARTIAL UPDATE POST
@app.patch(
    "/api/posts/{post_id}",
    response_model=PostResponse,
)
async def update_post_partial(
    post_id: int,
    post_data: PostUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    # Find post
    result = await db.execute(
        select(models.Post).where(
            models.Post.id == post_id
        )
    )

    post = result.scalars().first()

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found",
        )

    # Get only provided fields
    update_data = post_data.model_dump(
        exclude_unset=True
    )

    # Update fields
    for field, value in update_data.items():
        setattr(post, field, value)

    await db.commit()

    await db.refresh(
        post,
        attribute_names=["author"],
    )

    return post


# DELETE POST
@app.delete(
    "/api/posts/{post_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_post(
    post_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    result = await db.execute(
        select(models.Post).where(
            models.Post.id == post_id
        )
    )

    post = result.scalars().first()

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found",
        )

    await db.delete(post)

    await db.commit()


# ==============================================================================
# GLOBAL EXCEPTION HANDLERS
# ==============================================================================


# HTTP Exception Handler
@app.exception_handler(StarletteHTTPException)
async def general_http_exception_handler(
    request: Request,
    exception: StarletteHTTPException,
):
    """
    Handles HTTP exceptions.

    API routes:
        Returns JSON.

    Browser routes:
        Returns error.html.
    """

    message = (
        exception.detail
        if exception.detail
        else "An error occurred. Please check your request and try again."
    )

    # API error
    if request.url.path.startswith("/api"):
        return JSONResponse(
            status_code=exception.status_code,
            content={
                "detail": message,
            },
        )

    # Browser error
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


# Validation Exception Handler
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request,
    exception: RequestValidationError,
):
    """
    Handles request validation errors.

    API routes:
        Returns JSON validation errors.

    Browser routes:
        Returns error.html.
    """

    # API validation error
    if request.url.path.startswith("/api"):
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "detail": exception.errors(),
            },
        )

    # Browser validation error
    return templates.TemplateResponse(
        request=request,
        name="error.html",
        context={
            "request": request,
            "status_code": status.HTTP_422_UNPROCESSABLE_ENTITY,
            "title": status.HTTP_422_UNPROCESSABLE_ENTITY,
            "message": "Invalid request. Please check your input and try again.",
        },
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
    )