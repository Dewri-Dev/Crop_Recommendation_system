def get_market_forecast(crop_key, crop_data):
    """
    Calculates estimated revenue and profit for a crop.
    """
    d = crop_data["market_data"].get(crop_key.lower(), {"price_per_q": 2000, "yield_q_ha": 20, "input_cost": 20000})
    revenue = d["price_per_q"] * d["yield_q_ha"]
    net = revenue - d["input_cost"]
    
    return {
        "price_per_q": d["price_per_q"],
        "yield_q_ha": d["yield_q_ha"],
        "input_cost": d["input_cost"],
        "revenue": revenue,
        "net_profit": net,
        "roi_pct": round((net / d["input_cost"]) * 100, 1) if d["input_cost"] > 0 else 0
    }
