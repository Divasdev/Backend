from fastapi import FastAPI,Request
 
app=FastAPI()

posts=[
    {
        "id": 1,
        "title": "Hello FastAPI",
        "language": "Python",
        "description": "First API"
    }
]

@app.get("/posts")
def get_posts():
   return posts