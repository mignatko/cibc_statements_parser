from enum import Enum, unique
from typing import Literal


@unique
class Col(str, Enum):
    TRANS_DATE = "transaction_date"
    POST_DATE = "post_date"
    DESCRIPTION = "description"
    STORE_NAME = "store_name"
    PROVINCE = "province"
    CITY = "city"
    CATEGORY = "category"
    AMOUNT = "amount"


type ColName = Literal[
    Col.TRANS_DATE,
    Col.POST_DATE,
    Col.DESCRIPTION,
    Col.STORE_NAME,
    Col.PROVINCE,
    Col.CITY,
    Col.CATEGORY,
    Col.AMOUNT,
]
