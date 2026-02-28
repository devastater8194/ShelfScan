"""
ShelfScan AI — Nightly Neighborhood Demand Aggregation
=======================================================
Aggregates detected_products by pincode into the neighborhood_demand table.
Run this as a cron job or Railway scheduled task:

  Schedule: 0 2 * * *  (2 AM IST daily)
  Command:  python -c "import asyncio; from services.aggregation_service import run_aggregation; asyncio.run(run_aggregation())"
"""

import json
from datetime import datetime, timedelta
from collections import Counter, defaultdict
from database import db


async def run_aggregation():
    """Main aggregation job — runs across all pincodes with recent activity."""
    print(f"[{datetime.utcnow().isoformat()}] Starting neighborhood demand aggregation...")

    week_start = (datetime.utcnow() - timedelta(days=datetime.utcnow().weekday())).strftime("%Y-%m-%d")

    try:
        # Get all distinct pincodes with scans in the last 7 days
        recent_scans = (
            db.client.table("scans")
            .select("store_id, created_at")
            .gte("created_at", (datetime.utcnow() - timedelta(days=7)).isoformat())
            .execute()
        )
        store_ids = list(set(s["store_id"] for s in (recent_scans.data or [])))

        if not store_ids:
            print("No recent scans found. Exiting.")
            return

        # Get pincode for each active store
        stores = (
            db.client.table("stores")
            .select("id, pincode, city")
            .in_("id", store_ids)
            .execute()
        )
        pincode_map = {s["id"]: (s["pincode"], s["city"]) for s in (stores.data or [])}

        # Group store_ids by pincode
        by_pincode = defaultdict(list)
        for store_id, (pincode, city) in pincode_map.items():
            by_pincode[(pincode, city)].append(store_id)

        # For each pincode, aggregate products
        for (pincode, city), pin_store_ids in by_pincode.items():
            await _aggregate_pincode(pincode, city, pin_store_ids, week_start)

        print(f"Aggregation complete. Processed {len(by_pincode)} pincodes.")

    except Exception as e:
        print(f"Aggregation error: {e}")


async def _aggregate_pincode(pincode: str, city: str, store_ids: list, week_start: str):
    """Aggregate product data for a single pincode."""
    try:
        # Get all products detected in these stores this week
        products = (
            db.client.table("detected_products")
            .select("product_name, brand, category, stock_level, store_id")
            .in_("store_id", store_ids)
            .gte("detected_at", (datetime.utcnow() - timedelta(days=7)).isoformat())
            .execute()
        )
        all_products = products.data or []

        if not all_products:
            return

        # Compute aggregates
        stockout_items = [p["product_name"] for p in all_products if p["stock_level"] == "critical"]
        low_items = [p["product_name"] for p in all_products if p["stock_level"] == "low"]
        categories = [p["category"] for p in all_products if p.get("category")]

        stockout_counts = Counter(stockout_items).most_common(10)
        category_counts = Counter(categories).most_common(8)

        top_categories = [{"category": k, "count": v} for k, v in category_counts]
        stockout_products = [{"product": k, "times_critical": v} for k, v in stockout_counts]

        demand_signals = {
            "total_products_scanned": len(all_products),
            "unique_products": len(set(p["product_name"] for p in all_products)),
            "stockout_rate": round(len(stockout_items) / len(all_products) * 100, 1),
            "low_stock_rate": round(len(low_items) / len(all_products) * 100, 1),
            "top_stockouts": [p for p, _ in stockout_counts[:5]]
        }

        # Upsert into neighborhood_demand
        existing = (
            db.client.table("neighborhood_demand")
            .select("id")
            .eq("pincode", pincode)
            .eq("week_start", week_start)
            .execute()
        )

        record = {
            "pincode": pincode,
            "city": city,
            "week_start": week_start,
            "total_stores_scanned": len(store_ids),
            "top_categories": json.dumps(top_categories),
            "stockout_products": json.dumps(stockout_products),
            "demand_signals": json.dumps(demand_signals),
            "updated_at": datetime.utcnow().isoformat()
        }

        if existing.data:
            db.client.table("neighborhood_demand").update(record).eq("id", existing.data[0]["id"]).execute()
        else:
            db.client.table("neighborhood_demand").insert({**record, "created_at": datetime.utcnow().isoformat()}).execute()

        print(f"  ✓ Pincode {pincode} ({city}): {len(all_products)} products, {len(stockout_items)} stockouts")

    except Exception as e:
        print(f"  ✗ Pincode {pincode} aggregation failed: {e}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(run_aggregation())
