from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()

class Database:
    client: Optional[AsyncIOMotorClient] = None
    database = None

db = Database()

async def connect_to_mongo():
    """Подключение к MongoDB"""
    mongo_url = os.getenv("MONGO_URL", "mongodb://localhost:27017")
    db_name = os.getenv("DB_NAME", "project_db")
    
    db.client = AsyncIOMotorClient(mongo_url)
    db.database = db.client[db_name]
    
    print(f"Подключено к MongoDB: {db_name}")

async def close_mongo_connection():
    """Закрытие соединения с MongoDB"""
    if db.client:
        db.client.close()
        print("Соединение с MongoDB закрыто")

def get_database():
    """Получить экземпляр базы данных"""
    return db.database
