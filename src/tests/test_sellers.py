import pytest
from fastapi import status
from sqlalchemy import select

from src.models import entities


# Тест на ручку создающую продавца
@pytest.mark.asyncio
async def test_create_seller(db_session, async_client):
    data = {"first_name": "Ivan", "last_name": "Ivanov", "email": "abc@ya.ru", "password": "123123123qq"}
    response = await async_client.post("/api/v1/sellers/", json=data)

    assert response.status_code == status.HTTP_201_CREATED

    all_sellers = await db_session.execute(select(entities.Seller))
    res = all_sellers.scalars().all()
    assert len(res) == 1
    result_data = response.json()
    
    assert result_data == {
        "id": res[0].id,
        "first_name": "Ivan",
        "last_name": "Ivanov",
        "email": "abc@ya.ru",
    }


# Тест на ручку получения одного продавца
@pytest.mark.asyncio
async def test_get_seller(db_session, async_client):
    # Создаем продавца вручную
    seller = entities.Seller(id=1, first_name="Ivan", last_name="Ivanov", email="abc@ya.ru", password="123123123qq")
    db_session.add(seller)

    # Добавляем ему книгу
    book = entities.Book(author="Lermontov", title="Mziri", year=1997, count_pages=104, seller_id=1)

    db_session.add(book)
    await db_session.flush()

    response = await async_client.get(f"/api/v1/sellers/{seller.id}")

    assert response.status_code == status.HTTP_200_OK

    # Проверяем интерфейс ответа, на который у нас есть контракт.
    assert response.json() == {
        "id": seller.id,
        "first_name": "Ivan",
        "last_name": "Ivanov",
        "email": "abc@ya.ru",
        "books": [{"id": book.id, "author": "Lermontov", "title": "Mziri", "year": 1997, "count_pages": 104}],
    }


# Тест на ручку получения списка продавцов
@pytest.mark.asyncio
async def test_get_all_sellers(db_session, async_client):
    # Создаем продавцов вручную
    seller_1 = entities.Seller(id=1, first_name="Ivan", last_name="Ivanov", email="abc@ya.ru", password="123123123qq")
    seller_2 = entities.Seller(id=2, first_name="Petr", last_name="Petrov", email="cba@ya.ru", password="qq123123123")

    db_session.add_all([seller_1, seller_2])
    await db_session.flush()

    response = await async_client.get("/api/v1/sellers/")

    assert response.status_code == status.HTTP_200_OK

    # Проверяем интерфейс ответа, на который у нас есть контракт.
    assert response.json() == {
        "sellers": [
            {"id": seller_1.id, "first_name": "Ivan", "last_name": "Ivanov", "email": "abc@ya.ru"},
            {"id": seller_2.id, "first_name": "Petr", "last_name": "Petrov", "email": "cba@ya.ru"},
        ]
    }


# Тест на ручку обновления продавца
@pytest.mark.asyncio
async def test_update_seller(db_session, async_client):
    # Создаем продавца вручную
    seller = entities.Seller(id=1, first_name="Ivan", last_name="Ivanov", email="abc@ya.ru", password="123123123qq")
    db_session.add(seller)
    await db_session.flush()

    response = await async_client.put(
        f"/api/v1/sellers/{seller.id}",
        json={"first_name": "Petr", "last_name": "Petrov", "email": "cba@ya.ru", "id": seller.id},
    )

    assert response.status_code == status.HTTP_200_OK
    await db_session.flush()

    # Проверяем, что обновились все поля
    res = await db_session.get(entities.Seller, seller.id)
    assert res.first_name == "Petr"
    assert res.last_name == "Petrov"
    assert res.email == "cba@ya.ru"
    assert res.id == seller.id


# Тест на ручку удаления продавца
@pytest.mark.asyncio
async def test_delete_seller(db_session, async_client):
    # Создаем продавца вручную
    seller = entities.Seller(id=1, first_name="Ivan", last_name="Ivanov", email="abc@ya.ru", password="123123123qq")
    db_session.add(seller)

    # Добавляем ему книгу
    book = entities.Book(author="Lermontov", title="Mziri", year=1997, count_pages=104, seller_id=1)

    db_session.add(book)

    await db_session.flush()

    response = await async_client.delete(f"/api/v1/sellers/{seller.id}")

    assert response.status_code == status.HTTP_204_NO_CONTENT
    await db_session.flush()

    # Проверяем что продавца удалили
    all_sellers = await db_session.execute(select(entities.Book))
    res = all_sellers.scalars().all()
    assert len(res) == 0

    # Проверяем что и связанные с продавцом книги удалились
    all_seller_books = await db_session.execute(select(entities.Book).where(entities.Book.seller_id == seller.id))
    res = all_seller_books.scalars().all()
    assert len(res) == 0
