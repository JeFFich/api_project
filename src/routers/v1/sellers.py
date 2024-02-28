from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.configurations.database import get_async_session
from src.models.entities import Book, Seller
from src.schemas import BaseSeller, IncomingSeller, ReturnedAllSellers, ReturnedSeller

sellers_router = APIRouter(tags=["sellers"], prefix="/sellers")

DBSession = Annotated[AsyncSession, Depends(get_async_session)]


# Ручка для создания записи о продавце в БД.
@sellers_router.post("/", status_code=status.HTTP_201_CREATED, response_model=BaseSeller)
async def create_seller(seller: IncomingSeller, session: DBSession):
    # Создаем экземпляр продавца и добавляем его в БД
    new_seller = Seller(
        first_name=seller.first_name,
        last_name=seller.last_name,
        email=seller.email,
        password=seller.password,
    )
    session.add(new_seller)
    await session.flush()

    return new_seller


# Ручка для удаления продавца по id
@sellers_router.delete("/{seller_id}")
async def delete_seller(seller_id: int, session: DBSession):
    # Пытаемся найти продавца и удаляем, если он есть в БД
    deleted_seller = await session.get(Seller, seller_id)
    if deleted_seller:
        await session.delete(deleted_seller)

    return Response(status_code=status.HTTP_204_NO_CONTENT)


# Ручка для получения продавца по id
@sellers_router.get("/{seller_id}", response_model=ReturnedSeller)  # Прописываем модель ответа
async def get_seller(seller_id: int, session: DBSession):
    # Сперва пытаемся найти продавца и возвращаем 404, если не нашли в БД
    seller = await session.get(Seller, seller_id)
    if not seller:
        raise HTTPException(status_code=404, detail="Seller not found")

    # При существовании искомого продавца отбираем все связанные с ним книги из другой таблицы
    query = select(Book).where(Book.seller_id == seller_id)
    res = await session.execute(query)
    books = res.scalars().all()

    # Возвращаем результат
    return {
        "id": seller.id,
        "first_name": seller.first_name,
        "last_name": seller.last_name,
        "email": seller.email,
        "books": books        
    }


# Ручка для возврата списка продавцов
@sellers_router.get("/", response_model=ReturnedAllSellers)  # Прописываем модель ответа
async def get_all_sellers(session: DBSession):
    # Отбираем всех продавцов в БД и возвращаем их
    query = select(Seller)
    res = await session.execute(query)
    sellers = res.scalars().all()
    return {"sellers": sellers}


# Ручка для обновления данных о продавце; список книг и пароль, согласно контракту, не обновляются
@sellers_router.put("/{seller_id}", response_model=BaseSeller)
async def update_seller(seller_id: int, new_data: BaseSeller, session: DBSession):
    # Пытаемся найти запрашиваемого продавца и при находе изменяем поля
    if updated_seller := await session.get(Seller, seller_id):
        updated_seller.first_name = new_data.first_name
        updated_seller.last_name = new_data.last_name
        updated_seller.email = new_data.email

        await session.flush()

        return updated_seller

    # Возвращаем 404 если не нашли продавца
    return Response(status_code=status.HTTP_404_NOT_FOUND)
