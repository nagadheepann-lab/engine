from __future__ import annotations

from pydantic import BaseModel, Field


class DecisionRequest(BaseModel):
    farmer_name: str = Field(..., min_length=1)
    state: str = Field(..., min_length=1)
    district: str = Field(..., min_length=1)
    crop: str = Field(..., min_length=1)
    soil_type: str = Field(..., min_length=1)
    temperature: float = Field(..., ge=-50, le=60)
    humidity: float = Field(..., ge=0, le=100)
    rainfall: float = Field(..., ge=0)
    budget: float = Field(..., gt=0)
    land_area: float = Field(..., gt=0)
    image_upload: str | None = None
    water_availability: str = Field(..., min_length=1)
    crop_stage: str = Field(..., min_length=1)
    expected_selling_price: float = Field(..., gt=0)

    model_config = {
        "json_schema_extra": {
            "example": {
                "farmer_name": "Rajesh Kumar",
                "state": "Maharashtra",
                "district": "Pune",
                "crop": "Groundnut",
                "soil_type": "Black",
                "temperature": 31.0,
                "humidity": 84.0,
                "rainfall": 620.0,
                "budget": 50000,
                "land_area": 5.0,
                "image_upload": None,
                "water_availability": "Moderate",
                "crop_stage": "Vegetative",
                "expected_selling_price": 6400,
            }
        }
    }