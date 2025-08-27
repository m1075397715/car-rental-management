from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem,
    QPushButton, QHBoxLayout, QDialog, QFormLayout, QLineEdit, QComboBox,
    QDateEdit, QTextEdit, QMessageBox, QFileDialog
)
from PyQt5.QtCore import QDate, Qt, QTimer
from PyQt5.QtGui import QBrush, QColor
import csv

from data import save_all_data, vehicle_data, customer_data, order_data
from i18n import tr, register_page
from add_order_dialog import AddOrderDialog


# ========== 辅助 ==========
def generate_new_order_id():
    if not order_data:
        return 1001
    return max(int(o.get("id", 0)) for o in order_data) + 1

def find_order_by_id(order_id):
    for i, o in enumerate(order_data):
        if str(o.get("id")) == str(order_id):
            return i, o
    return None


# ========== 主页面 ==========
class OrderPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.page_size = 10
        self.current_page = 1
        self.search_text = ""
        self.flash_on = True
        self.sort_reverse = False

        layout = QVBoxLayout(self)
        self.title = QLabel(tr("order_manage"))
        self.title.setStyleSheet("font-size: 22px; font-weight: bold;")
        layout.addWidget(self.title)

        # 到期提醒
        self.remind_label = QLabel()
        self.remind_label.setStyleSheet("color: red; font-weight: bold;")
        layout.addWidget(self.remind_label)

        # 搜索栏
        search_layout = QHBoxLayout()
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText(tr("search_order_placeholder"))
        search_btn = QPushButton(tr("search"))
        self.search_btn = search_btn
        search_btn.clicked.connect(self.do_search)
        search_layout.addWidget(self.search_edit)
        search_layout.addWidget(search_btn)
        search_layout.addStretch()
        layout.addLayout(search_layout)

        # 按钮区
        btn_layout = QHBoxLayout()
        self.btn_add = QPushButton(tr("add_order"))
        self.btn_delete = QPushButton(tr("delete_order"))
        self.btn_export = QPushButton(tr("export_csv"))
        self.btn_renew = QPushButton(tr("renew_order"))
        btn_layout.addWidget(self.btn_add)
        btn_layout.addWidget(self.btn_delete)
        btn_layout.addWidget(self.btn_export)
        btn_layout.addWidget(self.btn_renew)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        # 表格
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            tr("order_id"), tr("customer_name"), tr("vehicle_plate"), tr("start_date"),
            tr("end_date"), tr("order_status"), tr("total_amount"), tr("remark")
        ])
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSortingEnabled(False)
        self.table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.table)

        # 分页
        page_layout = QHBoxLayout()
        self.btn_prev = QPushButton(tr("prev_page"))
        self.btn_next = QPushButton(tr("next_page"))
        self.lbl_page = QLabel()
        page_layout.addStretch()
        page_layout.addWidget(self.btn_prev)
        page_layout.addWidget(self.lbl_page)
        page_layout.addWidget(self.btn_next)
        page_layout.addStretch()
        layout.addLayout(page_layout)

        # 信号绑定
        self.btn_add.clicked.connect(self.add_order)
        self.btn_delete.clicked.connect(self.delete_order)
        self.btn_export.clicked.connect(self.export_csv)
        self.btn_renew.clicked.connect(self.renew_order)
        self.table.cellDoubleClicked.connect(self.edit_order)
        self.btn_prev.clicked.connect(self.prev_page)
        self.btn_next.clicked.connect(self.next_page)
        self.table.horizontalHeader().sectionClicked.connect(self.sort_by_column)

        # 闪烁定时器
        self.flash_timer = QTimer(self)
        self.flash_timer.timeout.connect(self.toggle_flash)
        self.flash_timer.start(600)

        register_page(self)
        self.refresh_table()

    # ===== 多语言刷新 =====
    def refresh_texts(self):
        self.title.setText(tr("order_manage"))
        self.btn_add.setText(tr("add_order"))
        self.btn_delete.setText(tr("delete_order"))
        self.btn_export.setText(tr("export_csv"))
        self.btn_renew.setText(tr("renew_order"))
        self.btn_prev.setText(tr("prev_page"))
        self.btn_next.setText(tr("next_page"))
        self.search_edit.setPlaceholderText(tr("search_order_placeholder"))
        self.search_btn.setText(tr("search"))
        self.table.setHorizontalHeaderLabels([
            tr("order_id"), tr("customer_name"), tr("vehicle_plate"), tr("start_date"),
            tr("end_date"), tr("order_status"), tr("total_amount"), tr("remark")
        ])
        self.refresh_table()

    # ===== 排序逻辑 =====
    def sort_by_column(self, column):
        self.sort_reverse = not getattr(self, "sort_reverse", False)
        col_map = {0:"id",1:"customer",2:"vehicle",3:"start_date",4:"end_date",5:"status",6:"amount",7:"remark"}
        key = col_map.get(column)
        if not key: return
        def sort_key(x):
            val = x.get(key, "")
            if isinstance(val, str) and val.replace(".","",1).isdigit():
                try: return float(val)
                except: return val
            return str(val).lower()
        order_data.sort(key=sort_key, reverse=self.sort_reverse)
        self.refresh_table()

    # ===== 表格刷新 =====
    def refresh_table(self):
        today = QDate.currentDate().toString("yyyy-MM-dd")
        expired = [o["id"] for o in order_data if o["end_date"] < today and o["status"] in ["ongoing","overdue"]]
        self.remind_label.setText(tr("order_expired")+" "+"、".join(map(str,expired)) if expired else "")

        filtered = self.get_filtered_data()
        total = len(filtered)
        total_pages = max(1,(total+self.page_size-1)//self.page_size)
        self.current_page = min(self.current_page, total_pages)
        start=(self.current_page-1)*self.page_size; end=min(start+self.page_size,total)
        page_data=filtered[start:end]

        self.table.setRowCount(len(page_data))
        today_qdate = QDate.currentDate()
        for row,o in enumerate(page_data):
            end_qdate=QDate.fromString(o["end_date"],"yyyy-MM-dd")
            days_to_end=today_qdate.daysTo(end_qdate)
            is_expired=end_qdate.isValid() and end_qdate<today_qdate and o["status"] in ["ongoing","overdue"]
            is_soon=end_qdate.isValid() and 0<=days_to_end<=3 and o["status"] in ["ongoing","overdue"]
            values=[str(o["id"]),o["customer"],o["vehicle"],o["start_date"],o["end_date"],tr(o["status"]),o["amount"],o["remark"]]
            for col,val in enumerate(values):
                item=QTableWidgetItem(val)
                if col==4:
                    if is_expired:
                        if self.flash_on:
                            item.setBackground(QBrush(QColor("#ff4d4f"))); item.setForeground(QBrush(QColor("#ffffff")))
                        else:
                            item.setBackground(QBrush(QColor("#ffffff"))); item.setForeground(QBrush(QColor("#ff4d4f")))
                    elif is_soon:
                        item.setBackground(QBrush(QColor("#fff566"))); item.setForeground(QBrush(QColor("#000000")))
                if o["status"]=="ongoing":
                    item.setBackground(QBrush(QColor("#d4f4dd")))
                elif o["status"]=="overdue":
                    item.setBackground(QBrush(QColor("#ffccc7")))
                elif o["status"]=="cancelled":
                    item.setBackground(QBrush(QColor("#d9d9d9"))); item.setForeground(QBrush(QColor("#888888")))
                self.table.setItem(row,col,item)
        self.lbl_page.setText(tr("page_info").format(self.current_page,total_pages,total))
        self.btn_prev.setEnabled(self.current_page>1)
        self.btn_next.setEnabled(self.current_page<total_pages)

    # ===== 基础逻辑 =====
    def toggle_flash(self):
        self.flash_on=not self.flash_on; self.refresh_table()

    def do_search(self):
        self.search_text=self.search_edit.text().strip(); self.current_page=1; self.refresh_table()

    def get_filtered_data(self):
        if not self.search_text: return order_data
        return [o for o in order_data if self.search_text.lower() in o["customer"].lower() 
                or self.search_text.lower() in o["vehicle"].lower()
                or self.search_text.lower() in o["status"].lower()]

    def get_selected_order(self,row):
        item=self.table.item(row,0)
        if not item:return None
        return find_order_by_id(item.text())

    # ===== CRUD =====
    def add_order(self):
        if not customer_data or not vehicle_data:
            QMessageBox.warning(self,tr("tip"),tr("add_customer_vehicle_first"));return
        dialog=AddOrderDialog(self)
        if dialog.exec_():
            data=dialog.get_data()
            if not data["customer"] or not data["vehicle"]:
                QMessageBox.warning(self,tr("tip"),tr("customer_vehicle_required"));return
            if data["start_date"] > data["end_date"]:
                QMessageBox.warning(self,tr("tip"),tr("date_invalid"));return
            try: float(data["amount"])
            except ValueError:
                QMessageBox.warning(self,tr("tip"),tr("amount_invalid"));return
            for k in ["ongoing","completed","overdue","cancelled"]:
                if data["status"]==tr(k): data["status"]=k
            data["id"]=generate_new_order_id()
            order_data.append(data); save_all_data(); self.refresh_table()

    def delete_order(self):
        row=self.table.currentRow()
        if row==-1: QMessageBox.warning(self,tr("tip"),tr("select_order")); return
        result=self.get_selected_order(row)
        if not result:return
        idx,order=result
        reply=QMessageBox.question(self,tr("delete_order"),tr("confirm_delete_order").format(order["id"]),QMessageBox.Yes|QMessageBox.No)
        if reply==QMessageBox.Yes: del order_data[idx]; save_all_data(); self.refresh_table()

    def edit_order(self,row,column):
        result=self.get_selected_order(row)
        if not result:return
        idx,order=result
        dialog=AddOrderDialog(self,order)
        if dialog.exec_():
            new_data=dialog.get_data()
            if not new_data["customer"] or not new_data["vehicle"]:
                QMessageBox.warning(self,tr("tip"),tr("customer_vehicle_required"));return
            if new_data["start_date"]>new_data["end_date"]:
                QMessageBox.warning(self,tr("tip"),tr("date_invalid"));return
            try: float(new_data["amount"])
            except ValueError:
                QMessageBox.warning(self,tr("tip"),tr("amount_invalid"));return
            for k in ["ongoing","completed","overdue","cancelled"]:
                if new_data["status"]==tr(k): new_data["status"]=k
            new_data["id"]=order["id"]
            order_data[idx]=new_data; save_all_data(); self.refresh_table()

    def renew_order(self):
        row=self.table.currentRow()
        if row==-1: QMessageBox.warning(self,tr("tip"),tr("select_order")); return
        result=self.get_selected_order(row)
        if not result:return
        idx,order=result
        dialog=QDialog(self); dialog.setWindowTitle(tr("renew_order"))
        layout=QFormLayout(dialog)
        new_end=QDateEdit(); new_end.setCalendarPopup(True)
        old_end_qdate=QDate.fromString(order["end_date"],"yyyy-MM-dd")
        new_end.setDate(old_end_qdate); new_end.setMinimumDate(old_end_qdate.addDays(1))
        layout.addRow(tr("new_end_date"),new_end)
        btn=QPushButton(tr("ok")); btn.clicked.connect(dialog.accept); layout.addWidget(btn)
        if dialog.exec_():
            new_end_date=new_end.date().toString("yyyy-MM-dd")
            if new_end_date<=order["end_date"]:
                QMessageBox.warning(self,tr("tip"),tr("renew_date_error")); return
            order["end_date"]=new_end_date; order["status"]="ongoing"
            save_all_data(); self.refresh_table()

    # ===== 分页 & 导出 =====
    def prev_page(self):
        if self.current_page>1:self.current_page-=1; self.refresh_table()
    def next_page(self):
        total=len(self.get_filtered_data()); total_pages=max(1,(total+self.page_size-1)//self.page_size)
        if self.current_page<total_pages:self.current_page+=1; self.refresh_table()
    def export_csv(self):
        path,_=QFileDialog.getSaveFileName(self,tr("export_csv"),"订单列表.csv","CSV Files (*.csv)")
        if not path:return
        try:
            with open(path,"w",newline='',encoding="utf-8-sig") as f:
                writer=csv.writer(f)
                writer.writerow([tr("order_id"),tr("customer_name"),tr("vehicle_plate"),tr("start_date"),tr("end_date"),tr("order_status"),tr("total_amount"),tr("remark")])
                for o in self.get_filtered_data():
                    writer.writerow([o["id"],o["customer"],o["vehicle"],o["start_date"],o["end_date"],tr(o["status"]),o["amount"],o["remark"]])
            QMessageBox.information(self,tr("export_csv"),tr("export_success"))
        except Exception as e:
            QMessageBox.critical(self,tr("export_csv"),tr("export_failed")+"\n"+str(e))