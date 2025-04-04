from pydantic import BaseModel

class UserCreate(BaseModel):
    username: str
    hashed_password: str

class UserOut(BaseModel):
    id: int
    username: str

    class Config:
        orm_mode = True
