import json
import os
import uuid
from datetime import date
from pathlib import Path
from typing import Optional
from fastmcp import FastMCP
from pydantic import Field

# ---------------------------------------------------------------------------
# Data
# ---------------------------------------------------------------------------

_DATA_PATH = Path(__file__).parent / "data" / "sage.json"
_db: dict = json.loads(_DATA_PATH.read_text())


def _match(record: dict, field: str, value: str) -> bool:
    """Case-insensitive substring match on a field."""
    return value.lower() in str(record.get(field, "")).lower()


# ---------------------------------------------------------------------------
# Server
# ---------------------------------------------------------------------------

mcp = FastMCP(
    name="sage-mock",
    version="1.0.0",
    instructions=(
        "Mock Sage ERP for RD Abbott specialty chemical and rubber ingredient distribution. "
        "Query and manage customers, products, inventory, sales orders, invoices, purchase orders, "
        "vendors, item receipts, price lists, and financial transactions."
    ),
)

# ---------------------------------------------------------------------------
# Customers
# ---------------------------------------------------------------------------

@mcp.tool()
def get_customers(
    id: Optional[str] = Field(default=None, description="Filter by customer ID, e.g. C-001"),
    name: Optional[str] = Field(default=None, description="Filter by customer name (partial match)"),
    customer_type: Optional[str] = Field(default=None, description="Filter by customer type: manufacturer | distributor | processor"),
    status: Optional[str] = Field(default=None, description="Filter by status: active | inactive"),
    account_manager: Optional[str] = Field(default=None, description="Filter by account manager name (partial match)"),
    currency: Optional[str] = Field(default=None, description="Filter by billing currency: USD | CAD"),
) -> list[dict]:
    """List customers. Optionally filter by ID, name, type, status, account manager, or currency."""
    results = _db["customers"]
    if id:
        results = [r for r in results if r["id"].upper() == id.upper()]
    if name:
        results = [r for r in results if _match(r, "name", name)]
    if customer_type:
        results = [r for r in results if _match(r, "customer_type", customer_type)]
    if status:
        results = [r for r in results if _match(r, "status", status)]
    if account_manager:
        results = [r for r in results if _match(r, "account_manager", account_manager)]
    if currency:
        results = [r for r in results if _match(r, "currency", currency)]
    return results


# ---------------------------------------------------------------------------
# Products
# ---------------------------------------------------------------------------

@mcp.tool()
def get_products(
    id: Optional[str] = Field(default=None, description="Filter by product ID, e.g. P-001"),
    sku: Optional[str] = Field(default=None, description="Filter by SKU (partial match)"),
    name: Optional[str] = Field(default=None, description="Filter by product name (partial match)"),
    category: Optional[str] = Field(default=None, description="Filter by category: accelerator | antioxidant | plasticizer | processing_aid | polymer | specialty_compound | filler"),
    status: Optional[str] = Field(default=None, description="Filter by status: active | discontinued"),
    hazmat: Optional[bool] = Field(default=None, description="Filter by hazmat flag: true returns only hazmat products, false returns non-hazmat"),
) -> list[dict]:
    """List products/SKUs. Optionally filter by ID, SKU, name, category, status, or hazmat flag."""
    results = _db["products"]
    if id:
        results = [r for r in results if r["id"].upper() == id.upper()]
    if sku:
        results = [r for r in results if _match(r, "sku", sku)]
    if name:
        results = [r for r in results if _match(r, "name", name)]
    if category:
        results = [r for r in results if _match(r, "category", category)]
    if status:
        results = [r for r in results if _match(r, "status", status)]
    if hazmat is not None:
        results = [r for r in results if r.get("hazmat") == hazmat]
    return results


# ---------------------------------------------------------------------------
# Inventory
# ---------------------------------------------------------------------------

@mcp.tool()
def get_inventory(
    product_id: Optional[str] = Field(default=None, description="Filter by product ID, e.g. P-001"),
    product_name: Optional[str] = Field(default=None, description="Filter by product name (partial match)"),
    location_id: Optional[str] = Field(default=None, description="Filter by warehouse location ID: WH-CHI | WH-HOU"),
    location_name: Optional[str] = Field(default=None, description="Filter by warehouse location name (partial match)"),
    low_stock: bool = Field(default=False, description="If true, return only items where quantity_available <= reorder_point"),
) -> list[dict]:
    """List inventory records by product and warehouse location. Filter by product, location, or low-stock status."""
    results = _db["inventory"]
    if product_id:
        results = [r for r in results if r["product_id"].upper() == product_id.upper()]
    if product_name:
        results = [r for r in results if _match(r, "product_name", product_name)]
    if location_id:
        results = [r for r in results if r["location_id"].upper() == location_id.upper()]
    if location_name:
        results = [r for r in results if _match(r, "location_name", location_name)]
    if low_stock:
        results = [r for r in results if r["quantity_available"] <= r["reorder_point"]]
    return results


# ---------------------------------------------------------------------------
# Sales Orders
# ---------------------------------------------------------------------------

@mcp.tool()
def get_sales_orders(
    id: Optional[str] = Field(default=None, description="Filter by order ID, e.g. SO-1001"),
    order_number: Optional[str] = Field(default=None, description="Filter by order number (partial match)"),
    customer_id: Optional[str] = Field(default=None, description="Filter by customer ID, e.g. C-001"),
    customer_name: Optional[str] = Field(default=None, description="Filter by customer name (partial match)"),
    status: Optional[str] = Field(default=None, description="Filter by status: pending | confirmed | picking | shipped | delivered | cancelled"),
    account_manager: Optional[str] = Field(default=None, description="Filter by account manager name (partial match)"),
    start_date: Optional[str] = Field(default=None, description="Filter orders on or after this order_date (YYYY-MM-DD)"),
    end_date: Optional[str] = Field(default=None, description="Filter orders on or before this order_date (YYYY-MM-DD)"),
) -> list[dict]:
    """List sales orders. Optionally filter by ID, customer, status, account manager, or date range."""
    results = _db["sales_orders"]
    if id:
        results = [r for r in results if r["id"].upper() == id.upper()]
    if order_number:
        results = [r for r in results if _match(r, "order_number", order_number)]
    if customer_id:
        results = [r for r in results if r["customer_id"].upper() == customer_id.upper()]
    if customer_name:
        results = [r for r in results if _match(r, "customer_name", customer_name)]
    if status:
        results = [r for r in results if _match(r, "status", status)]
    if account_manager:
        results = [r for r in results if _match(r, "account_manager", account_manager)]
    if start_date:
        results = [r for r in results if r.get("order_date") and r["order_date"] >= start_date]
    if end_date:
        results = [r for r in results if r.get("order_date") and r["order_date"] <= end_date]
    return results


# ---------------------------------------------------------------------------
# Invoices
# ---------------------------------------------------------------------------

@mcp.tool()
def get_invoices(
    id: Optional[str] = Field(default=None, description="Filter by invoice ID, e.g. INV-2001"),
    invoice_number: Optional[str] = Field(default=None, description="Filter by invoice number (partial match)"),
    customer_id: Optional[str] = Field(default=None, description="Filter by customer ID, e.g. C-001"),
    customer_name: Optional[str] = Field(default=None, description="Filter by customer name (partial match)"),
    status: Optional[str] = Field(default=None, description="Filter by status: open | partially_paid | paid | overdue"),
    start_date: Optional[str] = Field(default=None, description="Filter invoices on or after this invoice_date (YYYY-MM-DD)"),
    end_date: Optional[str] = Field(default=None, description="Filter invoices on or before this invoice_date (YYYY-MM-DD)"),
) -> list[dict]:
    """List invoices. Optionally filter by ID, customer, status, or invoice date range."""
    results = _db["invoices"]
    if id:
        results = [r for r in results if r["id"].upper() == id.upper()]
    if invoice_number:
        results = [r for r in results if _match(r, "invoice_number", invoice_number)]
    if customer_id:
        results = [r for r in results if r["customer_id"].upper() == customer_id.upper()]
    if customer_name:
        results = [r for r in results if _match(r, "customer_name", customer_name)]
    if status:
        results = [r for r in results if _match(r, "status", status)]
    if start_date:
        results = [r for r in results if r.get("invoice_date") and r["invoice_date"] >= start_date]
    if end_date:
        results = [r for r in results if r.get("invoice_date") and r["invoice_date"] <= end_date]
    return results


# ---------------------------------------------------------------------------
# Purchase Orders
# ---------------------------------------------------------------------------

@mcp.tool()
def get_purchase_orders(
    id: Optional[str] = Field(default=None, description="Filter by PO ID, e.g. PO-3001"),
    po_number: Optional[str] = Field(default=None, description="Filter by PO number (partial match)"),
    vendor_id: Optional[str] = Field(default=None, description="Filter by vendor ID, e.g. V-001"),
    vendor_name: Optional[str] = Field(default=None, description="Filter by vendor name (partial match)"),
    status: Optional[str] = Field(default=None, description="Filter by status: open | partially_received | received | closed"),
) -> list[dict]:
    """List purchase orders. Optionally filter by ID, vendor, or status."""
    results = _db["purchase_orders"]
    if id:
        results = [r for r in results if r["id"].upper() == id.upper()]
    if po_number:
        results = [r for r in results if _match(r, "po_number", po_number)]
    if vendor_id:
        results = [r for r in results if r["vendor_id"].upper() == vendor_id.upper()]
    if vendor_name:
        results = [r for r in results if _match(r, "vendor_name", vendor_name)]
    if status:
        results = [r for r in results if _match(r, "status", status)]
    return results


# ---------------------------------------------------------------------------
# Vendors
# ---------------------------------------------------------------------------

@mcp.tool()
def get_vendors(
    id: Optional[str] = Field(default=None, description="Filter by vendor ID, e.g. V-001"),
    name: Optional[str] = Field(default=None, description="Filter by vendor name (partial match)"),
    vendor_type: Optional[str] = Field(default=None, description="Filter by vendor type: manufacturer | distributor | logistics"),
    status: Optional[str] = Field(default=None, description="Filter by status: active | inactive"),
    country: Optional[str] = Field(default=None, description="Filter by country (partial match), e.g. Germany | United States"),
) -> list[dict]:
    """List vendors. Optionally filter by ID, name, type, status, or country."""
    results = _db["vendors"]
    if id:
        results = [r for r in results if r["id"].upper() == id.upper()]
    if name:
        results = [r for r in results if _match(r, "name", name)]
    if vendor_type:
        results = [r for r in results if _match(r, "vendor_type", vendor_type)]
    if status:
        results = [r for r in results if _match(r, "status", status)]
    if country:
        results = [r for r in results if _match(r, "country", country)]
    return results


# ---------------------------------------------------------------------------
# Item Receipts
# ---------------------------------------------------------------------------

@mcp.tool()
def get_item_receipts(
    id: Optional[str] = Field(default=None, description="Filter by receipt ID, e.g. REC-4001"),
    purchase_order_id: Optional[str] = Field(default=None, description="Filter by linked purchase order ID, e.g. PO-3002"),
    vendor_name: Optional[str] = Field(default=None, description="Filter by vendor name (partial match)"),
    status: Optional[str] = Field(default=None, description="Filter by status: received | partial | pending_inspection"),
) -> list[dict]:
    """List goods receipts / item receipts. Optionally filter by ID, purchase order, vendor, or status."""
    results = _db["item_receipts"]
    if id:
        results = [r for r in results if r["id"].upper() == id.upper()]
    if purchase_order_id:
        results = [r for r in results if r["purchase_order_id"].upper() == purchase_order_id.upper()]
    if vendor_name:
        results = [r for r in results if _match(r, "vendor_name", vendor_name)]
    if status:
        results = [r for r in results if _match(r, "status", status)]
    return results


# ---------------------------------------------------------------------------
# Price Lists
# ---------------------------------------------------------------------------

@mcp.tool()
def get_price_lists(
    id: Optional[str] = Field(default=None, description="Filter by price list ID, e.g. PL-001"),
    name: Optional[str] = Field(default=None, description="Filter by price list name (partial match)"),
    customer_tier: Optional[str] = Field(default=None, description="Filter by customer tier: standard | preferred | contract"),
) -> list[dict]:
    """List price lists by customer tier. Optionally filter by ID, name, or tier."""
    results = _db["price_lists"]
    if id:
        results = [r for r in results if r["id"].upper() == id.upper()]
    if name:
        results = [r for r in results if _match(r, "name", name)]
    if customer_tier:
        results = [r for r in results if _match(r, "customer_tier", customer_tier)]
    return results


# ---------------------------------------------------------------------------
# Transactions (GL)
# ---------------------------------------------------------------------------

@mcp.tool()
def get_transactions(
    transaction_type: Optional[str] = Field(default=None, description="Filter by type: invoice | payment | credit_memo | journal_entry | debit_memo"),
    account: Optional[str] = Field(default=None, description="Filter by GL account name (partial match)"),
    start_date: Optional[str] = Field(default=None, description="Filter transactions on or after this date (YYYY-MM-DD)"),
    end_date: Optional[str] = Field(default=None, description="Filter transactions on or before this date (YYYY-MM-DD)"),
) -> list[dict]:
    """List GL transactions. Optionally filter by transaction type, account, or date range."""
    results = _db["transactions"]
    if transaction_type:
        results = [r for r in results if _match(r, "transaction_type", transaction_type)]
    if account:
        results = [r for r in results if _match(r, "account", account)]
    if start_date:
        results = [r for r in results if r.get("date") and r["date"] >= start_date]
    if end_date:
        results = [r for r in results if r.get("date") and r["date"] <= end_date]
    return results


# ---------------------------------------------------------------------------
# Search
# ---------------------------------------------------------------------------

@mcp.tool()
def search_records(
    record_type: str = Field(description="Collection to search: customers | products | sales_orders | invoices | purchase_orders | vendors"),
    query: str = Field(description="Partial name/text to search for (case-insensitive)"),
) -> list[dict]:
    """Search across a record collection by partial name match. Useful for quick lookups."""
    collection_map = {
        "customers": ("customers", "name"),
        "products": ("products", "name"),
        "sales_orders": ("sales_orders", "customer_name"),
        "invoices": ("invoices", "customer_name"),
        "purchase_orders": ("purchase_orders", "vendor_name"),
        "vendors": ("vendors", "name"),
    }
    key = record_type.lower()
    if key not in collection_map:
        return [{"error": f"Unknown record_type '{record_type}'. Valid types: {', '.join(collection_map.keys())}"}]
    collection_key, field = collection_map[key]
    results = _db[collection_key]
    return [r for r in results if _match(r, field, query)]


# ---------------------------------------------------------------------------
# Write: Sales Orders
# ---------------------------------------------------------------------------

@mcp.tool()
def create_sales_order(
    customer_id: str = Field(description="Customer ID, e.g. C-001"),
    line_items_json: str = Field(description='JSON array of line items. Each item: {"product_id": "P-001", "quantity": 100, "unit_of_measure": "kg", "unit_price_usd": 8.20}'),
    ship_date: Optional[str] = Field(default=None, description="Planned ship date (YYYY-MM-DD)"),
    shipping_method: Optional[str] = Field(default="ground", description="Shipping method: ground | ltl_freight | air | will_call"),
    po_number: Optional[str] = Field(default=None, description="Customer purchase order number"),
    notes: Optional[str] = Field(default=None, description="Order notes"),
    account_manager: Optional[str] = Field(default=None, description="Account manager name"),
) -> dict:
    """Create a new sales order with pending status. Returns the created order record."""
    # Look up customer
    customers = [c for c in _db["customers"] if c["id"].upper() == customer_id.upper()]
    if not customers:
        return {"error": f"Customer '{customer_id}' not found."}
    customer = customers[0]

    # Parse line items
    try:
        line_items_raw = json.loads(line_items_json)
    except json.JSONDecodeError as exc:
        return {"error": f"Invalid line_items_json: {exc}"}

    # Enrich line items with product names and compute amounts
    enriched_items = []
    subtotal = 0.0
    for item in line_items_raw:
        pid = item.get("product_id", "")
        products = [p for p in _db["products"] if p["id"].upper() == pid.upper()]
        product_name = products[0]["name"] if products else pid
        qty = float(item.get("quantity", 0))
        price = float(item.get("unit_price_usd", 0))
        amount = round(qty * price, 2)
        subtotal += amount
        enriched_items.append({
            "product_id": pid,
            "product_name": product_name,
            "quantity": qty,
            "unit_of_measure": item.get("unit_of_measure", "kg"),
            "unit_price_usd": price,
            "amount_usd": amount,
        })

    subtotal = round(subtotal, 2)
    new_id = f"SO-{1000 + len(_db['sales_orders']) + 1}"
    order = {
        "id": new_id,
        "order_number": new_id,
        "customer_id": customer["id"],
        "customer_name": customer["name"],
        "status": "pending",
        "order_date": str(date.today()),
        "ship_date": ship_date,
        "requested_delivery_date": None,
        "po_number": po_number,
        "line_items": enriched_items,
        "subtotal_usd": subtotal,
        "tax_usd": 0.00,
        "freight_usd": 0.00,
        "total_usd": subtotal,
        "shipping_method": shipping_method or "ground",
        "account_manager": account_manager or "",
        "notes": notes or "",
    }
    _db["sales_orders"].append(order)
    return order


@mcp.tool()
def update_sales_order(
    id: str = Field(description="Sales order ID to update, e.g. SO-1001"),
    status: Optional[str] = Field(default=None, description="New status: pending | confirmed | picking | shipped | delivered | cancelled"),
    ship_date: Optional[str] = Field(default=None, description="Updated ship date (YYYY-MM-DD)"),
    notes: Optional[str] = Field(default=None, description="Updated or appended notes"),
) -> dict:
    """Update an existing sales order's status, ship date, or notes. Returns the updated record."""
    orders = [o for o in _db["sales_orders"] if o["id"].upper() == id.upper()]
    if not orders:
        return {"error": f"Sales order '{id}' not found."}
    order = orders[0]
    if status:
        order["status"] = status
    if ship_date:
        order["ship_date"] = ship_date
    if notes:
        order["notes"] = notes
    return order


# ---------------------------------------------------------------------------
# Write: Invoices
# ---------------------------------------------------------------------------

@mcp.tool()
def create_invoice(
    sales_order_id: str = Field(description="Sales order ID to invoice, e.g. SO-1001"),
    notes: Optional[str] = Field(default=None, description="Invoice notes"),
) -> dict:
    """Create an invoice from an existing sales order. Returns the created invoice record."""
    orders = [o for o in _db["sales_orders"] if o["id"].upper() == sales_order_id.upper()]
    if not orders:
        return {"error": f"Sales order '{sales_order_id}' not found."}
    order = orders[0]

    new_id = f"INV-{2000 + len(_db['invoices']) + 1}"
    today = str(date.today())

    # Compute due date string using payment terms from customer
    customers = [c for c in _db["customers"] if c["id"].upper() == order["customer_id"].upper()]
    payment_terms = customers[0]["payment_terms"] if customers else "Net30"
    terms_days = int("".join(filter(str.isdigit, payment_terms))) if payment_terms else 30
    due_date_obj = date.today()
    from datetime import timedelta
    due_date = str(due_date_obj + timedelta(days=terms_days))

    invoice = {
        "id": new_id,
        "invoice_number": new_id,
        "customer_id": order["customer_id"],
        "customer_name": order["customer_name"],
        "sales_order_id": order["id"],
        "status": "open",
        "invoice_date": today,
        "due_date": due_date,
        "paid_date": None,
        "line_items": order["line_items"],
        "subtotal_usd": order["subtotal_usd"],
        "tax_usd": order["tax_usd"],
        "total_usd": order["total_usd"],
        "amount_paid_usd": 0.00,
        "amount_due_usd": order["total_usd"],
        "payment_terms": payment_terms,
        "notes": notes or "",
    }
    _db["invoices"].append(invoice)
    return invoice


@mcp.tool()
def update_invoice(
    id: str = Field(description="Invoice ID to update, e.g. INV-2001"),
    status: Optional[str] = Field(default=None, description="New status: open | partially_paid | paid | overdue"),
    amount_paid_usd: Optional[float] = Field(default=None, description="Total amount paid to date (USD)"),
    paid_date: Optional[str] = Field(default=None, description="Date payment was received (YYYY-MM-DD)"),
) -> dict:
    """Update an invoice's payment status, amount paid, and paid date. Returns the updated record."""
    invoices = [i for i in _db["invoices"] if i["id"].upper() == id.upper()]
    if not invoices:
        return {"error": f"Invoice '{id}' not found."}
    invoice = invoices[0]
    if status:
        invoice["status"] = status
    if amount_paid_usd is not None:
        invoice["amount_paid_usd"] = round(amount_paid_usd, 2)
        invoice["amount_due_usd"] = round(invoice["total_usd"] - amount_paid_usd, 2)
    if paid_date:
        invoice["paid_date"] = paid_date
    return invoice


# ---------------------------------------------------------------------------
# Write: Purchase Orders
# ---------------------------------------------------------------------------

@mcp.tool()
def create_purchase_order(
    vendor_id: str = Field(description="Vendor ID, e.g. V-001"),
    line_items_json: str = Field(description='JSON array of line items. Each item: {"product_id": "P-001", "quantity": 500, "unit_of_measure": "kg", "unit_cost_usd": 4.85}'),
    expected_date: Optional[str] = Field(default=None, description="Expected delivery date (YYYY-MM-DD)"),
    notes: Optional[str] = Field(default=None, description="PO notes"),
) -> dict:
    """Create a new purchase order for a vendor. Returns the created PO record."""
    vendors = [v for v in _db["vendors"] if v["id"].upper() == vendor_id.upper()]
    if not vendors:
        return {"error": f"Vendor '{vendor_id}' not found."}
    vendor = vendors[0]

    try:
        line_items_raw = json.loads(line_items_json)
    except json.JSONDecodeError as exc:
        return {"error": f"Invalid line_items_json: {exc}"}

    enriched_items = []
    total = 0.0
    for item in line_items_raw:
        pid = item.get("product_id", "")
        products = [p for p in _db["products"] if p["id"].upper() == pid.upper()]
        product_name = products[0]["name"] if products else pid
        qty = float(item.get("quantity", 0))
        cost = float(item.get("unit_cost_usd", 0))
        amount = round(qty * cost, 2)
        total += amount
        enriched_items.append({
            "product_id": pid,
            "product_name": product_name,
            "quantity": qty,
            "unit_of_measure": item.get("unit_of_measure", "kg"),
            "unit_cost_usd": cost,
            "amount_usd": amount,
        })

    total = round(total, 2)
    new_id = f"PO-{3000 + len(_db['purchase_orders']) + 1}"
    po = {
        "id": new_id,
        "po_number": new_id,
        "vendor_id": vendor["id"],
        "vendor_name": vendor["name"],
        "status": "open",
        "order_date": str(date.today()),
        "expected_date": expected_date,
        "line_items": enriched_items,
        "total_usd": total,
        "currency": vendor.get("currency", "USD"),
        "notes": notes or "",
    }
    _db["purchase_orders"].append(po)
    return po


@mcp.tool()
def update_purchase_order(
    id: str = Field(description="Purchase order ID to update, e.g. PO-3001"),
    status: Optional[str] = Field(default=None, description="New status: open | partially_received | received | closed"),
    notes: Optional[str] = Field(default=None, description="Updated or appended notes"),
) -> dict:
    """Update a purchase order's status or notes. Returns the updated record."""
    pos = [p for p in _db["purchase_orders"] if p["id"].upper() == id.upper()]
    if not pos:
        return {"error": f"Purchase order '{id}' not found."}
    po = pos[0]
    if status:
        po["status"] = status
    if notes:
        po["notes"] = notes
    return po


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
