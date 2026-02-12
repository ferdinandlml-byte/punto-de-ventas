from __future__ import annotations

import sys
from pathlib import Path
from typing import Dict, Any

import pandas as pd
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas

from PySide6 import QtCore, QtGui, QtWidgets

if not __package__:
    project_root = Path(__file__).resolve().parent.parent
    project_root_str = str(project_root)
    if project_root_str not in sys.path:
        sys.path.insert(0, project_root_str)
    __package__ = "app"

try:
    from .db import (
        init_db,
        seed_sample_data,
        get_product_by_barcode,
        add_product,
        record_sale,
        get_daily_sales_summary,
        ensure_default_user,
        verify_user,
        list_products,
        get_product_by_id,
        update_product,
        delete_product,
        list_customers,
        add_customer,
        update_customer,
        delete_customer,
        list_suppliers,
        add_supplier,
        update_supplier,
        delete_supplier,
        list_expenses,
        add_expense,
        delete_expense,
        list_users,
        add_user,
        update_user,
        delete_user,
        get_setting,
        set_setting,
        record_purchase,
        backup_database,
        restore_database,
        get_top_products,
        list_sales_for_date,
        list_categories,
        add_category,
        delete_category,
        list_branches,
        add_branch,
        delete_branch,
        clear_transactions,
    )
except ImportError:
    from app.db import (
        init_db,
        seed_sample_data,
        get_product_by_barcode,
        add_product,
        record_sale,
        get_daily_sales_summary,
        ensure_default_user,
        verify_user,
        list_products,
        get_product_by_id,
        update_product,
        delete_product,
        list_customers,
        add_customer,
        update_customer,
        delete_customer,
        list_suppliers,
        add_supplier,
        update_supplier,
        delete_supplier,
        list_expenses,
        add_expense,
        delete_expense,
        list_users,
        add_user,
        update_user,
        delete_user,
        get_setting,
        set_setting,
        record_purchase,
        backup_database,
        restore_database,
        get_top_products,
        list_sales_for_date,
        list_categories,
        add_category,
        delete_category,
        list_branches,
        add_branch,
        delete_branch,
        clear_transactions,
    )


def get_currency_symbol() -> str:
    return get_setting("currency_symbol", "$")


def format_money(value: float) -> str:
    return f"{get_currency_symbol()} {value:,.2f}"


class LoginDialog(QtWidgets.QDialog):
    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Inicio de sesión")
        self.setFixedSize(500, 320)
        self.setWindowFlag(QtCore.Qt.WindowContextHelpButtonHint, False)

        self.username_input = QtWidgets.QLineEdit()
        self.username_input.setPlaceholderText("Usuario")
        self.password_input = QtWidgets.QLineEdit()
        self.password_input.setPlaceholderText("Contraseña")
        self.password_input.setEchoMode(QtWidgets.QLineEdit.Password)

        self.login_button = QtWidgets.QPushButton("Entrar")
        self.login_button.clicked.connect(self.try_login)

        self.status_label = QtWidgets.QLabel("")
        self.status_label.setStyleSheet("color: #c0392b;")

        card = QtWidgets.QFrame()
        card.setObjectName("card")
        form = QtWidgets.QFormLayout(card)
        form.setLabelAlignment(QtCore.Qt.AlignLeft)
        form.addRow("Usuario", self.username_input)
        form.addRow("Contraseña", self.password_input)

        layout = QtWidgets.QVBoxLayout(self)
        title = QtWidgets.QLabel("Punto de Venta")
        title_font = QtGui.QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(QtCore.Qt.AlignCenter)

        layout.addWidget(title)
        layout.addWidget(card)
        layout.addWidget(self.status_label)
        layout.addWidget(self.login_button)

        self.setStyleSheet(
            """
            QDialog { background-color: #f5f7fb; }
            #card { background: white; border-radius: 12px; padding: 12px; }
            QLineEdit {
                padding: 8px; border: 1px solid #d0d7de; border-radius: 8px;
                background: #ffffff; font-size: 12pt;
            }
            QPushButton {
                padding: 10px; border: none; border-radius: 8px;
                background: #2d6cdf; color: white; font-weight: bold;
            }
            QPushButton:hover { background: #2458b7; }
            QLabel { color: #1f2a44; }
            """
        )

        self.username_input.setFocus()

    def try_login(self) -> None:
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        if not username or not password:
            self.status_label.setText("Ingresa usuario y contraseña")
            return

        if verify_user(username, password):
            self.accept()
        else:
            self.status_label.setText("Credenciales inválidas")


class AddProductDialog(QtWidgets.QDialog):
    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Nuevo producto")
        self.setMinimumWidth(360)

        self.barcode_input = QtWidgets.QLineEdit()
        self.name_input = QtWidgets.QLineEdit()
        self.price_input = QtWidgets.QDoubleSpinBox()
        self.price_input.setMaximum(999999)
        self.price_input.setDecimals(2)
        self.stock_input = QtWidgets.QDoubleSpinBox()
        self.stock_input.setMaximum(999999)
        self.stock_input.setDecimals(2)

        form = QtWidgets.QFormLayout()
        form.addRow("Código de barras", self.barcode_input)
        form.addRow("Nombre", self.name_input)
        form.addRow("Precio", self.price_input)
        form.addRow("Stock", self.stock_input)

        buttons = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout = QtWidgets.QVBoxLayout(self)
        layout.addLayout(form)
        layout.addWidget(buttons)

    def get_values(self) -> Dict[str, Any]:
        return {
            "barcode": self.barcode_input.text().strip(),
            "name": self.name_input.text().strip(),
            "price": float(self.price_input.value()),
            "stock": float(self.stock_input.value()),
        }


class ProductDialog(QtWidgets.QDialog):
    def __init__(self, title: str, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setMinimumWidth(380)

        self.barcode_input = QtWidgets.QLineEdit()
        self.name_input = QtWidgets.QLineEdit()
        self.price_input = QtWidgets.QDoubleSpinBox()
        self.price_input.setMaximum(999999)
        self.price_input.setDecimals(2)
        self.stock_input = QtWidgets.QDoubleSpinBox()
        self.stock_input.setMaximum(999999)
        self.stock_input.setDecimals(2)

        form = QtWidgets.QFormLayout()
        form.addRow("Código de barras", self.barcode_input)
        form.addRow("Nombre", self.name_input)
        form.addRow("Precio", self.price_input)
        form.addRow("Stock", self.stock_input)

        buttons = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout = QtWidgets.QVBoxLayout(self)
        layout.addLayout(form)
        layout.addWidget(buttons)

    def set_values(self, values: Dict[str, Any]) -> None:
        self.barcode_input.setText(values.get("barcode", ""))
        self.name_input.setText(values.get("name", ""))
        self.price_input.setValue(float(values.get("price", 0)))
        self.stock_input.setValue(float(values.get("stock", 0)))

    def get_values(self) -> Dict[str, Any]:
        return {
            "barcode": self.barcode_input.text().strip(),
            "name": self.name_input.text().strip(),
            "price": float(self.price_input.value()),
            "stock": float(self.stock_input.value()),
        }


class DailyReportDialog(QtWidgets.QDialog):
    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Corte del día")
        self.setMinimumSize(700, 480)

        self.date_input = QtWidgets.QDateEdit(QtCore.QDate.currentDate())
        self.date_input.setCalendarPopup(True)
        self.refresh_button = QtWidgets.QPushButton("Actualizar")
        self.refresh_button.clicked.connect(self.load_data)

        self.table = QtWidgets.QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(
            ["Código", "Producto", "Cantidad", "Total"]
        )
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)

        self.total_label = QtWidgets.QLabel(format_money(0))
        total_font = QtGui.QFont()
        total_font.setPointSize(12)
        total_font.setBold(True)
        self.total_label.setFont(total_font)

        top = QtWidgets.QHBoxLayout()
        top.addWidget(QtWidgets.QLabel("Fecha:"))
        top.addWidget(self.date_input)
        top.addWidget(self.refresh_button)
        top.addStretch(1)

        totals_layout = QtWidgets.QHBoxLayout()
        totals_layout.addStretch(1)
        totals_layout.addWidget(QtWidgets.QLabel("Total vendido:"))
        totals_layout.addWidget(self.total_label)

        layout = QtWidgets.QVBoxLayout(self)
        layout.addLayout(top)
        layout.addWidget(self.table, 1)
        layout.addLayout(totals_layout)

        self.load_data()

    def load_data(self) -> None:
        date_str = self.date_input.date().toString("yyyy-MM-dd")
        rows = get_daily_sales_summary(date_str)
        self.table.setRowCount(len(rows))

        total = 0.0
        for row_index, row in enumerate(rows):
            self.table.setItem(row_index, 0, QtWidgets.QTableWidgetItem(row["barcode"]))
            self.table.setItem(row_index, 1, QtWidgets.QTableWidgetItem(row["name"]))
            self.table.setItem(
                row_index, 2, QtWidgets.QTableWidgetItem(f"{row['quantity']:.2f}")
            )
            self.table.setItem(
                row_index, 3, QtWidgets.QTableWidgetItem(format_money(row["total"]))
            )
            total += float(row["total"])

        self.total_label.setText(format_money(total))


class InventoryWidget(QtWidgets.QWidget):
    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)

        self.search_input = QtWidgets.QLineEdit()
        self.search_input.setPlaceholderText("Buscar por código o nombre")
        self.search_input.textChanged.connect(self.refresh_list)

        self.list_widget = QtWidgets.QListWidget()
        self.list_widget.setViewMode(QtWidgets.QListView.IconMode)
        self.list_widget.setResizeMode(QtWidgets.QListView.Adjust)
        self.list_widget.setMovement(QtWidgets.QListView.Static)
        self.list_widget.setSpacing(12)
        self.list_widget.setIconSize(QtCore.QSize(64, 64))
        self.list_widget.itemSelectionChanged.connect(self.update_selection)
        self.list_widget.itemDoubleClicked.connect(self.edit_product)

        self.total_label = QtWidgets.QLabel("Total productos: 0")

        self.detail_name = QtWidgets.QLabel("Producto:")
        self.detail_price = QtWidgets.QLabel("Precio:")
        self.detail_stock = QtWidgets.QLabel("Stock:")
        self.detail_barcode = QtWidgets.QLabel("Código:")

        self.add_button = QtWidgets.QPushButton("Agregar")
        self.add_button.clicked.connect(self.add_product_dialog)
        self.edit_button = QtWidgets.QPushButton("Editar")
        self.edit_button.clicked.connect(self.edit_product)
        self.delete_button = QtWidgets.QPushButton("Eliminar")
        self.delete_button.clicked.connect(self.delete_product_dialog)

        left_panel = QtWidgets.QVBoxLayout()
        left_panel.addWidget(QtWidgets.QLabel("Buscar"))
        left_panel.addWidget(self.search_input)
        left_panel.addSpacing(10)
        left_panel.addWidget(self.total_label)
        left_panel.addSpacing(10)
        left_panel.addWidget(QtWidgets.QLabel("Selección"))
        left_panel.addWidget(self.detail_name)
        left_panel.addWidget(self.detail_price)
        left_panel.addWidget(self.detail_stock)
        left_panel.addWidget(self.detail_barcode)
        left_panel.addSpacing(10)
        left_panel.addWidget(QtWidgets.QLabel("Opciones"))
        left_panel.addWidget(self.add_button)
        left_panel.addWidget(self.edit_button)
        left_panel.addWidget(self.delete_button)
        left_panel.addStretch(1)

        left_container = QtWidgets.QWidget()
        left_container.setLayout(left_panel)
        left_container.setFixedWidth(260)

        main_layout = QtWidgets.QHBoxLayout(self)
        main_layout.addWidget(left_container)
        main_layout.addWidget(self.list_widget, 1)

        self.refresh_list()

    def refresh_list(self) -> None:
        search = self.search_input.text().strip()
        products = list_products(search)
        self.list_widget.clear()

        icon = self.style().standardIcon(QtWidgets.QStyle.SP_FileIcon)
        for row in products:
            item = QtWidgets.QListWidgetItem(
                icon,
                f"{row['name']}\n{format_money(row['price'])}\nStock: {row['stock']:.2f}",
            )
            item.setData(QtCore.Qt.UserRole, int(row["id"]))
            item.setSizeHint(QtCore.QSize(160, 120))
            self.list_widget.addItem(item)

        self.total_label.setText(f"Total productos: {len(products)}")
        self.update_selection()

    def _current_product_id(self) -> int | None:
        items = self.list_widget.selectedItems()
        if not items:
            return None
        return items[0].data(QtCore.Qt.UserRole)

    def update_selection(self) -> None:
        product_id = self._current_product_id()
        if not product_id:
            self.detail_name.setText("Producto:")
            self.detail_price.setText("Precio:")
            self.detail_stock.setText("Stock:")
            self.detail_barcode.setText("Código:")
            return

        row = get_product_by_id(product_id)
        if row is None:
            return

        self.detail_name.setText(f"Producto: {row['name']}")
        self.detail_price.setText(f"Precio: {format_money(row['price'])}")
        self.detail_stock.setText(f"Stock: {row['stock']:.2f}")
        self.detail_barcode.setText(f"Código: {row['barcode']}")

    def add_product_dialog(self) -> None:
        dialog = ProductDialog("Agregar producto", self)
        if dialog.exec() != QtWidgets.QDialog.Accepted:
            return

        values = dialog.get_values()
        if not values["barcode"] or not values["name"]:
            QtWidgets.QMessageBox.warning(
                self, "Datos incompletos", "Código y nombre son obligatorios"
            )
            return

        ok = add_product(
            values["barcode"], values["name"], values["price"], values["stock"]
        )
        if not ok:
            QtWidgets.QMessageBox.warning(
                self, "Duplicado", "Ese código de barras ya existe"
            )
            return

        self.refresh_list()

    def edit_product(self) -> None:
        product_id = self._current_product_id()
        if not product_id:
            return

        row = get_product_by_id(product_id)
        if row is None:
            return

        dialog = ProductDialog("Editar producto", self)
        dialog.set_values(dict(row))
        if dialog.exec() != QtWidgets.QDialog.Accepted:
            return

        values = dialog.get_values()
        ok = update_product(
            product_id,
            values["barcode"],
            values["name"],
            values["price"],
            values["stock"],
        )
        if not ok:
            QtWidgets.QMessageBox.warning(
                self, "Duplicado", "Ese código de barras ya existe"
            )
            return

        self.refresh_list()

    def delete_product_dialog(self) -> None:
        product_id = self._current_product_id()
        if not product_id:
            return

        confirm = QtWidgets.QMessageBox.question(
            self, "Eliminar", "¿Deseas eliminar este producto?"
        )
        if confirm != QtWidgets.QMessageBox.Yes:
            return

        delete_product(product_id)
        self.refresh_list()


class ContactDialog(QtWidgets.QDialog):
    def __init__(self, title: str, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setMinimumWidth(380)

        self.name_input = QtWidgets.QLineEdit()
        self.phone_input = QtWidgets.QLineEdit()
        self.email_input = QtWidgets.QLineEdit()
        self.address_input = QtWidgets.QLineEdit()

        form = QtWidgets.QFormLayout()
        form.addRow("Nombre", self.name_input)
        form.addRow("Teléfono", self.phone_input)
        form.addRow("Correo", self.email_input)
        form.addRow("Dirección", self.address_input)

        buttons = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout = QtWidgets.QVBoxLayout(self)
        layout.addLayout(form)
        layout.addWidget(buttons)

    def set_values(self, values: Dict[str, Any]) -> None:
        self.name_input.setText(values.get("name", ""))
        self.phone_input.setText(values.get("phone", ""))
        self.email_input.setText(values.get("email", ""))
        self.address_input.setText(values.get("address", ""))

    def get_values(self) -> Dict[str, Any]:
        return {
            "name": self.name_input.text().strip(),
            "phone": self.phone_input.text().strip(),
            "email": self.email_input.text().strip(),
            "address": self.address_input.text().strip(),
        }


class ExpenseDialog(QtWidgets.QDialog):
    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Nuevo gasto")
        self.setMinimumWidth(360)

        self.concept_input = QtWidgets.QLineEdit()
        self.amount_input = QtWidgets.QDoubleSpinBox()
        self.amount_input.setDecimals(2)
        self.amount_input.setMaximum(999999)
        self.amount_input.setPrefix(f"{get_currency_symbol()} ")

        form = QtWidgets.QFormLayout()
        form.addRow("Concepto", self.concept_input)
        form.addRow("Monto", self.amount_input)

        buttons = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout = QtWidgets.QVBoxLayout(self)
        layout.addLayout(form)
        layout.addWidget(buttons)

    def get_values(self) -> Dict[str, Any]:
        return {
            "concept": self.concept_input.text().strip(),
            "amount": float(self.amount_input.value()),
        }


class UserDialog(QtWidgets.QDialog):
    def __init__(self, title: str, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setMinimumWidth(380)

        self.username_input = QtWidgets.QLineEdit()
        self.password_input = QtWidgets.QLineEdit()
        self.password_input.setEchoMode(QtWidgets.QLineEdit.Password)
        self.display_name_input = QtWidgets.QLineEdit()
        self.role_input = QtWidgets.QComboBox()
        self.role_input.addItems(["Administrador", "Supervisor", "Cajero"])
        self.active_input = QtWidgets.QCheckBox("Usuario activo")
        self.active_input.setChecked(True)

        form = QtWidgets.QFormLayout()
        form.addRow("Usuario", self.username_input)
        form.addRow("Contraseña", self.password_input)
        form.addRow("Nombre", self.display_name_input)
        form.addRow("Rol", self.role_input)
        form.addRow("", self.active_input)

        buttons = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout = QtWidgets.QVBoxLayout(self)
        layout.addLayout(form)
        layout.addWidget(buttons)

    def set_values(self, values: Dict[str, Any]) -> None:
        self.username_input.setText(values.get("username", ""))
        self.display_name_input.setText(values.get("display_name", ""))
        role = values.get("role", "Administrador")
        index = self.role_input.findText(role)
        if index >= 0:
            self.role_input.setCurrentIndex(index)
        self.active_input.setChecked(bool(values.get("is_active", 1)))

    def get_values(self) -> Dict[str, Any]:
        return {
            "username": self.username_input.text().strip(),
            "password": self.password_input.text().strip(),
            "display_name": self.display_name_input.text().strip(),
            "role": self.role_input.currentText(),
            "is_active": self.active_input.isChecked(),
        }


class CustomersWidget(QtWidgets.QWidget):
    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)
        self.table = QtWidgets.QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["Nombre", "Teléfono", "Correo", "Dirección"])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)

        self.add_button = QtWidgets.QPushButton("Agregar")
        self.add_button.clicked.connect(self.add_item)
        self.edit_button = QtWidgets.QPushButton("Editar")
        self.edit_button.clicked.connect(self.edit_item)
        self.delete_button = QtWidgets.QPushButton("Eliminar")
        self.delete_button.clicked.connect(self.delete_item)

        actions = QtWidgets.QHBoxLayout()
        actions.addWidget(self.add_button)
        actions.addWidget(self.edit_button)
        actions.addWidget(self.delete_button)
        actions.addStretch(1)

        layout = QtWidgets.QVBoxLayout(self)
        layout.addLayout(actions)
        layout.addWidget(self.table)

        self.refresh()

    def refresh(self) -> None:
        rows = list_customers()
        self.table.setRowCount(len(rows))
        for row_index, row in enumerate(rows):
            item = QtWidgets.QTableWidgetItem(row["name"])
            item.setData(QtCore.Qt.UserRole, int(row["id"]))
            self.table.setItem(row_index, 0, item)
            self.table.setItem(row_index, 1, QtWidgets.QTableWidgetItem(row["phone"] or ""))
            self.table.setItem(row_index, 2, QtWidgets.QTableWidgetItem(row["email"] or ""))
            self.table.setItem(row_index, 3, QtWidgets.QTableWidgetItem(row["address"] or ""))

    def _current_id(self) -> int | None:
        items = self.table.selectedItems()
        if not items:
            return None
        return items[0].data(QtCore.Qt.UserRole)

    def add_item(self) -> None:
        dialog = ContactDialog("Nuevo cliente", self)
        if dialog.exec() != QtWidgets.QDialog.Accepted:
            return
        values = dialog.get_values()
        if not values["name"]:
            QtWidgets.QMessageBox.warning(self, "Datos incompletos", "Nombre requerido")
            return
        add_customer(values["name"], values["phone"], values["email"], values["address"])
        self.refresh()

    def edit_item(self) -> None:
        customer_id = self._current_id()
        if not customer_id:
            return
        row = list_customers()
        current = next((r for r in row if r["id"] == customer_id), None)
        if current is None:
            return
        dialog = ContactDialog("Editar cliente", self)
        dialog.set_values(dict(current))
        if dialog.exec() != QtWidgets.QDialog.Accepted:
            return
        values = dialog.get_values()
        if not values["name"]:
            QtWidgets.QMessageBox.warning(self, "Datos incompletos", "Nombre requerido")
            return
        update_customer(customer_id, values["name"], values["phone"], values["email"], values["address"])
        self.refresh()

    def delete_item(self) -> None:
        customer_id = self._current_id()
        if not customer_id:
            return
        confirm = QtWidgets.QMessageBox.question(self, "Eliminar", "¿Eliminar cliente?")
        if confirm != QtWidgets.QMessageBox.Yes:
            return
        delete_customer(customer_id)
        self.refresh()


class SuppliersWidget(QtWidgets.QWidget):
    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)
        self.table = QtWidgets.QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["Nombre", "Teléfono", "Correo", "Dirección"])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)

        self.add_button = QtWidgets.QPushButton("Agregar")
        self.add_button.clicked.connect(self.add_item)
        self.edit_button = QtWidgets.QPushButton("Editar")
        self.edit_button.clicked.connect(self.edit_item)
        self.delete_button = QtWidgets.QPushButton("Eliminar")
        self.delete_button.clicked.connect(self.delete_item)

        actions = QtWidgets.QHBoxLayout()
        actions.addWidget(self.add_button)
        actions.addWidget(self.edit_button)
        actions.addWidget(self.delete_button)
        actions.addStretch(1)

        layout = QtWidgets.QVBoxLayout(self)
        layout.addLayout(actions)
        layout.addWidget(self.table)

        self.refresh()

    def refresh(self) -> None:
        rows = list_suppliers()
        self.table.setRowCount(len(rows))
        for row_index, row in enumerate(rows):
            item = QtWidgets.QTableWidgetItem(row["name"])
            item.setData(QtCore.Qt.UserRole, int(row["id"]))
            self.table.setItem(row_index, 0, item)
            self.table.setItem(row_index, 1, QtWidgets.QTableWidgetItem(row["phone"] or ""))
            self.table.setItem(row_index, 2, QtWidgets.QTableWidgetItem(row["email"] or ""))
            self.table.setItem(row_index, 3, QtWidgets.QTableWidgetItem(row["address"] or ""))

    def _current_id(self) -> int | None:
        items = self.table.selectedItems()
        if not items:
            return None
        return items[0].data(QtCore.Qt.UserRole)

    def add_item(self) -> None:
        dialog = ContactDialog("Nuevo proveedor", self)
        if dialog.exec() != QtWidgets.QDialog.Accepted:
            return
        values = dialog.get_values()
        if not values["name"]:
            QtWidgets.QMessageBox.warning(self, "Datos incompletos", "Nombre requerido")
            return
        add_supplier(values["name"], values["phone"], values["email"], values["address"])
        self.refresh()

    def edit_item(self) -> None:
        supplier_id = self._current_id()
        if not supplier_id:
            return
        row = list_suppliers()
        current = next((r for r in row if r["id"] == supplier_id), None)
        if current is None:
            return
        dialog = ContactDialog("Editar proveedor", self)
        dialog.set_values(dict(current))
        if dialog.exec() != QtWidgets.QDialog.Accepted:
            return
        values = dialog.get_values()
        if not values["name"]:
            QtWidgets.QMessageBox.warning(self, "Datos incompletos", "Nombre requerido")
            return
        update_supplier(supplier_id, values["name"], values["phone"], values["email"], values["address"])
        self.refresh()

    def delete_item(self) -> None:
        supplier_id = self._current_id()
        if not supplier_id:
            return
        confirm = QtWidgets.QMessageBox.question(self, "Eliminar", "¿Eliminar proveedor?")
        if confirm != QtWidgets.QMessageBox.Yes:
            return
        delete_supplier(supplier_id)
        self.refresh()


class ExpensesWidget(QtWidgets.QWidget):
    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)
        self.table = QtWidgets.QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["Fecha", "Concepto", "Monto"])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)

        self.add_button = QtWidgets.QPushButton("Agregar")
        self.add_button.clicked.connect(self.add_item)
        self.delete_button = QtWidgets.QPushButton("Eliminar")
        self.delete_button.clicked.connect(self.delete_item)

        actions = QtWidgets.QHBoxLayout()
        actions.addWidget(self.add_button)
        actions.addWidget(self.delete_button)
        actions.addStretch(1)

        layout = QtWidgets.QVBoxLayout(self)
        layout.addLayout(actions)
        layout.addWidget(self.table)

        self.refresh()

    def refresh(self) -> None:
        rows = list_expenses()
        self.table.setRowCount(len(rows))
        for row_index, row in enumerate(rows):
            item = QtWidgets.QTableWidgetItem(row["created_at"])
            item.setData(QtCore.Qt.UserRole, int(row["id"]))
            self.table.setItem(row_index, 0, item)
            self.table.setItem(row_index, 1, QtWidgets.QTableWidgetItem(row["concept"]))
            self.table.setItem(row_index, 2, QtWidgets.QTableWidgetItem(format_money(row["amount"])))

    def _current_id(self) -> int | None:
        items = self.table.selectedItems()
        if not items:
            return None
        return items[0].data(QtCore.Qt.UserRole)

    def add_item(self) -> None:
        dialog = ExpenseDialog(self)
        if dialog.exec() != QtWidgets.QDialog.Accepted:
            return
        values = dialog.get_values()
        if not values["concept"]:
            QtWidgets.QMessageBox.warning(self, "Datos incompletos", "Concepto requerido")
            return
        add_expense(values["concept"], values["amount"])
        self.refresh()

    def delete_item(self) -> None:
        expense_id = self._current_id()
        if not expense_id:
            return
        confirm = QtWidgets.QMessageBox.question(self, "Eliminar", "¿Eliminar gasto?")
        if confirm != QtWidgets.QMessageBox.Yes:
            return
        delete_expense(expense_id)
        self.refresh()


class UsersWidget(QtWidgets.QWidget):
    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)
        self.table = QtWidgets.QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["Usuario", "Nombre", "Rol", "Activo"])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)

        self.add_button = QtWidgets.QPushButton("Agregar")
        self.add_button.clicked.connect(self.add_item)
        self.edit_button = QtWidgets.QPushButton("Editar")
        self.edit_button.clicked.connect(self.edit_item)
        self.delete_button = QtWidgets.QPushButton("Eliminar")
        self.delete_button.clicked.connect(self.delete_item)

        actions = QtWidgets.QHBoxLayout()
        actions.addWidget(self.add_button)
        actions.addWidget(self.edit_button)
        actions.addWidget(self.delete_button)
        actions.addStretch(1)

        layout = QtWidgets.QVBoxLayout(self)
        layout.addLayout(actions)
        layout.addWidget(self.table)

        self.refresh()

    def refresh(self) -> None:
        rows = list_users()
        self.table.setRowCount(len(rows))
        for row_index, row in enumerate(rows):
            item = QtWidgets.QTableWidgetItem(row["username"])
            item.setData(QtCore.Qt.UserRole, int(row["id"]))
            self.table.setItem(row_index, 0, item)
            self.table.setItem(row_index, 1, QtWidgets.QTableWidgetItem(row["display_name"]))
            self.table.setItem(row_index, 2, QtWidgets.QTableWidgetItem(row["role"]))
            self.table.setItem(row_index, 3, QtWidgets.QTableWidgetItem("Sí" if row["is_active"] else "No"))

    def _current_id(self) -> int | None:
        items = self.table.selectedItems()
        if not items:
            return None
        return items[0].data(QtCore.Qt.UserRole)

    def add_item(self) -> None:
        dialog = UserDialog("Nuevo usuario", self)
        if dialog.exec() != QtWidgets.QDialog.Accepted:
            return
        values = dialog.get_values()
        if not values["username"] or not values["password"]:
            QtWidgets.QMessageBox.warning(self, "Datos incompletos", "Usuario y contraseña requeridos")
            return
        ok = add_user(values["username"], values["password"], values["display_name"], values["role"])
        if not ok:
            QtWidgets.QMessageBox.warning(self, "Duplicado", "Ese usuario ya existe")
            return
        self.refresh()

    def edit_item(self) -> None:
        user_id = self._current_id()
        if not user_id:
            return
        rows = list_users()
        current = next((r for r in rows if r["id"] == user_id), None)
        if current is None:
            return
        dialog = UserDialog("Editar usuario", self)
        dialog.set_values(dict(current))
        if dialog.exec() != QtWidgets.QDialog.Accepted:
            return
        values = dialog.get_values()
        ok = update_user(
            user_id,
            values["username"],
            values["password"] or None,
            values["display_name"],
            values["role"],
            values["is_active"],
        )
        if not ok:
            QtWidgets.QMessageBox.warning(self, "Duplicado", "Ese usuario ya existe")
            return
        self.refresh()

    def delete_item(self) -> None:
        user_id = self._current_id()
        if not user_id:
            return
        confirm = QtWidgets.QMessageBox.question(self, "Eliminar", "¿Eliminar usuario?")
        if confirm != QtWidgets.QMessageBox.Yes:
            return
        delete_user(user_id)
        self.refresh()


class PurchasesWidget(QtWidgets.QWidget):
    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)
        self.cart: Dict[str, Dict[str, Any]] = {}

        self.barcode_input = QtWidgets.QLineEdit()
        self.barcode_input.setPlaceholderText("Escanea el código de barras")
        self.barcode_input.returnPressed.connect(self.add_barcode)
        # Fuerza texto negro y fondo blanco para que siempre sea visible
        self.barcode_input.setStyleSheet(
            "color: #000000; background: #ffffff; selection-color: #000000; "
            "selection-background-color: #ffd54f; border: 1px solid #c0c4cc;"
        )
        barcode_palette = self.barcode_input.palette()
        barcode_palette.setColor(QtGui.QPalette.Text, QtCore.Qt.black)
        barcode_palette.setColor(QtGui.QPalette.Base, QtCore.Qt.white)
        barcode_palette.setColor(QtGui.QPalette.PlaceholderText, QtCore.Qt.darkGray)
        self.barcode_input.setPalette(barcode_palette)
        # Fuerza texto negro y fondo claro; también corrige la paleta para evitar heredar colores blancos
        self.barcode_input.setStyleSheet(
            "color: #000000; background: #ffffff; selection-color: #000000; "
            "selection-background-color: #ffd54f; border: 1px solid #c0c4cc;"
        )
        barcode_palette = self.barcode_input.palette()
        barcode_palette.setColor(QtGui.QPalette.Text, QtCore.Qt.black)
        barcode_palette.setColor(QtGui.QPalette.Base, QtCore.Qt.white)
        barcode_palette.setColor(QtGui.QPalette.PlaceholderText, QtCore.Qt.darkGray)
        self.barcode_input.setPalette(barcode_palette)

        self.qty_input = QtWidgets.QDoubleSpinBox()
        self.qty_input.setDecimals(2)
        self.qty_input.setMinimum(0.01)
        self.qty_input.setMaximum(9999)
        self.qty_input.setValue(1)

        self.cost_input = QtWidgets.QDoubleSpinBox()
        self.cost_input.setDecimals(2)
        self.cost_input.setMaximum(999999)
        self.cost_input.setPrefix(f"{get_currency_symbol()} ")

        self.supplier_input = QtWidgets.QComboBox()
        self._load_suppliers()

        self.add_button = QtWidgets.QPushButton("Agregar")
        self.add_button.clicked.connect(self.add_barcode)

        self.save_button = QtWidgets.QPushButton("Guardar compra")
        self.save_button.clicked.connect(self.save_purchase)

        self.table = QtWidgets.QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(
            ["Código", "Producto", "Costo", "Cantidad", "Total"]
        )
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)

        self.total_label = QtWidgets.QLabel(format_money(0))

        top_bar = QtWidgets.QHBoxLayout()
        top_bar.addWidget(QtWidgets.QLabel("Proveedor:"))
        top_bar.addWidget(self.supplier_input)
        top_bar.addWidget(QtWidgets.QLabel("Código:"))
        top_bar.addWidget(self.barcode_input, 2)
        top_bar.addWidget(QtWidgets.QLabel("Cantidad:"))
        top_bar.addWidget(self.qty_input)
        top_bar.addWidget(QtWidgets.QLabel("Costo:"))
        top_bar.addWidget(self.cost_input)
        top_bar.addWidget(self.add_button)

        totals = QtWidgets.QHBoxLayout()
        totals.addStretch(1)
        totals.addWidget(QtWidgets.QLabel("Total compra:"))
        totals.addWidget(self.total_label)
        totals.addWidget(self.save_button)

        layout = QtWidgets.QVBoxLayout(self)
        layout.addLayout(top_bar)
        layout.addWidget(self.table, 1)
        layout.addLayout(totals)

    def _load_suppliers(self) -> None:
        self.supplier_input.clear()
        self.supplier_input.addItem("Sin proveedor", None)
        for row in list_suppliers():
            self.supplier_input.addItem(row["name"], int(row["id"]))

    def add_barcode(self) -> None:
        barcode = self.barcode_input.text().strip()
        if not barcode:
            return
        qty = float(self.qty_input.value())
        cost = float(self.cost_input.value())
        product = get_product_by_barcode(barcode)
        if product is None:
            QtWidgets.QApplication.beep()
            return
        if cost <= 0:
            cost = float(product["price"])

        if barcode in self.cart:
            self.cart[barcode]["quantity"] += qty
        else:
            self.cart[barcode] = {
                "product_id": product["id"],
                "barcode": product["barcode"],
                "name": product["name"],
                "cost": cost,
                "quantity": qty,
            }

        self.cart[barcode]["line_total"] = (
            self.cart[barcode]["cost"] * self.cart[barcode]["quantity"]
        )
        self.barcode_input.clear()
        self.qty_input.setValue(1)
        self.cost_input.setValue(0)
        self.update_table()

    def update_table(self) -> None:
        self.table.setRowCount(len(self.cart))
        total = 0.0
        for row, item in enumerate(self.cart.values()):
            self.table.setItem(row, 0, QtWidgets.QTableWidgetItem(item["barcode"]))
            self.table.setItem(row, 1, QtWidgets.QTableWidgetItem(item["name"]))
            self.table.setItem(row, 2, QtWidgets.QTableWidgetItem(format_money(item["cost"])))
            self.table.setItem(row, 3, QtWidgets.QTableWidgetItem(f"{item['quantity']:.2f}"))
            self.table.setItem(row, 4, QtWidgets.QTableWidgetItem(format_money(item["line_total"])))
            total += item["line_total"]
        self.total_label.setText(format_money(total))

    def save_purchase(self) -> None:
        if not self.cart:
            return
        supplier_id = self.supplier_input.currentData()
        try:
            record_purchase(self.cart.values(), supplier_id)
        except Exception as exc:  # noqa: BLE001
            QtWidgets.QMessageBox.critical(self, "Error", str(exc))
            return
        self.cart.clear()
        self.update_table()
        QtWidgets.QMessageBox.information(self, "Compra", "Compra guardada")


class ReportsWidget(QtWidgets.QWidget):
    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)
        self.date_input = QtWidgets.QDateEdit(QtCore.QDate.currentDate())
        self.date_input.setCalendarPopup(True)
        self.refresh_button = QtWidgets.QPushButton("Actualizar")
        self.refresh_button.clicked.connect(self.refresh)

        self.daily_table = QtWidgets.QTableWidget(0, 4)
        self.daily_table.setHorizontalHeaderLabels(["Código", "Producto", "Cantidad", "Total"])
        self.daily_table.horizontalHeader().setStretchLastSection(True)

        self.top_table = QtWidgets.QTableWidget(0, 4)
        self.top_table.setHorizontalHeaderLabels(["Código", "Producto", "Cantidad", "Total"])
        self.top_table.horizontalHeader().setStretchLastSection(True)

        self.export_csv = QtWidgets.QPushButton("Exportar CSV")
        self.export_csv.clicked.connect(lambda: self.export("csv"))
        self.export_excel = QtWidgets.QPushButton("Exportar Excel")
        self.export_excel.clicked.connect(lambda: self.export("xlsx"))
        self.export_pdf = QtWidgets.QPushButton("Exportar PDF")
        self.export_pdf.clicked.connect(lambda: self.export("pdf"))

        top_bar = QtWidgets.QHBoxLayout()
        top_bar.addWidget(QtWidgets.QLabel("Fecha:"))
        top_bar.addWidget(self.date_input)
        top_bar.addWidget(self.refresh_button)
        top_bar.addStretch(1)
        top_bar.addWidget(self.export_csv)
        top_bar.addWidget(self.export_excel)
        top_bar.addWidget(self.export_pdf)

        tabs = QtWidgets.QTabWidget()
        daily_tab = QtWidgets.QWidget()
        daily_layout = QtWidgets.QVBoxLayout(daily_tab)
        daily_layout.addWidget(self.daily_table)
        tabs.addTab(daily_tab, "Corte diario")

        top_tab = QtWidgets.QWidget()
        top_layout = QtWidgets.QVBoxLayout(top_tab)
        top_layout.addWidget(self.top_table)
        tabs.addTab(top_tab, "Top productos")

        layout = QtWidgets.QVBoxLayout(self)
        layout.addLayout(top_bar)
        layout.addWidget(tabs)

        self.refresh()

    def refresh(self) -> None:
        date_str = self.date_input.date().toString("yyyy-MM-dd")
        rows = get_daily_sales_summary(date_str)
        self.daily_table.setRowCount(len(rows))
        for row_index, row in enumerate(rows):
            self.daily_table.setItem(row_index, 0, QtWidgets.QTableWidgetItem(row["barcode"]))
            self.daily_table.setItem(row_index, 1, QtWidgets.QTableWidgetItem(row["name"]))
            self.daily_table.setItem(row_index, 2, QtWidgets.QTableWidgetItem(f"{row['quantity']:.2f}"))
            self.daily_table.setItem(row_index, 3, QtWidgets.QTableWidgetItem(format_money(row["total"])))

        top_rows = get_top_products(30)
        self.top_table.setRowCount(len(top_rows))
        for row_index, row in enumerate(top_rows):
            self.top_table.setItem(row_index, 0, QtWidgets.QTableWidgetItem(row["barcode"]))
            self.top_table.setItem(row_index, 1, QtWidgets.QTableWidgetItem(row["name"]))
            self.top_table.setItem(row_index, 2, QtWidgets.QTableWidgetItem(f"{row['quantity']:.2f}"))
            self.top_table.setItem(row_index, 3, QtWidgets.QTableWidgetItem(format_money(row["total"])))

    def export(self, fmt: str) -> None:
        date_str = self.date_input.date().toString("yyyy-MM-dd")
        rows = get_daily_sales_summary(date_str)
        data = [
            {
                "barcode": row["barcode"],
                "name": row["name"],
                "quantity": float(row["quantity"]),
                "total": float(row["total"]),
            }
            for row in rows
        ]
        if not data:
            QtWidgets.QMessageBox.information(self, "Exportar", "No hay datos")
            return

        if fmt == "csv":
            path, _ = QtWidgets.QFileDialog.getSaveFileName(
                self, "Exportar CSV", "", "CSV (*.csv)"
            )
            if not path:
                return
            pd.DataFrame(data).to_csv(path, index=False)
        elif fmt == "xlsx":
            path, _ = QtWidgets.QFileDialog.getSaveFileName(
                self, "Exportar Excel", "", "Excel (*.xlsx)"
            )
            if not path:
                return
            pd.DataFrame(data).to_excel(path, index=False)
        elif fmt == "pdf":
            path, _ = QtWidgets.QFileDialog.getSaveFileName(
                self, "Exportar PDF", "", "PDF (*.pdf)"
            )
            if not path:
                return
            self._export_pdf(path, date_str, data)

    def _export_pdf(self, path: str, date_str: str, data: list[Dict[str, Any]]) -> None:
        c = canvas.Canvas(path)
        y = 800
        c.setFont("Helvetica-Bold", 12)
        c.drawString(40, y, f"Corte del día {date_str}")
        y -= 20
        c.setFont("Helvetica", 9)
        for row in data:
            line = f"{row['barcode']} - {row['name']} - {row['quantity']:.2f} - {format_money(row['total'])}"
            c.drawString(40, y, line[:120])
            y -= 12
            if y < 40:
                c.showPage()
                y = 800
        c.save()


class SimpleListDialog(QtWidgets.QDialog):
    def __init__(
        self,
        title: str,
        list_callback,
        add_callback,
        delete_callback,
        parent=None,
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setMinimumSize(420, 320)
        self.list_callback = list_callback
        self.add_callback = add_callback
        self.delete_callback = delete_callback

        self.list_widget = QtWidgets.QListWidget()
        self.refresh()

        self.name_input = QtWidgets.QLineEdit()
        self.add_button = QtWidgets.QPushButton("Agregar")
        self.add_button.clicked.connect(self.add_item)
        self.delete_button = QtWidgets.QPushButton("Eliminar")
        self.delete_button.clicked.connect(self.delete_item)

        actions = QtWidgets.QHBoxLayout()
        actions.addWidget(self.name_input)
        actions.addWidget(self.add_button)
        actions.addWidget(self.delete_button)

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.list_widget)
        layout.addLayout(actions)

    def refresh(self) -> None:
        self.list_widget.clear()
        for item in self.list_callback():
            list_item = QtWidgets.QListWidgetItem(item["name"])
            list_item.setData(QtCore.Qt.UserRole, int(item["id"]))
            self.list_widget.addItem(list_item)

    def add_item(self) -> None:
        name = self.name_input.text().strip()
        if not name:
            return
        ok = self.add_callback(name)
        if not ok:
            QtWidgets.QMessageBox.warning(self, "Duplicado", "Ese nombre ya existe")
            return
        self.name_input.clear()
        self.refresh()

    def delete_item(self) -> None:
        item = self.list_widget.currentItem()
        if not item:
            return
        confirm = QtWidgets.QMessageBox.question(self, "Eliminar", "¿Eliminar elemento?")
        if confirm != QtWidgets.QMessageBox.Yes:
            return
        item_id = item.data(QtCore.Qt.UserRole)
        if item_id is not None and item_id >= 0:
            self.delete_callback(int(item_id))
        self.refresh()


class CompanyDialog(QtWidgets.QDialog):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Mi Empresa")
        self.setMinimumWidth(420)

        self.name_input = QtWidgets.QLineEdit(get_setting("company_name", "Abarrotes"))
        self.phone_input = QtWidgets.QLineEdit(get_setting("company_phone", ""))
        self.address_input = QtWidgets.QLineEdit(get_setting("company_address", ""))
        self.rfc_input = QtWidgets.QLineEdit(get_setting("company_rfc", ""))

        form = QtWidgets.QFormLayout()
        form.addRow("Nombre", self.name_input)
        form.addRow("Teléfono", self.phone_input)
        form.addRow("Dirección", self.address_input)
        form.addRow("RFC", self.rfc_input)

        buttons = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Save | QtWidgets.QDialogButtonBox.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout = QtWidgets.QVBoxLayout(self)
        layout.addLayout(form)
        layout.addWidget(buttons)

    def save(self) -> None:
        set_setting("company_name", self.name_input.text().strip())
        set_setting("company_phone", self.phone_input.text().strip())
        set_setting("company_address", self.address_input.text().strip())
        set_setting("company_rfc", self.rfc_input.text().strip())


class CurrencyDialog(QtWidgets.QDialog):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Moneda")
        self.setMinimumWidth(300)

        self.symbol_input = QtWidgets.QLineEdit(get_setting("currency_symbol", "$"))
        form = QtWidgets.QFormLayout()
        form.addRow("Símbolo", self.symbol_input)

        buttons = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Save | QtWidgets.QDialogButtonBox.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout = QtWidgets.QVBoxLayout(self)
        layout.addLayout(form)
        layout.addWidget(buttons)

    def save(self) -> None:
        set_setting("currency_symbol", self.symbol_input.text().strip() or "$")


class TicketDialog(QtWidgets.QDialog):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Editar Factura / Ticket")
        self.setMinimumWidth(420)

        self.footer_input = QtWidgets.QLineEdit(
            get_setting("ticket_footer", "Gracias por su compra")
        )

        form = QtWidgets.QFormLayout()
        form.addRow("Pie de ticket", self.footer_input)

        buttons = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Save | QtWidgets.QDialogButtonBox.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout = QtWidgets.QVBoxLayout(self)
        layout.addLayout(form)
        layout.addWidget(buttons)

    def save(self) -> None:
        set_setting("ticket_footer", self.footer_input.text().strip())


class SalesWidget(QtWidgets.QWidget):
    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)
        self.cart: Dict[str, Dict[str, Any]] = {}
        self.last_ticket_path: Path | None = None
        # IVA se desactiva; forzamos 0
        self.tax_rate = 0.0

        self.barcode_input = QtWidgets.QLineEdit()
        self.barcode_input.setPlaceholderText("Escanea el código de barras")
        self.barcode_input.returnPressed.connect(self.add_barcode)

        self.qty_input = QtWidgets.QDoubleSpinBox()
        self.qty_input.setDecimals(2)
        self.qty_input.setMinimum(0.01)
        self.qty_input.setMaximum(9999)
        self.qty_input.setValue(1)

        self.add_button = QtWidgets.QPushButton("Agregar")
        self.add_button.clicked.connect(self.add_barcode)

        self.discount_input = QtWidgets.QDoubleSpinBox()
        self.discount_input.setDecimals(2)
        self.discount_input.setMaximum(999999)
        self.discount_input.setPrefix(f"{get_currency_symbol()} ")
        self.discount_input.valueChanged.connect(self.update_table)

        self.payment_input = QtWidgets.QDoubleSpinBox()
        self.payment_input.setDecimals(2)
        self.payment_input.setMaximum(999999)
        self.payment_input.setPrefix(f"{get_currency_symbol()} ")
        self.payment_input.valueChanged.connect(self.update_table)

        self.clear_button = QtWidgets.QPushButton("Vaciar carrito")
        self.clear_button.clicked.connect(self.clear_cart)

        self.remove_button = QtWidgets.QPushButton("Quitar seleccionado")
        self.remove_button.clicked.connect(self.remove_selected_item)

        self.checkout_button = QtWidgets.QPushButton("Finalizar venta")
        self.checkout_button.clicked.connect(self.complete_sale)

        self.print_button = QtWidgets.QPushButton("Imprimir ticket")
        self.print_button.setEnabled(False)
        self.print_button.clicked.connect(self.open_last_ticket)

        self.new_product_button = QtWidgets.QPushButton("Nuevo producto")
        self.new_product_button.clicked.connect(self.open_add_product)

        self.daily_report_button = QtWidgets.QPushButton("Corte del día")
        self.daily_report_button.clicked.connect(self.open_daily_report)

        self.table = QtWidgets.QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(
            ["Código", "Producto", "Precio", "Cantidad", "Total"]
        )
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)

        self.subtotal_label = QtWidgets.QLabel(format_money(0))
        self.discount_label = QtWidgets.QLabel(format_money(0))
        self.total_label = QtWidgets.QLabel(format_money(0))
        self.change_label = QtWidgets.QLabel(format_money(0))
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setBold(True)
        self.total_label.setFont(font)

        top_bar = QtWidgets.QHBoxLayout()
        top_bar.addWidget(QtWidgets.QLabel("Código:"))
        top_bar.addWidget(self.barcode_input, 3)
        top_bar.addWidget(QtWidgets.QLabel("Cantidad:"))
        top_bar.addWidget(self.qty_input)
        top_bar.addWidget(self.add_button)
        top_bar.addWidget(QtWidgets.QLabel("Descuento:"))
        top_bar.addWidget(self.discount_input)

        totals_layout = QtWidgets.QGridLayout()
        totals_layout.addWidget(QtWidgets.QLabel("Subtotal:"), 0, 0)
        totals_layout.addWidget(self.subtotal_label, 0, 1)
        totals_layout.addWidget(QtWidgets.QLabel("Descuento:"), 1, 0)
        totals_layout.addWidget(self.discount_label, 1, 1)
        totals_layout.addWidget(QtWidgets.QLabel("Total:"), 2, 0)
        totals_layout.addWidget(self.total_label, 2, 1)
        totals_layout.addWidget(QtWidgets.QLabel("Pago con:"), 3, 0)
        totals_layout.addWidget(self.payment_input, 3, 1)
        totals_layout.addWidget(QtWidgets.QLabel("Cambio:"), 4, 0)
        totals_layout.addWidget(self.change_label, 4, 1)

        actions_layout = QtWidgets.QHBoxLayout()
        actions_layout.addWidget(self.new_product_button)
        actions_layout.addWidget(self.daily_report_button)
        actions_layout.addWidget(self.print_button)
        actions_layout.addStretch(1)
        actions_layout.addWidget(self.remove_button)
        actions_layout.addWidget(self.clear_button)
        actions_layout.addWidget(self.checkout_button)

        layout = QtWidgets.QVBoxLayout(self)
        layout.addLayout(top_bar)
        layout.addWidget(self.table, 1)
        layout.addLayout(totals_layout)
        layout.addLayout(actions_layout)

    def add_barcode(self) -> None:
        barcode = self.barcode_input.text().strip()
        if not barcode:
            return

        qty = float(self.qty_input.value())
        product = get_product_by_barcode(barcode)
        if product is None:
            QtWidgets.QApplication.beep()
            self._status_message("Producto no encontrado", 3000)
            return

        if barcode in self.cart:
            self.cart[barcode]["quantity"] += qty
        else:
            self.cart[barcode] = {
                "product_id": product["id"],
                "barcode": product["barcode"],
                "name": product["name"],
                "price": float(product["price"]),
                "quantity": qty,
            }

        self.cart[barcode]["line_total"] = (
            self.cart[barcode]["price"] * self.cart[barcode]["quantity"]
        )

        self.barcode_input.clear()
        self.qty_input.setValue(1)
        self.update_table()

    def update_table(self) -> None:
        self.table.setRowCount(len(self.cart))
        subtotal = 0.0

        for row, item in enumerate(self.cart.values()):
            self.table.setItem(row, 0, QtWidgets.QTableWidgetItem(item["barcode"]))
            self.table.setItem(row, 1, QtWidgets.QTableWidgetItem(item["name"]))
            self.table.setItem(
                row, 2, QtWidgets.QTableWidgetItem(format_money(item["price"]))
            )
            self.table.setItem(
                row, 3, QtWidgets.QTableWidgetItem(f"{item['quantity']:.2f}")
            )
            self.table.setItem(
                row, 4, QtWidgets.QTableWidgetItem(format_money(item["line_total"]))
            )
            subtotal += item["line_total"]

        self.subtotal_label.setText(format_money(subtotal))
        discount = float(self.discount_input.value())
        total = max(0.0, subtotal - discount)
        payment = float(self.payment_input.value())
        change = max(0.0, payment - total)
        self.discount_label.setText(format_money(discount))
        self.total_label.setText(format_money(total))
        self.change_label.setText(format_money(change))

    def clear_cart(self) -> None:
        self.cart.clear()
        self.update_table()
        self._status_message("Carrito limpio", 2000)

    def remove_selected_item(self) -> None:
        row = self.table.currentRow()
        if row < 0:
            self._status_message("Selecciona un producto de la lista", 2500)
            return
        barcode_item = self.table.item(row, 0)
        if not barcode_item:
            self._status_message("No se pudo obtener el código", 2500)
            return
        barcode = barcode_item.text()
        if barcode in self.cart:
            del self.cart[barcode]
            self.update_table()
            self._status_message("Producto quitado del carrito", 2500)
        else:
            self._status_message("No se encontró el producto en el carrito", 2500)

    def complete_sale(self) -> None:
        if not self.cart:
            self._status_message("No hay productos en el carrito", 3000)
            return

        try:
            discount = float(self.discount_input.value())
            subtotal = sum(item["line_total"] for item in self.cart.values())
            total_due = max(0.0, subtotal - discount)
            payment = float(self.payment_input.value())
            if payment < total_due:
                QtWidgets.QMessageBox.warning(
                    self,
                    "Pago insuficiente",
                    f"Total: {format_money(total_due)}\nPago con: {format_money(payment)}",
                )
                return

            sale_id, total = record_sale(
                self.cart.values(), discount=discount, tax_rate=0.0
            )
            change = max(0.0, payment - total)
        except Exception as exc:  # noqa: BLE001
            QtWidgets.QMessageBox.critical(self, "Error", str(exc))
            return

        self.last_ticket_path = self._generate_ticket_pdf(
            sale_id,
            list(self.cart.values()),
            discount,
            payment,
            change,
        )
        self.print_button.setEnabled(self.last_ticket_path is not None)
        self.clear_cart()
        self.discount_input.setValue(0)
        self.payment_input.setValue(0)
        self.change_label.setText(format_money(0))
        self._status_message(
            f"Venta #{sale_id} registrada. Total {format_money(total)} | Cambio {format_money(change)}",
            4000,
        )

    def open_add_product(self) -> None:
        dialog = AddProductDialog(self)
        if dialog.exec() != QtWidgets.QDialog.Accepted:
            return

        values = dialog.get_values()
        if not values["barcode"] or not values["name"]:
            QtWidgets.QMessageBox.warning(
                self, "Datos incompletos", "Código y nombre son obligatorios"
            )
            return

        ok = add_product(
            values["barcode"], values["name"], values["price"], values["stock"]
        )
        if not ok:
            QtWidgets.QMessageBox.warning(
                self, "Duplicado", "Ese código de barras ya existe"
            )
            return

        self._status_message("Producto agregado", 3000)

    def open_daily_report(self) -> None:
        dialog = DailyReportDialog(self)
        dialog.exec()

    def open_last_ticket(self) -> None:
        if self.last_ticket_path and self.last_ticket_path.exists():
            QtGui.QDesktopServices.openUrl(
                QtCore.QUrl.fromLocalFile(str(self.last_ticket_path))
            )

    def _generate_ticket_pdf(
        self,
        sale_id: int,
        items: list[Dict[str, Any]],
        discount: float,
        payment: float,
        change: float,
    ) -> Path | None:
        tickets_dir = Path(__file__).resolve().parent.parent / "data" / "tickets"
        tickets_dir.mkdir(parents=True, exist_ok=True)
        ticket_path = tickets_dir / f"venta_{sale_id}.pdf"

        subtotal = sum(item["line_total"] for item in items)
        taxable = max(0.0, subtotal - discount)
        total = taxable

        width = 80 * mm
        height = 200 * mm
        c = canvas.Canvas(str(ticket_path), pagesize=(width, height))
        y = height - 10 * mm

        company = get_setting("company_name", "Abarrotes")
        c.setFont("Helvetica-Bold", 10)
        c.drawString(8 * mm, y, company)
        y -= 6 * mm
        c.setFont("Helvetica", 8)
        c.drawString(8 * mm, y, f"Venta #{sale_id}")
        y -= 5 * mm

        for item in items:
            c.drawString(8 * mm, y, item["name"][:20])
            y -= 4 * mm
            line = f"{item['quantity']:.2f} x {format_money(item['price'])}"
            c.drawString(8 * mm, y, line)
            c.drawRightString(width - 6 * mm, y, format_money(item["line_total"]))
            y -= 5 * mm

        y -= 2 * mm
        c.drawString(8 * mm, y, "Subtotal:")
        c.drawRightString(width - 6 * mm, y, format_money(subtotal))
        y -= 4 * mm
        c.drawString(8 * mm, y, "Descuento:")
        c.drawRightString(width - 6 * mm, y, format_money(discount))
        y -= 4 * mm
        c.setFont("Helvetica-Bold", 9)
        c.drawString(8 * mm, y, "Total:")
        c.drawRightString(width - 6 * mm, y, format_money(total))
        y -= 5 * mm
        c.setFont("Helvetica", 8)
        c.drawString(8 * mm, y, "Pago con:")
        c.drawRightString(width - 6 * mm, y, format_money(payment))
        y -= 4 * mm
        c.drawString(8 * mm, y, "Cambio:")
        c.drawRightString(width - 6 * mm, y, format_money(change))

        footer = get_setting("ticket_footer", "Gracias por su compra")
        y -= 8 * mm
        c.setFont("Helvetica", 8)
        c.drawString(8 * mm, y, footer[:40])

        c.showPage()
        c.save()
        return ticket_path

    def _status_message(self, message: str, timeout: int) -> None:
        window = self.window()
        if isinstance(window, QtWidgets.QMainWindow) and window.statusBar():
            window.statusBar().showMessage(message, timeout)


class DashboardWindow(QtWidgets.QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Punto de Venta - Abarrotes")
        self.setMinimumSize(1100, 700)

        self.status_bar = QtWidgets.QStatusBar()
        self.setStatusBar(self.status_bar)

        self.stack = QtWidgets.QStackedWidget()
        self.sales_widget = SalesWidget()

        self.inventory_widget = InventoryWidget()
        self.customers_widget = CustomersWidget()
        self.suppliers_widget = SuppliersWidget()
        self.purchases_widget = PurchasesWidget()
        self.reports_widget = ReportsWidget()
        self.expenses_widget = ExpensesWidget()
        self.users_widget = UsersWidget()

        self.pages = {
            "Ventas": self.sales_widget,
            "Inventario": self.inventory_widget,
            "Clientes": self.customers_widget,
            "Proveedor": self.suppliers_widget,
            "Compras": self.purchases_widget,
            "Reportes": self.reports_widget,
            "Configuración": self._config_page(),
            "Gastos": self.expenses_widget,
            "Usuarios": self.users_widget,
            "Información": self._placeholder_page("Información"),
        }

        for widget in self.pages.values():
            self.stack.addWidget(widget)

        sidebar = QtWidgets.QFrame()
        sidebar.setObjectName("sidebar")
        sidebar_layout = QtWidgets.QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(12, 12, 12, 12)
        sidebar_layout.setSpacing(8)

        title = QtWidgets.QLabel("PUNTO DE VENTA")
        title.setObjectName("sidebarTitle")
        title.setAlignment(QtCore.Qt.AlignCenter)
        sidebar_layout.addWidget(title)

        self.nav_buttons: Dict[str, QtWidgets.QPushButton] = {}
        for name in self.pages.keys():
            button = QtWidgets.QPushButton(name)
            button.setCheckable(True)
            button.clicked.connect(lambda checked, n=name: self.switch_page(n))
            self.nav_buttons[name] = button
            sidebar_layout.addWidget(button)

        sidebar_layout.addStretch(1)

        logout_button = QtWidgets.QPushButton("Cerrar sesión")
        logout_button.clicked.connect(self.close)
        sidebar_layout.addWidget(logout_button)

        content_frame = QtWidgets.QFrame()
        content_layout = QtWidgets.QVBoxLayout(content_frame)
        content_layout.setContentsMargins(16, 16, 16, 16)
        content_layout.addWidget(self.stack)

        main = QtWidgets.QWidget()
        main_layout = QtWidgets.QHBoxLayout(main)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(sidebar)
        main_layout.addWidget(content_frame, 1)
        self.setCentralWidget(main)

        self._apply_dashboard_style()
        self.switch_page("Ventas")

    def _placeholder_page(self, title: str) -> QtWidgets.QWidget:
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(widget)
        label = QtWidgets.QLabel(title)
        label.setAlignment(QtCore.Qt.AlignCenter)
        label_font = QtGui.QFont()
        label_font.setPointSize(20)
        label_font.setBold(True)
        label.setFont(label_font)
        sub = QtWidgets.QLabel("Sección en desarrollo")
        sub.setAlignment(QtCore.Qt.AlignCenter)
        layout.addStretch(1)
        layout.addWidget(label)
        layout.addWidget(sub)
        layout.addStretch(1)
        return widget

    def _config_page(self) -> QtWidgets.QWidget:
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(widget)
        title = QtWidgets.QLabel("CONFIGURACIÓN")
        title.setAlignment(QtCore.Qt.AlignCenter)
        title_font = QtGui.QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title.setFont(title_font)

        grid = QtWidgets.QGridLayout()
        grid.setSpacing(16)

        items = [
            "Categorías",
            "Sucursales",
            "Mi Empresa",
            "Copia de seguridad DB",
            "Restaurar DB",
            "Eliminar registros DB",
            "Moneda",
            "Editar Factura",
            "Descargar Plantilla",
            "Importar Productos",
            "Exportar Productos",
        ]

        for index, label in enumerate(items):
            button = QtWidgets.QPushButton(label)
            button.setObjectName("tileButton")
            button.setFixedSize(170, 110)
            button.clicked.connect(lambda checked, text=label: self._handle_config_action(text))
            row = index // 5
            col = index % 5
            grid.addWidget(button, row, col)

        layout.addWidget(title)
        layout.addSpacing(10)
        layout.addLayout(grid)
        layout.addStretch(1)
        return widget

    def _handle_config_action(self, action: str) -> None:
        if action == "Categorías":
            dialog = SimpleListDialog(
                "Categorías",
                lambda: [dict(row) for row in list_categories()],
                add_category,
                delete_category,
                self,
            )
            dialog.exec()
        elif action == "Sucursales":
            dialog = SimpleListDialog(
                "Sucursales",
                lambda: [dict(row) for row in list_branches()],
                lambda name: add_branch(name, ""),
                delete_branch,
                self,
            )
            dialog.exec()
        elif action == "Mi Empresa":
            dialog = CompanyDialog(self)
            if dialog.exec() == QtWidgets.QDialog.Accepted:
                dialog.save()
        elif action == "Copia de seguridad DB":
            path, _ = QtWidgets.QFileDialog.getSaveFileName(
                self, "Guardar respaldo", "", "SQLite DB (*.db)"
            )
            if path:
                backup_database(Path(path))
        elif action == "Restaurar DB":
            path, _ = QtWidgets.QFileDialog.getOpenFileName(
                self, "Restaurar respaldo", "", "SQLite DB (*.db)"
            )
            if path:
                restore_database(Path(path))
        elif action == "Eliminar registros DB":
            confirm = QtWidgets.QMessageBox.question(
                self, "Eliminar", "¿Eliminar ventas, compras y gastos?"
            )
            if confirm == QtWidgets.QMessageBox.Yes:
                clear_transactions()
        elif action == "Moneda":
            dialog = CurrencyDialog(self)
            if dialog.exec() == QtWidgets.QDialog.Accepted:
                dialog.save()
        elif action == "Editar Factura":
            dialog = TicketDialog(self)
            if dialog.exec() == QtWidgets.QDialog.Accepted:
                dialog.save()
        elif action == "Descargar Plantilla":
            self._download_template()
        elif action == "Importar Productos":
            self._import_products()
        elif action == "Exportar Productos":
            self._export_products()

    def _download_template(self) -> None:
        path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self, "Guardar plantilla", "", "CSV (*.csv)"
        )
        if not path:
            return
        df = pd.DataFrame(columns=["barcode", "name", "price", "stock"])
        df.to_csv(path, index=False)

    def _import_products(self) -> None:
        path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "Importar productos", "", "CSV (*.csv);;Excel (*.xlsx)"
        )
        if not path:
            return
        if path.lower().endswith(".xlsx"):
            df = pd.read_excel(path)
        else:
            df = pd.read_csv(path)

        required = {"barcode", "name", "price", "stock"}
        if not required.issubset(set(df.columns)):
            QtWidgets.QMessageBox.warning(
                self, "Formato", "La plantilla debe tener columnas: barcode, name, price, stock"
            )
            return

        for _, row in df.iterrows():
            barcode = str(row["barcode"]).strip()
            name = str(row["name"]).strip()
            price = float(row["price"])
            stock = float(row["stock"])
            if not barcode or not name:
                continue
            existing = get_product_by_barcode(barcode)
            if existing is None:
                add_product(barcode, name, price, stock)
            else:
                update_product(int(existing["id"]), barcode, name, price, stock)

        self.inventory_widget.refresh_list()

    def _export_products(self) -> None:
        path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self, "Exportar productos", "", "CSV (*.csv);;Excel (*.xlsx)"
        )
        if not path:
            return
        rows = list_products()
        data = [
            {
                "barcode": row["barcode"],
                "name": row["name"],
                "price": float(row["price"]),
                "stock": float(row["stock"]),
            }
            for row in rows
        ]
        df = pd.DataFrame(data)
        if path.lower().endswith(".xlsx"):
            df.to_excel(path, index=False)
        else:
            df.to_csv(path, index=False)

    def switch_page(self, name: str) -> None:
        widget = self.pages[name]
        self.stack.setCurrentWidget(widget)
        for button_name, button in self.nav_buttons.items():
            button.setChecked(button_name == name)

    def _apply_dashboard_style(self) -> None:
        self.setStyleSheet(
            """
            * { font-size: 12pt; }
            QMainWindow { background: #f2f4f8; }
            QLabel { color: #111827; }
            #sidebar { background: #1f2937; border-right: 1px solid #111827; }
            #sidebarTitle { color: #ffffff; font-weight: 700; font-size: 16pt; }
            #sidebar QPushButton {
                text-align: left; padding: 12px 14px; border-radius: 10px;
                color: #e5e7eb; background: transparent; font-weight: 600;
            }
            #sidebar QPushButton:hover { background: #374151; }
            #sidebar QPushButton:checked { background: #2563eb; color: #ffffff; }
            QTableWidget { background: #ffffff; border: 1px solid #e5e7eb; color: #111827; }
            QTableWidget::item { color: #111827; }
            QHeaderView::section { background: #e5e7eb; padding: 6px; color: #111827; }
            QLineEdit, QDoubleSpinBox {
                padding: 8px; border: 1px solid #d1d5db; border-radius: 6px;
                background: #ffffff;
            }
            QAbstractSpinBox { color: #111827; }
            QAbstractSpinBox::up-button, QAbstractSpinBox::down-button {
                subcontrol-origin: border; width: 18px;
                background: #e5e7eb; border-left: 1px solid #d1d5db;
            }
            QAbstractSpinBox::up-arrow, QAbstractSpinBox::down-arrow {
                width: 8px; height: 8px; color: #111827;
            }
            QPushButton {
                padding: 10px 14px; border-radius: 10px; border: none;
                background: #2563eb; color: white; font-weight: 600;
            }
            QPushButton:hover { background: #1d4ed8; }
            QPushButton:disabled { background: #9ca3af; }
            QPushButton#tileButton {
                background: #ffffff; color: #111827; border: 1px solid #d1d5db;
                font-weight: 600; text-align: center;
            }
            QPushButton#tileButton:hover { background: #e5e7eb; }
            """
        )


def main() -> None:
    init_db()
    seed_sample_data()
    ensure_default_user()
    if not get_setting("currency_symbol", ""):
        set_setting("currency_symbol", "$")
    if not get_setting("ticket_footer", ""):
        set_setting("ticket_footer", "Gracias por su compra")

    app = QtWidgets.QApplication(sys.argv)
    app.setStyleSheet(
        """
        QDialog { background-color: #f5f7fb; }
        QDialog QLabel { color: #111827; }
        QDialog QLineEdit, QDialog QDoubleSpinBox, QDialog QComboBox,
        QDialog QDateEdit, QDialog QSpinBox, QDialog QAbstractSpinBox {
            padding: 8px; border: 1px solid #d1d5db; border-radius: 6px;
            background: #ffffff; color: #111827;
        }
        QDialog QComboBox QAbstractItemView {
            background: #ffffff; color: #111827; selection-background-color: #e5e7eb;
        }
        QDialog QCalendarWidget QWidget {
            background: #ffffff; color: #111827;
        }
        QDialog QCalendarWidget QToolButton {
            color: #111827; background: #e5e7eb; border-radius: 6px; padding: 6px;
        }
        QDialog QCalendarWidget QMenu {
            background: #ffffff; color: #111827;
        }
        QDialog QPushButton {
            padding: 10px 14px; border-radius: 10px; border: none;
            background: #2563eb; color: white; font-weight: 600;
        }
        QDialog QPushButton:hover { background: #1d4ed8; }
        """
    )
    login = LoginDialog()
    if login.exec() != QtWidgets.QDialog.Accepted:
        return
    window = DashboardWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
