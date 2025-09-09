from pydantic import BaseModel
from datetime import datetime

class InventoryBase(BaseModel):
    name: str
    quantity: int


class InventoryCreate(InventoryBase):
    pass


class InventoryUpdate(BaseModel):
    quantity: int


class InventoryResponse(InventoryBase):
    id: int
    updated_at: datetime

    class Config:
        from_attributes = True
