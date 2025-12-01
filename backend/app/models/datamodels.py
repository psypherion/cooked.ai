from pydantic import BaseModel
from typing import Optional, Dict

# 1. The Output Structure (What we send to Frontend)
class UserProfile(BaseModel):
    display_name: str
    archetype: str

class RoastContent(BaseModel):
    headline: str
    music_roast: str
    movie_roast: str
    visual_roast: Optional[str] = None
    overall_verdict: str

class Stats(BaseModel):
    basic_score: int
    red_flag_score: int

class Verdicts(BaseModel):
    verdict_1: str
    verdict_2: str
    verdict_3: str
    verdict_4: str

class RoastResponse(BaseModel):
    status: str
    data: Dict[str, UserProfile | RoastContent | Stats | Verdicts]
    
class RoastData(BaseModel):
    user_profile: UserProfile
    roast: RoastContent
    stats: Stats
    verdict: Verdicts

class APIResponse(BaseModel):
    status: str
    data: RoastData