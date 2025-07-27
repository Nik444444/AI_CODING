from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
from datetime import datetime
import os

# Создать приложение
app = FastAPI(
    title="Project API",
    description="API для проекта, созданного AI агентами",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Модели данных
class Item(BaseModel):
    id: Optional[str] = None
    name: str
    description: Optional[str] = None
    created_at: Optional[datetime] = None

class ItemCreate(BaseModel):
    name: str
    description: Optional[str] = None

# Временное хранилище (в продакшене заменить на MongoDB)
items_db = []

# Эндпоинты
@app.get("/")
async def root():
    return {
        "message": "API проекта работает!",
        "created_by": "AI Backend Developer",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now(),
        "service": "backend-api"
    }

@app.get("/items", response_model=List[Item])
async def get_items():
    return items_db

@app.post("/items", response_model=Item)
async def create_item(item: ItemCreate):
    new_item = Item(
        id=str(len(items_db) + 1),
        name=item.name,
        description=item.description,
        created_at=datetime.now()
    )
    items_db.append(new_item)
    return new_item

@app.get("/items/{item_id}", response_model=Item)
async def get_item(item_id: str):
    for item in items_db:
        if item.id == item_id:
            return item
    raise HTTPException(status_code=404, detail="Item not found")

@app.delete("/items/{item_id}")
async def delete_item(item_id: str):
    for i, item in enumerate(items_db):
        if item.id == item_id:
            del items_db[i]
            return {"message": "Item deleted"}
    raise HTTPException(status_code=404, detail="Item not found")

if __name__ == "__main__":
    uvicorn.run(
        "main:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=True
    )
