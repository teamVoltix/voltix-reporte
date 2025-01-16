from pydantic import BaseModel
from typing import Dict

class ComparisonData(BaseModel):
    user: str
    billing_period_start: str
    billing_period_end: str
    measurement_start: str
    measurement_end: str
    comparison_results: Dict
    is_comparison_valid: bool
