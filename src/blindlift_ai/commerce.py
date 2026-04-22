from __future__ import annotations

from datetime import UTC, datetime
import sqlite3


class CommerceService:
    def __init__(self, connection: sqlite3.Connection) -> None:
        self.connection = connection

    def add_product(self, name: str, price: float, quantity: int) -> sqlite3.Row:
        cursor = self.connection.cursor()
        cursor.execute(
            """
            INSERT INTO products (name, price, quantity, created_at)
            VALUES (?, ?, ?, ?)
            """,
            (name.strip(), price, quantity, datetime.now(UTC).isoformat()),
        )
        self.connection.commit()
        return self.get_product(cursor.lastrowid)

    def get_product(self, product_id: int) -> sqlite3.Row:
        row = self.connection.execute(
            "SELECT id, name, price, quantity FROM products WHERE id = ?",
            (product_id,),
        ).fetchone()
        if row is None:
            raise ValueError(f"Product {product_id} was not found.")
        return row

    def list_products(self) -> list[sqlite3.Row]:
        rows = self.connection.execute(
            "SELECT id, name, price, quantity FROM products ORDER BY name ASC"
        ).fetchall()
        return list(rows)

    def record_sale(self, product_id: int, quantity: int) -> sqlite3.Row:
        product = self.get_product(product_id)
        if quantity > product["quantity"]:
            raise ValueError("Sale quantity exceeds available stock.")

        total = quantity * float(product["price"])
        cursor = self.connection.cursor()
        cursor.execute(
            """
            INSERT INTO sales (product_id, quantity, total, created_at)
            VALUES (?, ?, ?, ?)
            """,
            (product_id, quantity, total, datetime.now(UTC).isoformat()),
        )
        cursor.execute(
            "UPDATE products SET quantity = quantity - ? WHERE id = ?",
            (quantity, product_id),
        )
        self.connection.commit()
        return self.connection.execute(
            "SELECT id, product_id, quantity, total FROM sales WHERE id = ?",
            (cursor.lastrowid,),
        ).fetchone()

    def summary(self) -> dict[str, float | int]:
        row = self.connection.execute(
            """
            SELECT
                COUNT(*) AS products_in_catalog,
                COALESCE(SUM(quantity), 0) AS units_in_stock
            FROM products
            """
        ).fetchone()
        revenue_row = self.connection.execute(
            "SELECT COALESCE(SUM(total), 0) AS revenue FROM sales"
        ).fetchone()
        return {
            "products_in_catalog": int(row["products_in_catalog"]),
            "units_in_stock": int(row["units_in_stock"]),
            "revenue": float(revenue_row["revenue"]),
        }

