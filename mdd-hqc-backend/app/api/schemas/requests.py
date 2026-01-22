from pydantic import BaseModel


class PathRequest(BaseModel):
    path: str
