"""Request schemas shared by API endpoints that operate on filesystem paths."""

from pydantic import BaseModel


class PathRequest(BaseModel):
    """Carries the path of the artifact that one API request should process.

    This schema keeps path-based endpoints consistent when they need the caller to point
    to an existing file in the backend workspace.
    """

    path: str
