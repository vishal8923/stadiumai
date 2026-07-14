from fastapi import APIRouter, Depends
from typing import Optional
from app.models.schemas import WasteRequest, WasteResponse
from app.dependencies import general_rate_limit

router = APIRouter(prefix="/api/v1", tags=["sustainability"])

@router.post("/sustainability/waste", response_model=WasteResponse, dependencies=[general_rate_limit])
def classify_waste_item(request: WasteRequest, location: Optional[str] = None):
    """
    Classify a waste item (compost, recycle, landfill) and find nearest disposal bins.
    Intentionally rule-based, non-AI logic that works normally when Gemini is disabled.
    """
    desc = request.item_description.lower().strip()
    
    # Predefined keyword matching logic
    if any(k in desc for k in ["plastic", "bottle", "can", "soda", "cup", "beer", "aluminum", "container"]):
        item_type = "Recyclable (Plastic/Metal)"
        bin_type = "Recycling Bin (Blue)"
        bin_location = "Next to washrooms in Concourse 1 or Concourse 3"
        environmental_impact = "Saves energy and redirects plastics away from landfills. Promotes a circular economy."
        disposal_tip = "Empty any liquid from the cup or bottle before placing it in the recycling bin."
    elif any(k in desc for k in ["banana", "apple", "food", "hotdog", "shawarma", "peel", "core", "bread", "wrap", "organic", "nacho"]):
        item_type = "Organic Waste"
        bin_type = "Compost Bin (Green)"
        bin_location = "Adjacent to all main food court vendors on Level 1"
        environmental_impact = "Converts organic food waste into rich nutrient compost, lowering methane emissions."
        disposal_tip = "Remove plastic cutlery or foil wrappers before disposing of food scraps."
    else:
        item_type = "General Waste"
        bin_type = "Landfill Bin (Black)"
        bin_location = "Concourse corridors near Seating Section entrances"
        environmental_impact = "Contributes to landfill waste. Consider choosing reusable containers next time."
        disposal_tip = "Ensure no liquids or recyclable plastics are mixed into this bin."

    # If the user provided a location, customize bin location description
    loc = request.location or location
    if loc:
        bin_location = f"Nearest {bin_type} is located near {loc} on the main concourse corridor."

    return WasteResponse(
        item_type=item_type,
        bin_type=bin_type,
        bin_location=bin_location,
        environmental_impact=environmental_impact,
        disposal_tip=disposal_tip
    )
