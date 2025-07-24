from pydantic import BaseModel
from typing import Optional, Any
from fastapi.responses import JSONResponse

class APIResponse(BaseModel):
    status: str = "success"         # "success" or "error"
    message: Optional[str] = None   # optional explanation
    data: Optional[Any] = None      # actual payload
    
def create_response(status_code: int, message: str, data: Optional[Any] = None) -> JSONResponse:
    """
    Create a response with data and optional message.
    """
    return JSONResponse(status_code=status_code, content=APIResponse(status= "success" if status_code==200 else "error", message=message, data=data).model_dump())