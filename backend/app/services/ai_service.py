import os
import json
import chromadb
import face_recognition
import numpy as np
from PIL import Image
import io
from fastapi import UploadFile
from google import genai
from chromadb.utils import embedding_functions
from app.core.config import settings
from app.core.exceptions import RoastGenerationError

# Configure Gemini Client
client = genai.Client(api_key=settings.GEMINI_API_KEY)
MODEL_NAME = "gemini-2.5-flash-preview-09-2025"

# Setup ChromaDB Client
try:
    chroma_client = chromadb.PersistentClient(path=settings.CHROMA_DB_PATH)
    embedding_func = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="all-MiniLM-L6-v2"
    )
    
    # Text Collection
    roast_collection = chroma_client.get_or_create_collection(
        name="reddit_roasts", 
        embedding_function=embedding_func
    )
    
    # Face Collection (Placeholder for now, assuming it exists or will be created)
    # In a real scenario, this would be populated with face encodings of celebrities/roastable people
    face_collection = chroma_client.get_or_create_collection(
        name="reddit_faces"
    )
    
    print("✅ Connected to ChromaDB collections.")
except Exception as e:
    print(f"⚠️ Warning: Could not connect to ChromaDB. RAG will be disabled. Error: {e}")
    roast_collection = None
    face_collection = None

class AIService:
    @staticmethod
    def get_text_rag_context(query_text: str, n_results=3):
        """Retrieves similar roasts from the vector DB based on text."""
        if not roast_collection:
            return []
            
        try:
            results = roast_collection.query(
                query_texts=[query_text],
                n_results=n_results
            )
            return results['documents'][0]
        except Exception as e:
            print(f"⚠️ Text Retrieval Warning: {e}")
            return []

    @staticmethod
    def get_visual_rag_context(image_bytes: bytes, n_results=1):
        """
        Retrieves roast context based on face similarity.
        Uses face_recognition to get encoding, then queries ChromaDB.
        """
        if not face_collection:
            return None
            
        try:
            # Load image for face_recognition
            image = face_recognition.load_image_file(io.BytesIO(image_bytes))
            face_encodings = face_recognition.face_encodings(image)
            
            if not face_encodings:
                return None
                
            # Get the first face found
            query_encoding = face_encodings[0].tolist()
            
            results = face_collection.query(
                query_embeddings=[query_encoding],
                n_results=n_results
            )
            
            # Assuming metadata contains the roast or name associated with the lookalike
            if results['documents'] and results['documents'][0]:
                return results['documents'][0][0]
                
            return None
            
        except Exception as e:
            print(f"⚠️ Visual Retrieval Warning: {e}")
            return None

    @staticmethod
    async def generate_roast(name: str, taste: str, image: UploadFile = None):
        
        # 1. Retrieve RAG Context
        # Specific topic match
        specific_examples = AIService.get_text_rag_context(taste, n_results=3)
        # Style match (generic savage roasts)
        style_examples = AIService.get_text_rag_context("brutal savage devastating insult", n_results=3)
        
        all_examples = list(set(specific_examples + style_examples))
        examples_str = "\n- ".join(all_examples) if all_examples else "No examples found."
        
        visual_context = ""
        image_bytes = None
        
        # 2. Process Image & Visual RAG
        if image:
            print(f"📸 Processing image: {image.filename}")
            image_bytes = await image.read()
            
            # Reset cursor for Gemini
            # await image.seek(0) # Not needed if we pass bytes directly
            
            # Try Visual RAG
            lookalike_roast = AIService.get_visual_rag_context(image_bytes)
            if lookalike_roast:
                visual_context = f"\nVISUAL LOOKALIKE ROAST: The user looks like someone who deserves this: {lookalike_roast}"

        # 3. Construct Prompt
        prompt_text = f"""
        You are a ruthless, elitist pop-culture critic. Roast the user based on their data.
        
        USER NAME: {name}
        USER TASTE/HOBBIES: {taste}
        {visual_context}
        
        --- STYLE GUIDE (TONE & DELIVERY) ---
        Here are actual savage comments from the internet to guide your tone.
        DO NOT copy these exactly. Study their sentence structure, brevity, and cruelty.
        
        EXAMPLES:
        - {examples_str}
        --- END STYLE GUIDE ---
        
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

        # 4. Prepare content for Gemini
        contents = [prompt_text]
        
        if image_bytes:
            # Convert bytes to PIL Image for the SDK
            try:
                pil_image = Image.open(io.BytesIO(image_bytes))
                contents.append(pil_image)
            except Exception as e:
                print(f"❌ Error processing image for Gemini: {e}")

        # 5. Generate
        try:
            print("🔥 Sending to Gemini...")
            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=contents
            )
            
            # Clean response (remove markdown backticks if Gemini adds them)
            raw_text = response.text.strip()
            if raw_text.startswith("```json"):
                raw_text = raw_text[7:]
            if raw_text.endswith("```"):
                raw_text = raw_text[:-3]
                
            return json.loads(raw_text)

        except Exception as e:
            print(f"❌ AI Error: {e}")
            # Fallback JSON
            return {
                "user_profile": { "display_name": name, "archetype": "Unroastable NPC" },
                "roast": {
                    "headline": "Our AI broke trying to comprehend your blandness.",
                    "music_roast": "You broke the system.",
                    "movie_roast": "Try again later.",
                    "visual_roast": "Error analyzing image.",
                    "overall_verdict": "Server Error."
                },
                "stats": { "basic_score": 0, "red_flag_score": 0 },
                "verdict": { "verdict_1": "Error", "verdict_2": "Fail", "verdict_3": "404", "verdict_4": "Broke" }
            }
