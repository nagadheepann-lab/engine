from __future__ import annotations

import logging

from fastapi import APIRouter, UploadFile, File, Form
from fastapi.responses import JSONResponse

from app.schemas.request import DecisionRequest
from app.schemas.response import DecisionResponse
from app.fusion.decision_engine import DecisionEngine

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "/decision-engine",
    response_model=DecisionResponse,
    summary="Run the Hybrid AI Decision Fusion Engine",
)
async def decision_engine_endpoint(
    farmer_name: str = Form(...),
    state: str = Form(...),
    district: str = Form(...),
    crop: str = Form(...),
    soil_type: str = Form(...),
    temperature: float = Form(...),
    humidity: float = Form(...),
    rainfall: float = Form(...),
    budget: float = Form(...),
    land_area: float = Form(...),
    image_upload: UploadFile | None = File(None),
    water_availability: str = Form(...),
    crop_stage: str = Form(...),
    expected_selling_price: float = Form(...),
) -> DecisionResponse:
    logger.info(
        "Received decision request: farmer=%s, crop=%s, district=%s",
        farmer_name,
        crop,
        district,
    )

    image_path: str | None = None
    if image_upload:
        import tempfile
        import os

        suffix = os.path.splitext(image_upload.filename)[1] or ".jpg"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            content = await image_upload.read()
            tmp.write(content)
            image_path = tmp.name
        logger.info("Image uploaded: %s", image_path)

    request = DecisionRequest(
        farmer_name=farmer_name,
        state=state,
        district=district,
        crop=crop,
        soil_type=soil_type,
        temperature=temperature,
        humidity=humidity,
        rainfall=rainfall,
        budget=budget,
        land_area=land_area,
        image_upload=image_path,
        water_availability=water_availability,
        crop_stage=crop_stage,
        expected_selling_price=expected_selling_price,
    )

    engine = DecisionEngine()
    response = await engine.run(request)

    if image_path and os.path.exists(image_path):
        os.unlink(image_path)

    return JSONResponse(content=response.model_dump())