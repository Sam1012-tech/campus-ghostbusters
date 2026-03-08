from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import math

# Initialize the app
app = FastAPI(title="Ghostbusters API")

#Allow the React frontend to talk to this backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins for small projects
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# data validation, pydantic models
class PlayerLocation(BaseModel):
    username: str
    lat: float
    lon: float

# --- 2. THE MATH ENGINE (Your Territory) ---
def get_distance(lat1, lon1, lat2, lon2):
    """
    Calculates distance. Uses Haversine for GPS coordinates.
    (If your team chooses a 2D simulation, you can swap this for simple Pythagorean math).
    """
    R = 6371000  # Radius of Earth in meters
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def calculate_flee_vector(p_lat, p_lon, g_lat, g_lon):
    """Pushes the ghost further away along the same vector."""
    v_lat = g_lat - p_lat
    v_lon = g_lon - p_lon
    
    # 1.5 multiplier pushes it 50% further away
    return g_lat + (v_lat * 1.5), g_lon + (v_lon * 1.5)

# --- 3. API ENDPOINTS ---

@app.get("/")
def health_check():
    return {"status": "online", "message": "Ghostbusters Backend is running!"}

@app.post("/scan")
def scan_for_ghosts(player: PlayerLocation):
    # HARDCODED GHOST for you to test with right now.
    # Tell your DB partner to write a function that replaces this with a real database query later!
    nearest_ghost = {
        "id": 1, 
        "type": "Poltergeist", 
        "lat": 13.0285, # Rough coordinates for MSRIT area
        "lon": 77.5653 
    }
    
    # Calculate how far the player is from the ghost
    distance = get_distance(player.lat, player.lon, nearest_ghost["lat"], nearest_ghost["lon"])
    
    # LOGIC 1: Player is right on top of it (Busted!)
    if distance <= 5:
        # TODO: Tell DB partner to write a function to add points to the user here
        return {
            "status": "busted",
            "message": f"You trapped the {nearest_ghost['type']}!",
            "distance_meters": round(distance)
        }
        
    # LOGIC 2: Player got too close (Anti-Gravity Triggered!)
    elif distance <= 30:
        new_lat, new_lon = calculate_flee_vector(player.lat, player.lon, nearest_ghost["lat"], nearest_ghost["lon"])
        # TODO: Tell DB partner to update the database with these new coordinates
        return {
            "status": "spooked",
            "message": "Your EMF meter spooked it! The ghost fled.",
            "new_lat": new_lat,
            "new_lon": new_lon,
            "distance_meters": round(distance)
        }
        
    # LOGIC 3: Player is too far away
    else:
        return {
            "status": "clear",
            "message": "EMF meter is quiet. Keep searching.",
            "distance_meters": round(distance)
        }