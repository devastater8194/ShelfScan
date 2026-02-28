"""ShelfScan AI - Neighborhood Demand Intelligence"""
from database import db
from datetime import datetime


async def get_neighborhood_data(pincode: str) -> dict:
    """Get aggregated neighborhood demand data for a pincode"""
    try:
        demand = db.client.table("neighborhood_demand") \
            .select("*") \
            .eq("pincode", pincode) \
            .order("week_start", desc=True) \
            .limit(4) \
            .execute()

        stores = db.client.table("stores") \
            .select("store_name, store_type, shelf_health_score, last_scan_at, total_scans") \
            .eq("pincode", pincode) \
            .execute()

        products = db.client.table("detected_products") \
            .select("product_name, category, stock_level") \
            .execute()

        return {
            "pincode": pincode,
            "demand_trends": demand.data or [],
            "stores": stores.data or [],
            "popular_products": _aggregate_products(products.data or [])
        }
    except Exception as e:
        return {"pincode": pincode, "error": str(e)}


def _aggregate_products(products: list) -> list:
    from collections import Counter
    counts = Counter(p.get("product_name") for p in products if p.get("product_name"))
    return [{"product": k, "scan_count": v} for k, v in counts.most_common(10)]
