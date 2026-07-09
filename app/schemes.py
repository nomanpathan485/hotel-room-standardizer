from pydantic import BaseModel


class RoomCreate(BaseModel):
    supplier_code: int
    supplier_name: str
    supplier_room_name: str


class RoomResponse(BaseModel):
    id: int
    supplier_code: int
    supplier_name: str
    supplier_room_name: str
    standard_room_name: str | None = None

    class Config:
        from_attributes = True