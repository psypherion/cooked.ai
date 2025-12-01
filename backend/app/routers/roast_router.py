from fastapi import APIRouter, UploadFile, File, Form, Depends
from app.services.ai_service import AIService
from app.services.spotify_service import SpotifyService
from app.models.api_models import RoastResponse

router = APIRouter()
spotify_service = SpotifyService()

@router.post("/generate-roast", response_model=RoastResponse)
async def generate_roast(
    image: UploadFile = File(None),
    name: str = Form(...),
    taste: str = Form(...)
):
    """
    Generate a roast based on user's name, taste (or Spotify token), and optional selfie.
    """
    # Process taste input (e.g., check if it's a Spotify token)
    processed_taste = spotify_service.process_input(taste)
    
    # Generate Roast
    roast_data = await AIService.generate_roast(name, processed_taste, image)
    
    return RoastResponse(
        status="success",
        data=roast_data
    )
