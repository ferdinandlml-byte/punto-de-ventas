from __future__ import annotations

from datetime import datetime
import hashlib
import shutil
from pathlib import Path
import sqlite3
from typing import Iterable, Dict, Any, Tuple, List

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "pos.db"


def _connect() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db() -> None:
    with _connect() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                barcode TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                price REAL NOT NULL,
                stock REAL NOT NULL DEFAULT 0
            );

            CREATE TABLE IF NOT EXISTS sales (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT NOT NULL,
                subtotal REAL NOT NULL DEFAULT 0,
                discount REAL NOT NULL DEFAULT 0,
                tax_rate REAL NOT NULL DEFAULT 0,
                tax_amount REAL NOT NULL DEFAULT 0,
                total REAL NOT NULL
            );

            CREATE TABLE IF NOT EXISTS sale_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sale_id INTEGER NOT NULL,
                product_id INTEGER NOT NULL,
                quantity REAL NOT NULL,
                price REAL NOT NULL,
                line_total REAL NOT NULL,
                FOREIGN KEY (sale_id) REFERENCES sales(id) ON DELETE CASCADE,
                FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE RESTRICT
            );

            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                display_name TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'Administrador',
                is_active INTEGER NOT NULL DEFAULT 1
            );

            CREATE TABLE IF NOT EXISTS customers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                phone TEXT,
                email TEXT,
                address TEXT
            );

            CREATE TABLE IF NOT EXISTS suppliers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                phone TEXT,
                email TEXT,
                address TEXT
            );

            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT NOT NULL,
                concept TEXT NOT NULL,
                amount REAL NOT NULL
            );

            CREATE TABLE IF NOT EXISTS purchases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT NOT NULL,
                supplier_id INTEGER,
                total REAL NOT NULL,
                FOREIGN KEY (supplier_id) REFERENCES suppliers(id) ON DELETE SET NULL
            );

            CREATE TABLE IF NOT EXISTS purchase_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                purchase_id INTEGER NOT NULL,
                product_id INTEGER NOT NULL,
                quantity REAL NOT NULL,
                cost REAL NOT NULL,
                line_total REAL NOT NULL,
                FOREIGN KEY (purchase_id) REFERENCES purchases(id) ON DELETE CASCADE,
                FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE RESTRICT
            );

            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL
            );

            CREATE TABLE IF NOT EXISTS branches (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                address TEXT
            );
            """
        )
        _ensure_column(conn, "sales", "subtotal", "REAL NOT NULL DEFAULT 0")
        _ensure_column(conn, "sales", "discount", "REAL NOT NULL DEFAULT 0")
        _ensure_column(conn, "sales", "tax_rate", "REAL NOT NULL DEFAULT 0")
        _ensure_column(conn, "sales", "tax_amount", "REAL NOT NULL DEFAULT 0")
        _ensure_column(conn, "users", "role", "TEXT NOT NULL DEFAULT 'Administrador'")
        conn.commit()


def _ensure_column(conn: sqlite3.Connection, table: str, column: str, ddl: str) -> None:
    existing = {
        row["name"] for row in conn.execute(f"PRAGMA table_info({table})").fetchall()
    }
    if column not in existing:
        conn.execute(f"ALTER TABLE {table} ADD COLUMN {column} {ddl}")


def _hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def ensure_default_user() -> None:
    with _connect() as conn:
        count = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        if count > 0:
            return

        conn.execute(
            """
            INSERT INTO users (username, password_hash, display_name, role)
            VALUES (?, ?, ?, ?)
            """,
            ("admin", _hash_password("1234"), "Administrador", "Administrador"),
        )
        conn.commit()


def seed_sample_data() -> None:
    with _connect() as conn:
        count = conn.execute("SELECT COUNT(*) FROM products").fetchone()[0]
        if count > 0:
            return

        products = [
            ("7501055354651", "Coca Cola 600ml", 18.0, 50),
            ("7501000111409", "Sabritas Clásicas 45g", 17.0, 40),
            ("7501000632256", "Bimbo Pan Blanco", 45.0, 20),
            ("7501000610124", "Leche Lala 1L", 28.0, 30),
            ("7501001335606", "Atún Herdez 140g", 24.0, 25),
        ]
        conn.executemany(
            "INSERT INTO products (barcode, name, price, stock) VALUES (?, ?, ?, ?)",
            products,
        )
        conn.commit()


def verify_user(username: str, password: str) -> bool:
    with _connect() as conn:
        row = conn.execute(
            "SELECT password_hash, is_active FROM users WHERE username = ?",
            (username,),
        ).fetchone()
        if row is None or row["is_active"] != 1:
            return False
        return row["password_hash"] == _hash_password(password)


def get_product_by_barcode(barcode: str) -> sqlite3.Row | None:
    with _connect() as conn:
        return conn.execute(
            "SELECT id, barcode, name, price, stock FROM products WHERE barcode = ?",
            (barcode,),
        ).fetchone()


def add_product(barcode: str, name: str, price: float, stock: float) -> bool:
    try:
        with _connect() as conn:
            conn.execute(
                "INSERT INTO products (barcode, name, price, stock) VALUES (?, ?, ?, ?)",
                (barcode, name, price, stock),
            )
            conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False


def list_products(search: str = "") -> List[sqlite3.Row]:
    query = ""
    params: Tuple[Any, ...] = ()
    if search:
        query = "WHERE barcode LIKE ? OR name LIKE ?"
        like = f"%{search}%"
        params = (like, like)

    with _connect() as conn:
        return conn.execute(
            f"""
            SELECT id, barcode, name, price, stock
            FROM products
            {query}
            ORDER BY name ASC
            """,
            params,
        ).fetchall()


def get_product_by_id(product_id: int) -> sqlite3.Row | None:
    with _connect() as conn:
        return conn.execute(
            "SELECT id, barcode, name, price, stock FROM products WHERE id = ?",
            (product_id,),
        ).fetchone()


def update_product(
    product_id: int, barcode: str, name: str, price: float, stock: float
) -> bool:
    try:
        with _connect() as conn:
            conn.execute(
                """
                UPDATE products
                SET barcode = ?, name = ?, price = ?, stock = ?
                WHERE id = ?
                """,
                (barcode, name, price, stock, product_id),
            )
            conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False


def delete_product(product_id: int) -> None:
    with _connect() as conn:
        conn.execute("DELETE FROM products WHERE id = ?", (product_id,))
        conn.commit()


def record_sale(
    items: Iterable[Dict[str, Any]],
    discount: float = 0.0,
    tax_rate: float = 0.0,
) -> Tuple[int, float]:
    items_list = list(items)
    if not items_list:
        raise ValueError("No hay artículos en la venta")

    subtotal = sum(item["line_total"] for item in items_list)
    discount = max(0.0, float(discount))
    taxable = max(0.0, subtotal - discount)
    tax_amount = taxable * float(tax_rate)
    total = taxable + tax_amount
    created_at = datetime.now().isoformat(sep=" ", timespec="seconds")

    with _connect() as conn:
        cur = conn.execute(
            """
            INSERT INTO sales (created_at, subtotal, discount, tax_rate, tax_amount, total)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (created_at, subtotal, discount, tax_rate, tax_amount, total),
        )
        sale_id = cur.lastrowid

        conn.executemany(
            """
            INSERT INTO sale_items (sale_id, product_id, quantity, price, line_total)
            VALUES (?, ?, ?, ?, ?)
            """,
            [
                (
                    sale_id,
                    item["product_id"],
                    item["quantity"],
                    item["price"],
                    item["line_total"],
                )
                for item in items_list
            ],
        )

        for item in items_list:
            conn.execute(
                "UPDATE products SET stock = stock - ? WHERE id = ?",
                (item["quantity"], item["product_id"]),
            )

        conn.commit()

    return sale_id, total


def get_setting(key: str, default: str = "") -> str:
    with _connect() as conn:
        row = conn.execute("SELECT value FROM settings WHERE key = ?", (key,)).fetchone()
        if row is None:
            return default
        return row["value"]


def set_setting(key: str, value: str) -> None:
    with _connect() as conn:
        conn.execute(
            "INSERT INTO settings (key, value) VALUES (?, ?) ON CONFLICT(key) DO UPDATE SET value = excluded.value",
            (key, value),
        )
        conn.commit()


def list_categories() -> List[sqlite3.Row]:
    with _connect() as conn:
        return conn.execute(
            "SELECT id, name FROM categories ORDER BY name"
        ).fetchall()


def add_category(name: str) -> bool:
    try:
        with _connect() as conn:
            conn.execute("INSERT INTO categories (name) VALUES (?)", (name,))
            conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False


def delete_category(category_id: int) -> None:
    with _connect() as conn:
        conn.execute("DELETE FROM categories WHERE id = ?", (category_id,))
        conn.commit()


def list_branches() -> List[sqlite3.Row]:
    with _connect() as conn:
        return conn.execute(
            "SELECT id, name, address FROM branches ORDER BY name"
        ).fetchall()


def add_branch(name: str, address: str) -> bool:
    try:
        with _connect() as conn:
            conn.execute(
                "INSERT INTO branches (name, address) VALUES (?, ?)",
                (name, address),
            )
            conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False


def delete_branch(branch_id: int) -> None:
    with _connect() as conn:
        conn.execute("DELETE FROM branches WHERE id = ?", (branch_id,))
        conn.commit()


def list_customers() -> List[sqlite3.Row]:
    with _connect() as conn:
        return conn.execute(
            "SELECT id, name, phone, email, address FROM customers ORDER BY name"
        ).fetchall()


def add_customer(name: str, phone: str, email: str, address: str) -> None:
    with _connect() as conn:
        conn.execute(
            "INSERT INTO customers (name, phone, email, address) VALUES (?, ?, ?, ?)",
            (name, phone, email, address),
        )
        conn.commit()


def update_customer(
    customer_id: int, name: str, phone: str, email: str, address: str
) -> None:
    with _connect() as conn:
        conn.execute(
            """
            UPDATE customers SET name = ?, phone = ?, email = ?, address = ?
            WHERE id = ?
            """,
            (name, phone, email, address, customer_id),
        )
        conn.commit()


def delete_customer(customer_id: int) -> None:
    with _connect() as conn:
        conn.execute("DELETE FROM customers WHERE id = ?", (customer_id,))
        conn.commit()


def list_suppliers() -> List[sqlite3.Row]:
    with _connect() as conn:
        return conn.execute(
            "SELECT id, name, phone, email, address FROM suppliers ORDER BY name"
        ).fetchall()


def add_supplier(name: str, phone: str, email: str, address: str) -> None:
    with _connect() as conn:
        conn.execute(
            "INSERT INTO suppliers (name, phone, email, address) VALUES (?, ?, ?, ?)",
            (name, phone, email, address),
        )
        conn.commit()


def update_supplier(
    supplier_id: int, name: str, phone: str, email: str, address: str
) -> None:
    with _connect() as conn:
        conn.execute(
            """
            UPDATE suppliers SET name = ?, phone = ?, email = ?, address = ?
            WHERE id = ?
            """,
            (name, phone, email, address, supplier_id),
        )
        conn.commit()


def delete_supplier(supplier_id: int) -> None:
    with _connect() as conn:
        conn.execute("DELETE FROM suppliers WHERE id = ?", (supplier_id,))
        conn.commit()


def list_expenses() -> List[sqlite3.Row]:
    with _connect() as conn:
        return conn.execute(
            "SELECT id, created_at, concept, amount FROM expenses ORDER BY created_at DESC"
        ).fetchall()


def add_expense(concept: str, amount: float) -> None:
    created_at = datetime.now().isoformat(sep=" ", timespec="seconds")
    with _connect() as conn:
        conn.execute(
            "INSERT INTO expenses (created_at, concept, amount) VALUES (?, ?, ?)",
            (created_at, concept, amount),
        )
        conn.commit()


def delete_expense(expense_id: int) -> None:
    with _connect() as conn:
        conn.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
        conn.commit()


def list_users() -> List[sqlite3.Row]:
    with _connect() as conn:
        return conn.execute(
            "SELECT id, username, display_name, role, is_active FROM users ORDER BY username"
        ).fetchall()


def add_user(username: str, password: str, display_name: str, role: str) -> bool:
    try:
        with _connect() as conn:
            conn.execute(
                """
                INSERT INTO users (username, password_hash, display_name, role)
                VALUES (?, ?, ?, ?)
                """,
                (username, _hash_password(password), display_name, role),
            )
            conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False


def update_user(
    user_id: int, username: str, password: str | None, display_name: str, role: str, is_active: bool
) -> bool:
    try:
        with _connect() as conn:
            if password:
                conn.execute(
                    """
                    UPDATE users
                    SET username = ?, password_hash = ?, display_name = ?, role = ?, is_active = ?
                    WHERE id = ?
                    """,
                    (username, _hash_password(password), display_name, role, int(is_active), user_id),
                )
            else:
                conn.execute(
                    """
                    UPDATE users
                    SET username = ?, display_name = ?, role = ?, is_active = ?
                    WHERE id = ?
                    """,
                    (username, display_name, role, int(is_active), user_id),
                )
            conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False


def delete_user(user_id: int) -> None:
    with _connect() as conn:
        conn.execute("DELETE FROM users WHERE id = ?", (user_id,))
        conn.commit()


def record_purchase(
    items: Iterable[Dict[str, Any]],
    supplier_id: int | None,
) -> Tuple[int, float]:
    items_list = list(items)
    if not items_list:
        raise ValueError("No hay artículos en la compra")

    total = sum(item["line_total"] for item in items_list)
    created_at = datetime.now().isoformat(sep=" ", timespec="seconds")

    with _connect() as conn:
        cur = conn.execute(
            "INSERT INTO purchases (created_at, supplier_id, total) VALUES (?, ?, ?)",
            (created_at, supplier_id, total),
        )
        purchase_id = cur.lastrowid

        conn.executemany(
            """
            INSERT INTO purchase_items (purchase_id, product_id, quantity, cost, line_total)
            VALUES (?, ?, ?, ?, ?)
            """,
            [
                (
                    purchase_id,
                    item["product_id"],
                    item["quantity"],
                    item["cost"],
                    item["line_total"],
                )
                for item in items_list
            ],
        )

        for item in items_list:
            conn.execute(
                "UPDATE products SET stock = stock + ? WHERE id = ?",
                (item["quantity"], item["product_id"]),
            )

        conn.commit()

    return purchase_id, total


def backup_database(backup_path: Path) -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(DB_PATH, backup_path)


def restore_database(backup_path: Path) -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(backup_path, DB_PATH)


def clear_transactions() -> None:
    with _connect() as conn:
        conn.executescript(
            """
            DELETE FROM sale_items;
            DELETE FROM sales;
            DELETE FROM purchase_items;
            DELETE FROM purchases;
            DELETE FROM expenses;
            """
        )
        conn.commit()


def get_daily_sales_summary(target_date: str) -> List[sqlite3.Row]:
    with _connect() as conn:
        return conn.execute(
            """
            SELECT
                p.barcode AS barcode,
                p.name AS name,
                SUM(si.quantity) AS quantity,
                SUM(si.line_total) AS total
            FROM sale_items si
            JOIN sales s ON s.id = si.sale_id
            JOIN products p ON p.id = si.product_id
            WHERE DATE(s.created_at) = DATE(?)
            GROUP BY p.id, p.barcode, p.name
            ORDER BY SUM(si.quantity) DESC
            """,
            (target_date,),
        ).fetchall()


def get_top_products(limit: int = 20) -> List[sqlite3.Row]:
    with _connect() as conn:
        return conn.execute(
            """
            SELECT
                p.barcode AS barcode,
                p.name AS name,
                SUM(si.quantity) AS quantity,
                SUM(si.line_total) AS total
            FROM sale_items si
            JOIN products p ON p.id = si.product_id
            GROUP BY p.id, p.barcode, p.name
            ORDER BY SUM(si.quantity) DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()


def list_sales_for_date(target_date: str) -> List[sqlite3.Row]:
    with _connect() as conn:
        return conn.execute(
            """
            SELECT id, created_at, subtotal, discount, tax_rate, tax_amount, total
            FROM sales
            WHERE DATE(created_at) = DATE(?)
            ORDER BY created_at
            """,
            (target_date,),
        ).fetchall()
