from enum import Enum, unique
from typing import Literal, TypeAlias


@unique
class Col(str, Enum):
    TRANS_DATE = "transaction_date"
    POST_DATE = "post_date"
    DESCRIPTION = "description"
    CATEGORY = "category"
    AMOUNT = "amount"


ColName: TypeAlias = Literal[
    Col.TRANS_DATE,
    Col.POST_DATE,
    Col.DESCRIPTION,
    Col.CATEGORY,
    Col.AMOUNT,
]
