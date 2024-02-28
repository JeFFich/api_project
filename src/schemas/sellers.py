from pydantic import BaseModel, field_validator
from pydantic_core import PydanticCustomError

from .books import ReturnedBookWithoutSellerID

__all__ = ["IncomingSeller", "ReturnedAllSellers", "ReturnedSeller", "BaseSeller"]


# Базовый класс "Продавца", содержащий общие поля, необходимые для создания объекта
class BasePostSeller(BaseModel):
    first_name: str
    last_name: str
    email: str
    password: str


# Базовый класс возвращаемого провдавца; содержит id и не содержит пароля
class BaseSeller(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: str


# Класс для валидации входящих данных. Не содержит id так как его присваивает БД.
class IncomingSeller(BasePostSeller):
    @field_validator("password")  # Валидатор, что длина пароля не менее 8 символов
    @staticmethod
    def validate_password(val: int):
        if len(val) < 8:
            raise PydanticCustomError("Validation error", "Password too short!")
        return val


# Класс, валидирующий исходящие данные; к базовому классу возврата добавляется еще список книг, очищенных от seller_id
class ReturnedSeller(BaseSeller):
    books: list[ReturnedBookWithoutSellerID]


# Класс для возврата всего списка продавцов; список книг не возвращается, как было прописано в контракте
class ReturnedAllSellers(BaseModel):
    sellers: list[BaseSeller]
