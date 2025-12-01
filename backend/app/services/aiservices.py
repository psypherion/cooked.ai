import os
import json
import google.generativeai as genai
from fastapi import UploadFile
from dotenv import load_dotenv

load_dotenv()

# Configure the SDK
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Use the fast, multimodal model
MODEL_NAME = "gemini-2.5-flash-preview-09-2025"

class AIService:
    @staticmethod
    async def generate_roast(name: str, taste: str, image: UploadFile = None):
        model = genai.GenerativeModel(MODEL_NAME)
        
        # 1. Base Prompt
        prompt_text = f"""
        You are a ruthless, elitist pop-culture critic. Roast the user based on their data.
        
        USER NAME: {name}
        USER TASTE/HOBBIES: {taste}
        
        OUTPUT FORMAT: Return ONLY valid JSON matching this structure:
        {{
            "user_profile": {{ "display_name": "{name}", "archetype": "An insulting 2-5 word title" }},
            "roast": {{
                "headline": "A brutal, short summary sentence.",
                "music_roast": "Roast their specific music taste or lack thereof.",
                "movie_roast": "Roast their movie choices.",
                "visual_roast": "Analyze the image if provided, otherwise leave empty.",
                "overall_verdict": "Final judgment."
            }},
            "stats": {{ "basic_score": (0-100), "red_flag_score": (0-100) }},
            "verdict": {{ "verdict_1": "Word", "verdict_2": "Word", "verdict_3": "Word", "verdict_4": "Word" }}
        }}
        """

        # 2. Prepare content parts
        content_parts: list = [prompt_text]

        # 3. Process Image if uploaded
        if image:
            print(f"📸 Processing image: {image.filename}")
            image_bytes = await image.read()
            
            # Add image blob to the prompt parts
            content_parts.append({
                "mime_type": image.content_type,
                "data": image_bytes
            })
            
            # Reset cursor just in case
            await image.seek(0)

        # 4. Generate
        try:
            print("🔥 Sending to Gemini...")
            response = model.generate_content(content_parts)
            
            # Clean response (remove markdown backticks if Gemini adds them)
            raw_text = response.text.strip()
            if raw_text.startswith("```json"):
                raw_text = raw_text[7:]
            if raw_text.endswith("```"):
                raw_text = raw_text[:-3]
                
            return json.loads(raw_text)

        except Exception as e:
            print(f"❌ AI Error: {e}")
            # Fallback JSON to prevent app crash
            return {
                "user_profile": { "display_name": name, "archetype": "Unroastable NPC" },
                "roast": {
                    "headline": "Our AI broke trying to comprehend your blandness.",
                    "music_roast": "You broke the system.",
                    "movie_roast": "Try again later.",
                    "overall_verdict": "Server Error."
                },
                "stats": { "basic_score": 0, "red_flag_score": 0 },
                "verdict": { "verdict_1": "Error", "verdict_2": "Fail", "verdict_3": "404", "verdict_4": "Broke" }
            }