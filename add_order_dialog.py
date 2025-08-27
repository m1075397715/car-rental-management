# add_order_dialog.py

from PyQt5.QtWidgets import (
    QDialog, QFormLayout, QComboBox, QDateEdit, QLineEdit,
    QTextEdit, QPushButton, QHBoxLayout
)
from PyQt5.QtCore import QDate
from i18n import tr
from data import customer_data, vehicle_data


class AddOrderDialog(QDialog):
    def __init__(self, parent=None, data=None):
        super().__init__(parent)
        self.setWindowTitle(tr("add_order"))
        self.setFixedSize(400, 400)
        layout = QFormLayout(self)

        self.customer = QComboBox()
        self.customer.addItems([c["name"] for c in customer_data])
        layout.addRow(tr("customer_name"), self.customer)

        self.vehicle = QComboBox()
        self.vehicle.addItems([v["plate"] for v in vehicle_data])
        layout.addRow(tr("vehicle_plate"), self.vehicle)

        self.start_date = QDateEdit()
        self.start_date.setCalendarPopup(True)
        self.start_date.setDate(QDate.currentDate())
        layout.addRow(tr("start_date"), self.start_date)

        self.end_date = QDateEdit()
        self.end_date.setCalendarPopup(True)
        self.end_date.setDate(QDate.currentDate().addDays(1))
        layout.addRow(tr("end_date"), self.end_date)

        self.status = QComboBox()
        self.status.addItems([tr("ongoing"), tr("completed"), tr("overdue"), tr("cancelled")])
        layout.addRow(tr("order_status"), self.status)

        self.amount = QLineEdit()
        layout.addRow(tr("total_amount"), self.amount)

        self.remark = QTextEdit()
        layout.addRow(tr("remark"), self.remark)

        # 按钮
        btn_layout = QHBoxLayout()
        self.btn_ok = QPushButton(tr("ok"))
        self.btn_cancel = QPushButton(tr("cancel"))
        btn_layout.addWidget(self.btn_ok)
        btn_layout.addWidget(self.btn_cancel)
        layout.addRow(btn_layout)
        self.btn_ok.clicked.connect(self.accept)
        self.btn_cancel.clicked.connect(self.reject)

        # 如果传入了已有数据（编辑模式）
        if data:
            self.customer.setCurrentText(data["customer"])
            self.vehicle.setCurrentText(data["vehicle"])
            self.start_date.setDate(QDate.fromString(data["start_date"], "yyyy-MM-dd"))
            self.end_date.setDate(QDate.fromString(data["end_date"], "yyyy-MM-dd"))
            self.status.setCurrentText(tr(data["status"]))
            self.amount.setText(data["amount"])
            self.remark.setPlainText(data["remark"])

    def get_data(self):
        return {
            "customer": self.customer.currentText(),
            "vehicle": self.vehicle.currentText(),
            "start_date": self.start_date.date().toString("yyyy-MM-dd"),
            "end_date": self.end_date.date().toString("yyyy-MM-dd"),
            "status": self.status.currentText(),
            "amount": self.amount.text(),
            "remark": self.remark.toPlainText(),
        }