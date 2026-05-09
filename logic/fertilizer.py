import streamlit as st

def calculate_fertilizer_prescription(crop_key, actual_N, actual_P, actual_K, crop_data):
    """
    Calculates fertilizer requirements based on crop needs and soil deficit.
    """
    req       = crop_data["npk_requirements"].get(crop_key.lower(), {"N": 80, "P": 40, "K": 40})
    deficit_N = max(0, req["N"] - actual_N)
    deficit_P = max(0, req["P"] - actual_P)
    deficit_K = max(0, req["K"] - actual_K)
    
    # Simple conversion logic:
    # DAP provides P (46%) and N (18%)
    # Urea provides N (46%)
    # MOP provides K (60%)
    
    dap_kg    = deficit_P / 0.46
    urea_kg   = max(0, deficit_N - dap_kg * 0.18) / 0.46
    mop_kg    = deficit_K / 0.60
    
    return {
        "required": req,
        "deficit_N": round(deficit_N),
        "deficit_P": round(deficit_P),
        "deficit_K": round(deficit_K),
        "urea_kg": round(urea_kg),
        "dap_kg": round(dap_kg),
        "mop_kg": round(mop_kg),
        "all_optimal": deficit_N == 0 and deficit_P == 0 and deficit_K == 0
    }
