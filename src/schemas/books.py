from pydantic import BaseModel, Field, field_validator
from pydantic_core import PydanticCustomError

__all__ = ["IncomingBook", "ReturnedAllBooks", "ReturnedBook"]


# Базовый класс "Книги", содержащий поля, которые есть во всех классах-наследниках.
# Проверка на соответствие seller_id происходит при попытке записи в БД
class BaseBook(BaseModel):
    title: str
    author: str
    year: int
    seller_id: int


# Класс для валидации входящих данных. Не содержит id так как его присваивает БД.
class IncomingBook(BaseBook):
    year: int = 2024  # Пример присваивания дефолтного значения
    count_pages: int = Field(
        alias="pages",
        default=300,
    )  # Пример использования тонкой настройки полей. Передачи в них метаинформации.

    @field_validator("year")  # Валидатор, проверяет что дата не слишком древняя
    @staticmethod
    def validate_year(val: int):
        if val < 1900:
            raise PydanticCustomError("Validation error", "Year is wrong!")
        return val


# Класс, валидирующий исходящие данные. Он уже содержит id
class ReturnedBook(BaseBook):
    id: int
    count_pages: int


# Класс для возврата массива объектов "Книга"
class ReturnedAllBooks(BaseModel):
    books: list[ReturnedBook]


# Класс для возврата книги без seller_id (специально для ручки GET для конкретного продавца
class ReturnedBookWithoutSellerID(BaseModel):
    id: int
    title: str
    author: str
    year: int
    count_pages: int
    