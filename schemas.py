# ------------------------------------------------------------------------------
# WHY DO WE HAVE A SEPARATE schemas.py FILE?
# ------------------------------------------------------------------------------
# Instead of mixing data-shape rules with our route logic, we define them here.
# This keeps the code clean and reusable — any route in main.py can import and
# use these schemas without rewriting the same rules over and over.
# ------------------------------------------------------------------------------

# BaseModel  → the parent class from Pydantic that gives our schemas validation powers.
# ConfigDict → lets us configure how a schema behaves (e.g., reading from a DB model).
# Field      → lets us add extra rules to a field, like min/max length.
from pydantic import BaseModel,ConfigDict,Field,EmailStr

# ==============================================================================
# WHAT IS A PYDANTIC SCHEMA?
# A schema is like a "template" that describes the shape of data.
# When data arrives at our API, Pydantic checks it against this template
# automatically — no extra validation code needed from us.
# ==============================================================================
from datetime import datetime

class UserBase(BaseModel):
   username:str=Field(min_length=1,max_length=50)
   email:EmailStr=Field(max_length=120)
   
class UserCreate(UserBase):
   password:str=Field(min_length=8)

class UserPublic(BaseModel):
   model_config=ConfigDict(from_attributes=True)

   id:int 
   username:str
   image_file:str|None 
   image_path:str
   
class UserPrivate(UserPublic):
   email:EmailStr
   
   
   
   
class UserUpdate(BaseModel):
   username:str |None =Field( default=None,min_length=1,max_length=50)
   email:EmailStr | None =Field( default=None,max_length=120)
   image_file:str | None =Field(default=None,min_length=1,max_length=200)


class Token(BaseModel):
   access_token:str 
   token_type:str 
   
   
   



# --- BASE SCHEMA ---
# PostBase holds the fields that are SHARED by both the request and response schemas.
# Putting shared fields here avoids copy-pasting — other schemas will inherit from it.
class PostBase(BaseModel):
  
   title: str =Field(min_length=1,max_length=100)
   content: str =Field(min_length=1)
   


class PostCreate(PostBase):
   pass 


class PostUpdate(BaseModel):
   
   title: str | None =Field( default=None,min_length=1,max_length=100)
   content: str| None  =Field(default=None,min_length=1)
   

class PostResponse(PostBase):
   
   model_config=ConfigDict(from_attributes=True)

   # These two fields only appear in the RESPONSE — they are NOT part of the request.
   # FastAPI includes them automatically when returning post data to the client.
   id:int 
   user_id:int 
   date_posted: datetime
   author:UserPublic






