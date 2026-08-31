from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any

class ProcessRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=1000, description="Product description text from the seller")
    language: str = Field(default="auto", description="Language mode: auto, English, Hindi")

class ApproveRequest(BaseModel):
    product_name: str
    category: str
    subcategory: str
    attributes: Dict[str, Any]
