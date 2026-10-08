from fastapi import FastAPI, Request, HTTPException, status
from fastapi.exception_handlers import request_validation_exception_handler
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from schemas import PostCreate, PostResponse



app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

posts: list[dict] = [
    {
        "id": 1,
        "author" : "Olalekan",
        "title": "Fast Api is Awesome",
        "content": "The framework is super fast and easy to use",
        "date_posted": "1/1/2025",
    },
    {

        "id": 2,
        "author" : "Toheeb",
        "title": "Fast Api is Awesome",
        "content": "Python is super fast and easy to use",
        "date_posted": "10/10/2025",
    }
]

@app.get("/", include_in_schema=False, name = "home")
def home(request: Request):
    return templates.TemplateResponse(request, "home.html", {"posts": posts, "title": "Home"})


@app.get("/posts/{post_id}", include_in_schema=False)
def get_postPage(request: Request, post_id: int):
        for post in posts:
            if post.get("id") == post_id:
                title = post["title"][:50]
                return templates.TemplateResponse(request, "post.html", {"posts": posts, "title": title})
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found") 

@app.get("/api/posts", response_model = list[PostResponse])
def get_posts():
    return posts

@app.post(
          "/api/create_posts", 
          response_model = PostResponse, 
          status_code=status.HTTP_201_CREATED)
def create_post(post: PostCreate):
    new_id = max(post["id"] for post in posts) + 1 if posts else 1
    new_post = {
         "id": new_id,
         "author": post.author,
         "title": post.title,
         "content": post.content,
          "date_posted": "2025-01-01",  # Placeholder date
    }
    posts.append(new_post)
    return new_post

@app.get("/api/posts/{post_id}", response_model = PostResponse)
def get_postById(post_id: int):
        for post in posts:
            if post["id"] == post_id:
                return {"data": post}
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")  

@app.exception_handler(StarletteHTTPException)
def http_exception_handler(request: Request, exc: StarletteHTTPException):
   message = exc.detail if exc.detail else "An error occurred."
   return templates.TemplateResponse(
       "error.html",
       {"request": request, "status_code": exc.status_code, "title": exc.status_code, "message": message},
       status_code=exc.status_code,
   )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request,
    exception: RequestValidationError,
):
    if request.url.path.startswith("/api"):
        return await request_validation_exception_handler(request, exception)

    return templates.TemplateResponse(
        request,
        "error.html",
        {
            "status_code": status.HTTP_422_UNPROCESSABLE_CONTENT,
            "title": status.HTTP_422_UNPROCESSABLE_CONTENT,
            "message": "Invalid request. Please check your input and try again.",
        },
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
    )