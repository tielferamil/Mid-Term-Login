from pydantic import BaseModel
from typing import List

# Model for a food item
class FoodItem(BaseModel):
    name: str
    calories: int

# Model for calorie tracking data
class CalorieData(BaseModel):
    target: int = 0
    foods: List[FoodItem] = []
    totalCalories: int = 0