from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient
from models import User, FoodItem

MONGO_URI = "mongodb+srv://tielferamil:KHp0Wvip8ohKtawk@cluster0.9mh9yk6.mongodb.net/mydb?retryWrites=true&w=majority"


async def init_db():
    client = AsyncIOMotorClient(MONGO_URI)
    await init_beanie(
        database=client.get_default_database(), document_models=[User, FoodItem]
    )
