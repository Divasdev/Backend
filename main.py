# ==============================================================================
# FASTAPI BLOG APPLICATION
# Main Entry Point & Route Definitions
# ==============================================================================

# --- IMPORTS ---
# FastAPI: Core class to create the web application instance.
# Request: Class representing incoming HTTP requests (required for Jinja2 templates to build URLs).
# HTTPException: Exception raised to send HTTP error responses (e.g. 404 Not Found).
# status: Module containing HTTP status code constants (e.g. status.HTTP_404_NOT_FOUND).
from fastapi import FastAPI, Request, HTTPException, status

# RequestValidationError: Triggered automatically by FastAPI when request data/types fail validation.
from fastapi.exceptions import RequestValidationError

# JSONResponse: Returns structured JSON responses to client/API requests.
from fastapi.responses import JSONResponse

# StarletteHTTPException: Base exception class for HTTP errors in Starlette/FastAPI.
from starlette.exceptions import HTTPException as StarletteHTTPException

# Jinja2Templates: Configures Jinja2 template rendering engine for HTML pages.
from fastapi.templating import Jinja2Templates

# StaticFiles: Utility to serve static assets (CSS, JS, images, icons).
from fastapi.staticfiles import StaticFiles


# --- APPLICATION SETUP ---
# Create the main FastAPI application instance.
app = FastAPI()

# Mount the 'static' directory to serve static assets under the '/static' URL prefix.
# Example: '/static/css/main.css' maps to 'static/css/main.css' on disk.
app.mount("/static", StaticFiles(directory="static"), name="static")

# Configure Jinja2 templates directory location.
templates = Jinja2Templates(directory="templates")


# --- DUMMY DATA STORE ---
# In-memory database simulation using a Python list of dictionaries representing blog posts.
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


# ==============================================================================
# FRONTEND / HTML ROUTES (Renders Jinja2 HTML Templates)
# ==============================================================================

# Route: Home Page & Posts List Page
# Decorators bind HTTP GET requests for '/' and '/posts' to the home() function.
# include_in_schema=False hides these website HTML routes from the OpenAPI /docs page.
# name='home' / name='posts' allow reverse URL resolution using url_for('home') in templates.
@app.get("/", include_in_schema=False, name="home")
@app.get("/posts", include_in_schema=False, name="posts")
def home(request: Request):
    """
    Renders the main blog homepage (home.html) displaying all posts.
    
    Parameters:
    - request (Request): Incoming HTTP request object (required by Jinja2 for url_for generation).
    
    Returns:
    - TemplateResponse: Renders 'home.html' with the list of blog posts and page title.
    """
    return templates.TemplateResponse(
        request=request,
        name="home.html",
        context={
            "posts": posts,
            "title": "Home",
        },
    )


# Route: Single Post Detail Page
# {id} is a dynamic path parameter. FastAPI automatically converts it to an integer.
@app.get("/posts/{id}", include_in_schema=False)
def get_post(request: Request, id: int):
    """
    Renders the detail page (post.html) for a specific blog post by ID.
    
    Parameters:
    - request (Request): Incoming HTTP request object.
    - id (int): Dynamic post ID passed from the URL path.
    
    Returns:
    - TemplateResponse: Renders 'post.html' with the target post data.
    
    Raises:
    - HTTPException 404: If no post with the matching ID is found.
    """
    for post in posts:
        if post.get("id") == id:
            title = post["title"][:50]  # Truncate post title for page head title tag
            return templates.TemplateResponse(
                request=request,
                name="post.html",
                context={
                    "post": post,
                    "title": title,
                },
            )
    # If loop completes without finding a matching ID, raise a 404 Not Found error.
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post Not Found")


# ==============================================================================
# BACKEND REST API ROUTES (Returns Raw JSON Data)
# ==============================================================================

# API Endpoint: Get All Posts
@app.get("/api/posts")
def get_posts():
    """
    API endpoint returning all blog posts in raw JSON format.
    
    Returns:
    - list[dict]: List of dictionary post objects serialized automatically to JSON.
    """
    return posts


# API Endpoint: Get Single Post by ID
@app.get("/api/posts/{id}")
def get_post_api(id: int):
    """
    API endpoint returning a single post by its ID in raw JSON format.
    
    Parameters:
    - id (int): Post ID passed as a path parameter in URL (e.g. /api/posts/101).
    
    Returns:
    - dict: Matching post dictionary serialized to JSON.
    
    Raises:
    - HTTPException 404: If the specified post ID is not found.
    """
    for post in posts:
        if post.get("id") == id:
            return post

    # Raise 404 if post ID does not exist
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post Not Found")


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
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            content={"detail": exception.errors()},
        )

    # Render HTML error template for browser requests
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


