from pydantic import BaseModel
class RoomResponse(BaseModel):
    id: int
    supplier_code: int
    supplier_name: str
    supplier_room_name: str

    class Config:
        from_attributes = True