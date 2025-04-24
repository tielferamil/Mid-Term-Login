from fastapi import FastAPI, Depends, HTTPException, applications, status, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from beanie import PydanticObjectId
from pydantic import BaseModel, EmailStr
from fastapi.responses import HTMLResponse
from auth import (
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token,
)
from models import User, FoodItem
from database import init_db
from typing import List
from datetime import datetime
from fastapi.staticfiles import StaticFiles


class FoodInput(BaseModel):
    name: str
    calories: int


app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", response_class=HTMLResponse)
async def serve_index():
    with open("index.html", "r") as f:
        return HTMLResponse(content=f.read(), status_code=200)


# Allow frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")


@app.on_event("startup")
async def app_init():
    await init_db()


async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    user_id = decode_access_token(token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    user = await User.get(PydanticObjectId(user_id))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@app.post("/signup")
async def signup(email: EmailStr = Body(...), password: str = Body(...)):
    if await User.find_one(User.email == email):
        raise HTTPException(status_code=400, detail="Email already registered")
    user = User(email=email, hashed_password=hash_password(password))
    await user.insert()
    return {"message": "User created successfully"}


@app.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await User.find_one(User.email == form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token({"sub": str(user.id)})
    return {"access_token": token, "token_type": "bearer"}


@app.post("/food")
async def log_food(food: FoodInput, user: User = Depends(get_current_user)):
    food_doc = FoodItem(
        user_id=str(user.id),
        name=food.name,
        calories=food.calories,
        timestamp=datetime.utcnow(),
    )
    await food_doc.insert()
    return {"message": "Food logged", "food": food_doc}


@app.get("/food", response_model=List[FoodItem])
async def get_food(user: User = Depends(get_current_user)):
    return await FoodItem.find(FoodItem.user_id == str(user.id)).to_list()


@app.delete("/food/{food_id}")
async def delete_food(food_id: str, user: User = Depends(get_current_user)):
    food = await FoodItem.get(PydanticObjectId(food_id))
    if not food or food.user_id != str(user.id):
        raise HTTPException(status_code=404, detail="Food not found")
    await food.delete()
    return {"message": "Food deleted"}
