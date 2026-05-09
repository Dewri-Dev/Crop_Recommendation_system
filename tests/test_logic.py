import pytest
import json
from logic.fertilizer import calculate_fertilizer_prescription
from logic.market import get_market_forecast

# Mock crop data for testing
MOCK_CROP_DATA = {
    "crop_keys": ["rice", "wheat"],
    "npk_requirements": {
        "rice": {"N": 80, "P": 40, "K": 40},
        "wheat": {"N": 120, "P": 60, "K": 40}
    },
    "market_data": {
        "rice": {"price_per_q": 2000, "yield_q_ha": 25, "input_cost": 20000},
        "wheat": {"price_per_q": 2500, "yield_q_ha": 30, "input_cost": 25000}
    }
}

def test_fertilizer_optimal():
    # Scenario: Soil already has exactly what rice needs
    result = calculate_fertilizer_prescription("rice", 80, 40, 40, MOCK_CROP_DATA)
    assert result["all_optimal"] is True
    assert result["urea_kg"] == 0
    assert result["dap_kg"] == 0
    assert result["mop_kg"] == 0

def test_fertilizer_deficit():
    # Scenario: Soil is completely depleted
    result = calculate_fertilizer_prescription("rice", 0, 0, 0, MOCK_CROP_DATA)
    assert result["all_optimal"] is False
    # P need is 40. DAP is 46% P. 40 / 0.46 = 86.95 -> 87
    assert result["dap_kg"] == 87
    # K need is 40. MOP is 60% K. 40 / 0.6 = 66.66 -> 67
    assert result["mop_kg"] == 67

def test_market_forecast():
    # Rice: 2000 * 25 = 50,000 revenue. 50,000 - 20,000 = 30,000 profit.
    result = get_market_forecast("rice", MOCK_CROP_DATA)
    assert result["revenue"] == 50000
    assert result["net_profit"] == 30000
    assert result["roi_pct"] == 150.0

def test_market_forecast_missing_crop():
    # Should fallback to defaults if crop not in data
    result = get_market_forecast("unknown_crop", MOCK_CROP_DATA)
    assert result["revenue"] == 40000  # 2000 * 20 default
    assert result["net_profit"] == 20000 # 40000 - 20000 default
