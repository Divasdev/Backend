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
from pydantic import BaseModel,ConfigDict,Field

# ==============================================================================
# WHAT IS A PYDANTIC SCHEMA?
# A schema is like a "template" that describes the shape of data.
# When data arrives at our API, Pydantic checks it against this template
# automatically — no extra validation code needed from us.
# ==============================================================================


# --- BASE SCHEMA ---
# PostBase holds the fields that are SHARED by both the request and response schemas.
# Putting shared fields here avoids copy-pasting — other schemas will inherit from it.
class PostBase(BaseModel):
   # Each field uses a Python type hint (str, int, etc.).
   # FastAPI reads these hints to know what type of data is expected.
   # Field() adds extra rules — here we set minimum and maximum allowed lengths.
   title: str =Field(min_length=1,max_length=100)
   content: str =Field(min_length=1)
   author : str =Field(min_length=1,max_length=50)

# --- REQUEST SCHEMA (used for INCOMING data) ---
# PostCreate is the schema that VALIDATES data sent by the user when creating a post.
# It inherits title, content, and author from PostBase — no extra fields needed here.
# FastAPI will automatically reject requests that don't match this shape.
class PostCreate(PostBase):
   pass 


# --- RESPONSE SCHEMA (used for OUTGOING data) ---
# PostResponse is the schema that SHAPES the data we send BACK to the client.
# We add extra fields (id, date_posted) that the server generates — the user never sends these.
class PostResponse(PostBase):
   # from_attributes=True tells Pydantic it can also read data from an ORM/DB object
   # (like a SQLAlchemy model), not just from a plain Python dictionary.
   model_config=ConfigDict(from_attributes=True)

   # These two fields only appear in the RESPONSE — they are NOT part of the request.
   # FastAPI includes them automatically when returning post data to the client.
   id:int 
   date_posted: str 

   



