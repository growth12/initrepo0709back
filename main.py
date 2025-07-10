from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
import random
from datetime import datetime, timedelta

# FastAPI 앱 인스턴스 생성
app = FastAPI(
    title="Enhanced FastAPI 쇼핑몰 API",
    description="시각적으로 향상된 쇼핑몰 API 서버",
    version="2.0.0"
)

# CORS 미들웨어 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://56.155.27.230:3000", "http://localhost:3000"],  # 프론트가 띄워진 주소
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic 모델 정의
class Item(BaseModel):
    id: Optional[int] = None
    name: str
    description: Optional[str] = None
    price: float
    is_available: bool = True
    category: str = "기타"
    image_url: Optional[str] = None
    created_at: Optional[str] = None
    stock_count: int = 0
    rating: float = 0.0
    tags: List[str] = []

class ItemCreate(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    is_available: bool = True
    category: str = "기타"
    image_url: Optional[str] = None
    stock_count: int = 0
    tags: List[str] = []

class Statistics(BaseModel):
    total_items: int
    available_items: int
    total_value: float
    categories: dict
    avg_price: float

# 메모리 기반 데이터 저장소
items_db = []
item_id_counter = 1

# 샘플 데이터 생성
def initialize_sample_data():
    global item_id_counter
    sample_items = [
        {
            "name": "MacBook Pro M3",
            "description": "Apple의 최신 MacBook Pro with M3 chip",
            "price": 2500000,
            "category": "전자제품",
            "image_url": "https://images.unsplash.com/photo-1541807084-5c52b6b3adef?w=400",
            "stock_count": 5,
            "rating": 4.8,
            "tags": ["노트북", "Apple", "고성능"]
        },
        {
            "name": "Nike Air Max 270",
            "description": "편안한 일상용 운동화",
            "price": 180000,
            "category": "신발",
            "image_url": "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=400",
            "stock_count": 12,
            "rating": 4.5,
            "tags": ["운동화", "Nike", "편안함"]
        },
        {
            "name": "Samsung Galaxy S24",
            "description": "최신 Android 플래그십 스마트폰",
            "price": 1200000,
            "category": "전자제품",
            "image_url": "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=400",
            "stock_count": 8,
            "rating": 4.6,
            "tags": ["스마트폰", "Samsung", "Android"]
        },
        {
            "name": "Levi's 501 Original Jeans",
            "description": "클래식한 디자인의 데님 청바지",
            "price": 120000,
            "category": "의류",
            "image_url": "https://images.unsplash.com/photo-1542272604-787c3835535d?w=400",
            "stock_count": 15,
            "rating": 4.3,
            "tags": ["청바지", "Levi's", "클래식"]
        },
        {
            "name": "Starbucks Americano",
            "description": "진한 에스프레소의 깊은 맛",
            "price": 4500,
            "category": "음료",
            "image_url": "https://images.unsplash.com/photo-1509042239860-f550ce710b93?w=400",
            "stock_count": 50,
            "rating": 4.2,
            "tags": ["커피", "Starbucks", "아메리카노"]
        },
        {
            "name": "Sony WH-1000XM5",
            "description": "최고 수준의 노이즈 캔슬링 헤드폰",
            "price": 450000,
            "category": "전자제품",
            "image_url": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=400",
            "stock_count": 7,
            "rating": 4.9,
            "tags": ["헤드폰", "Sony", "노이즈캔슬링"]
        }
    ]
    
    for item_data in sample_items:
        new_item = Item(
            id=item_id_counter,
            created_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            **item_data
        )
        items_db.append(new_item)
        item_id_counter += 1

# 앱 시작 시 샘플 데이터 생성
initialize_sample_data()

# 루트 엔드포인트
@app.get("/")
async def root():
    return {
        "message": "Enhanced 쇼핑몰 API에 오신 것을 환영합니다!",
        "version": "2.0.0",
        "features": ["상품 관리", "통계", "카테고리 필터", "검색"],
        "total_items": len(items_db)
    }

# 헬스체크 엔드포인트
@app.get("/health")
async def health_check():
    return {
        "status": "healthy", 
        "message": "서버가 정상적으로 작동 중입니다",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "uptime": "운영 중"
    }

# 통계 엔드포인트
@app.get("/statistics", response_model=Statistics)
async def get_statistics():
    total_items = len(items_db)
    available_items = len([item for item in items_db if item.is_available])
    total_value = sum(item.price * item.stock_count for item in items_db)
    
    categories = {}
    for item in items_db:
        categories[item.category] = categories.get(item.category, 0) + 1
    
    avg_price = sum(item.price for item in items_db) / len(items_db) if items_db else 0
    
    return Statistics(
        total_items=total_items,
        available_items=available_items,
        total_value=total_value,
        categories=categories,
        avg_price=avg_price
    )

# 모든 아이템 조회 (필터링 및 정렬 기능 추가)
@app.get("/items", response_model=List[Item])
async def get_items(
    category: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    available_only: bool = False,
    sort_by: str = "id",
    order: str = "asc"
):
    filtered_items = items_db.copy()
    
    # 필터링
    if category:
        filtered_items = [item for item in filtered_items if item.category == category]
    if min_price is not None:
        filtered_items = [item for item in filtered_items if item.price >= min_price]
    if max_price is not None:
        filtered_items = [item for item in filtered_items if item.price <= max_price]
    if available_only:
        filtered_items = [item for item in filtered_items if item.is_available]
    
    # 정렬
    reverse = order == "desc"
    if sort_by == "price":
        filtered_items.sort(key=lambda x: x.price, reverse=reverse)
    elif sort_by == "rating":
        filtered_items.sort(key=lambda x: x.rating, reverse=reverse)
    elif sort_by == "name":
        filtered_items.sort(key=lambda x: x.name, reverse=reverse)
    else:
        filtered_items.sort(key=lambda x: x.id, reverse=reverse)
    
    return filtered_items

# 카테고리 목록 조회
@app.get("/categories")
async def get_categories():
    categories = list(set(item.category for item in items_db))
    category_counts = {}
    for item in items_db:
        category_counts[item.category] = category_counts.get(item.category, 0) + 1
    
    return {
        "categories": categories,
        "category_counts": category_counts
    }

# 검색 엔드포인트
@app.get("/search", response_model=List[Item])
async def search_items(q: str):
    if not q:
        return []
    
    search_term = q.lower()
    results = []
    
    for item in items_db:
        if (search_term in item.name.lower() or 
            (item.description and search_term in item.description.lower()) or
            any(search_term in tag.lower() for tag in item.tags)):
            results.append(item)
    
    return results

# 특정 아이템 조회
@app.get("/items/{item_id}", response_model=Item)
async def get_item(item_id: int):
    for item in items_db:
        if item.id == item_id:
            return item
    raise HTTPException(status_code=404, detail="아이템을 찾을 수 없습니다")

# 새 아이템 생성
@app.post("/items", response_model=Item)
async def create_item(item: ItemCreate):
    global item_id_counter
    
    # 랜덤 이미지 URL 생성 (이미지가 제공되지 않은 경우)
    if not item.image_url:
        image_topics = ["product", "technology", "fashion", "food", "electronics"]
        topic = random.choice(image_topics)
        item.image_url = f"https://images.unsplash.com/photo-1{random.randint(500000000, 699999999)}-{random.randint(100000000, 999999999)}?w=400&q=80&auto=format&fit=crop&topic={topic}"
    
    new_item = Item(
        id=item_id_counter,
        name=item.name,
        description=item.description,
        price=item.price,
        is_available=item.is_available,
        category=item.category,
        image_url=item.image_url,
        created_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        stock_count=item.stock_count,
        rating=round(random.uniform(3.0, 5.0), 1),  # 랜덤 평점
        tags=item.tags
    )
    items_db.append(new_item)
    item_id_counter += 1
    return new_item

# 아이템 업데이트
@app.put("/items/{item_id}", response_model=Item)
async def update_item(item_id: int, item: ItemCreate):
    for i, existing_item in enumerate(items_db):
        if existing_item.id == item_id:
            updated_item = Item(
                id=item_id,
                name=item.name,
                description=item.description,
                price=item.price,
                is_available=item.is_available,
                category=item.category,
                image_url=item.image_url or existing_item.image_url,
                created_at=existing_item.created_at,
                stock_count=item.stock_count,
                rating=existing_item.rating,
                tags=item.tags
            )
            items_db[i] = updated_item
            return updated_item
    raise HTTPException(status_code=404, detail="아이템을 찾을 수 없습니다")

# 아이템 삭제
@app.delete("/items/{item_id}")
async def delete_item(item_id: int):
    for i, item in enumerate(items_db):
        if item.id == item_id:
            deleted_item = items_db.pop(i)
            return {"message": f"아이템 '{deleted_item.name}'이 삭제되었습니다", "deleted_item": deleted_item}
    raise HTTPException(status_code=404, detail="아이템을 찾을 수 없습니다")

# 재고 업데이트
@app.patch("/items/{item_id}/stock")
async def update_stock(item_id: int, stock_count: int):
    for item in items_db:
        if item.id == item_id:
            item.stock_count = stock_count
            return {"message": f"아이템 '{item.name}'의 재고가 {stock_count}개로 업데이트되었습니다", "item": item}
    raise HTTPException(status_code=404, detail="아이템을 찾을 수 없습니다")

# 사용자 정보 엔드포인트
@app.get("/users/me")
async def read_user_me():
    return {
        "username": "관리자",
        "email": "admin@shopapi.com",
        "role": "admin",
        "last_login": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

# 경로 매개변수 예제
@app.get("/users/{user_id}")
async def read_user(user_id: int):
    return {
        "user_id": user_id,
        "username": f"사용자{user_id}",
        "email": f"user{user_id}@example.com",
        "created_at": (datetime.now() - timedelta(days=random.randint(1, 365))).strftime("%Y-%m-%d")
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)