from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem,
    QPushButton, QHBoxLayout, QDialog, QFormLayout, QLineEdit, QComboBox, QTextEdit,
    QMessageBox, QFileDialog, QCheckBox, QDialogButtonBox
)
from PyQt5.QtCore import Qt
import csv
from i18n import tr, register_page
from data import save_all_data, customer_data, order_data


# ========== 辅助函数 ==========
def generate_new_customer_id():
    if not customer_data:
        return 1
    return max(int(c.get("id", 0)) for c in customer_data) + 1

def find_customer_by_id(cid):
    for i, c in enumerate(customer_data):
        if str(c.get("id")) == str(cid):
            return i, c
    return None


# ========== 新增/编辑客户对话框 ==========
class AddCustomerDialog(QDialog):
    def __init__(self, parent=None, data=None):
        super().__init__(parent)
        self.setWindowTitle(tr("add_customer"))
        self.setFixedSize(400, 350)
        layout = QFormLayout(self)

        self.name = QLineEdit()
        layout.addRow(tr("name"), self.name)

        self.phone = QLineEdit()
        layout.addRow(tr("phone"), self.phone)

        self.is_corporate = QCheckBox(tr("is_corporate"))
        layout.addRow(self.is_corporate)

        self.status = QComboBox()
        self.status.addItems([tr("normal"), tr("vip"), tr("blacklist")])
        layout.addRow(tr("status"), self.status)

        self.remark = QTextEdit()
        layout.addRow(tr("remark"), self.remark)

        btn_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        layout.addRow(btn_box)
        btn_box.accepted.connect(self.accept)
        btn_box.rejected.connect(self.reject)

        self.customer_id = None
        if data:
            self.customer_id = data.get("id")
            self.name.setText(data["name"])
            self.phone.setText(data["phone"])
            self.is_corporate.setChecked(data["is_corporate"])
            self.status.setCurrentText(tr(data["status"]))
            self.remark.setPlainText(data["remark"])

    def get_data(self):
        return {
            "id": self.customer_id,
            "name": self.name.text(),
            "phone": self.phone.text(),
            "is_corporate": self.is_corporate.isChecked(),
            "status": self.status.currentText(),
            "remark": self.remark.toPlainText(),
        }


# ========== 历史订单对话框 ==========
class OrderHistoryDialog(QDialog):
    def __init__(self, customer_name, parent=None):
        super().__init__(parent)
        self.setWindowTitle(tr("order_history") + f" - {customer_name}")
        self.setFixedSize(600, 300)
        layout = QVBoxLayout(self)
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            tr("order_id"), tr("vehicle_plate"), tr("start_date"), tr("end_date"), tr("total_amount")
        ])
        orders = [o for o in order_data if o["customer"] == customer_name]
        self.table.setRowCount(len(orders))
        for i, o in enumerate(orders):
            self.table.setItem(i, 0, QTableWidgetItem(str(o.get("id", i+1))))
            self.table.setItem(i, 1, QTableWidgetItem(o.get("vehicle", "")))
            self.table.setItem(i, 2, QTableWidgetItem(o.get("start_date", "")))
            self.table.setItem(i, 3, QTableWidgetItem(o.get("end_date", "")))
            self.table.setItem(i, 4, QTableWidgetItem(o.get("amount", "")))
        layout.addWidget(self.table)
        btn = QPushButton(tr("ok"))
        btn.clicked.connect(self.accept)
        layout.addWidget(btn)


# ========== 客户主页面 ==========
class CustomerPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.page_size = 10
        self.current_page = 1
        self.search_text = ""
        self.sort_reverse = False

        layout = QVBoxLayout(self)
        self.title = QLabel(tr("customer_manage"))
        self.title.setStyleSheet("font-size: 22px; font-weight: bold;")
        layout.addWidget(self.title)

        # 搜索栏
        search_layout = QHBoxLayout()
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText(tr("search_customer_placeholder"))
        search_btn = QPushButton(tr("search"))
        self.search_btn = search_btn
        search_btn.clicked.connect(self.do_search)
        search_layout.addWidget(self.search_edit)
        search_layout.addWidget(search_btn)
        search_layout.addStretch()
        layout.addLayout(search_layout)

        # 按钮
        btn_layout = QHBoxLayout()
        self.btn_add = QPushButton(tr("add_customer"))
        self.btn_delete = QPushButton(tr("delete_customer"))
        self.btn_export = QPushButton(tr("export_csv"))
        btn_layout.addWidget(self.btn_add)
        btn_layout.addWidget(self.btn_delete)
        btn_layout.addWidget(self.btn_export)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        # 表格
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            tr("customer_id"), tr("name"), tr("phone"), tr("is_corporate"),
            tr("status"), tr("remark"), tr("order_history")
        ])
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSortingEnabled(False)
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

        # 信号连接
        self.btn_add.clicked.connect(self.add_customer)
        self.btn_delete.clicked.connect(self.delete_customer)
        self.btn_export.clicked.connect(self.export_csv)
        self.table.cellDoubleClicked.connect(self.edit_or_history)
        self.btn_prev.clicked.connect(self.prev_page)
        self.btn_next.clicked.connect(self.next_page)
        self.table.horizontalHeader().sectionClicked.connect(self.sort_by_column)

        register_page(self)
        self.refresh_table()

    # ===== 多语言刷新 =====
    def refresh_texts(self):
        self.title.setText(tr("customer_manage"))
        self.btn_add.setText(tr("add_customer"))
        self.btn_delete.setText(tr("delete_customer"))
        self.btn_export.setText(tr("export_csv"))
        self.btn_prev.setText(tr("prev_page"))
        self.btn_next.setText(tr("next_page"))
        self.search_edit.setPlaceholderText(tr("search_customer_placeholder"))
        self.search_btn.setText(tr("search"))
        self.table.setHorizontalHeaderLabels([
            tr("customer_id"), tr("name"), tr("phone"), tr("is_corporate"),
            tr("status"), tr("remark"), tr("order_history")
        ])
        self.refresh_table()

    # ===== 排序逻辑 =====
    def sort_by_column(self, column):
        self.sort_reverse = not getattr(self, "sort_reverse", False)
        col_map = {0:"id",1:"name",2:"phone",3:"is_corporate",4:"status",5:"remark"}
        key = col_map.get(column)
        if not key: return

        def sort_key(x):
            val = x.get(key, "")
            if isinstance(val, bool): return str(val)
            if isinstance(val, str) and val.isdigit(): return int(val)
            return str(val).lower()

        customer_data.sort(key=sort_key, reverse=self.sort_reverse)
        self.refresh_table()

    # ===== 搜索 + 刷新表格 =====
    def do_search(self):
        self.search_text = self.search_edit.text().strip()
        self.current_page=1; self.refresh_table()

    def get_filtered_data(self):
        if not self.search_text: return customer_data
        return [c for c in customer_data if self.search_text.lower() in c["name"].lower() or self.search_text in c["phone"]]

    def get_selected_customer(self,row):
        item=self.table.item(row,0)
        if not item:return None
        return find_customer_by_id(item.text())

    def refresh_table(self):
        filtered=self.get_filtered_data()
        total=len(filtered); total_pages=max(1,(total+self.page_size-1)//self.page_size)
        self.current_page=min(self.current_page,total_pages)
        start=(self.current_page-1)*self.page_size; end=min(start+self.page_size,total)
        page_data=filtered[start:end]

        self.table.setRowCount(len(page_data))
        for row,c in enumerate(page_data):
            self.table.setItem(row,0,QTableWidgetItem(str(c.get("id",""))))
            self.table.setItem(row,1,QTableWidgetItem(c["name"]))
            self.table.setItem(row,2,QTableWidgetItem(c["phone"]))
            self.table.setItem(row,3,QTableWidgetItem(tr("yes") if c["is_corporate"] else tr("no")))
            self.table.setItem(row,4,QTableWidgetItem(tr(c["status"])))
            self.table.setItem(row,5,QTableWidgetItem(c["remark"]))
            btn=QPushButton(tr("view_history"))
            btn.clicked.connect(lambda _,n=c["name"]:self.show_history(n))
            self.table.setCellWidget(row,6,btn)

        self.lbl_page.setText(tr("page_info").format(self.current_page,total_pages,total))
        self.btn_prev.setEnabled(self.current_page>1)
        self.btn_next.setEnabled(self.current_page<total_pages)

    # ===== CRUD =====
    def add_customer(self):
        dialog=AddCustomerDialog(self)
        if dialog.exec_():
            data=dialog.get_data()
            if not data["name"] or not data["phone"]:
                QMessageBox.warning(self,tr("tip"),tr("name_phone_required"));return
            if not data["phone"].isdigit()or len(data["phone"])<6:
                QMessageBox.warning(self,tr("tip"),tr("phone_invalid"));return
            if any(c["phone"]==data["phone"] for c in customer_data):
                QMessageBox.warning(self,tr("tip"),tr("phone_exists"));return
            for k in ["normal","vip","blacklist"]:
                if data["status"]==tr(k): data["status"]=k
            data["id"]=generate_new_customer_id()
            customer_data.append(data); save_all_data(); self.refresh_table()

    def delete_customer(self):
        row=self.table.currentRow()
        if row==-1:
            QMessageBox.warning(self,tr("tip"),tr("select_customer"));return
        result=self.get_selected_customer(row)
        if not result:return
        idx,customer=result
        reply=QMessageBox.question(self,tr("delete_customer"),tr("confirm_delete_customer").format(customer["name"]),QMessageBox.Yes|QMessageBox.No)
        if reply==QMessageBox.Yes:
            del customer_data[idx]; save_all_data(); self.refresh_table()

    def edit_or_history(self,row,column):
        if column==6:
            name=self.table.item(row,1).text()
            self.show_history(name)
        else:
            result=self.get_selected_customer(row)
            if not result:return
            idx,data=result
            dialog=AddCustomerDialog(self,data)
            if dialog.exec_():
                new_data=dialog.get_data()
                if not new_data["name"] or not new_data["phone"]:
                    QMessageBox.warning(self,tr("tip"),tr("name_phone_required"));return
                if not new_data["phone"].isdigit()or len(new_data["phone"])<6:
                    QMessageBox.warning(self,tr("tip"),tr("phone_invalid"));return
                if any(c["phone"]==new_data["phone"] and c is not data for c in customer_data):
                    QMessageBox.warning(self,tr("tip"),tr("phone_exists"));return
                for k in ["normal","vip","blacklist"]:
                    if new_data["status"]==tr(k): new_data["status"]=k
                new_data["id"]=data["id"]
                customer_data[idx]=new_data; save_all_data(); self.refresh_table()

    def show_history(self,customer_name):
        dlg=OrderHistoryDialog(customer_name,self)
        dlg.exec_()

    # ===== 分页 & 导出 =====
    def prev_page(self):
        if self.current_page>1:self.current_page-=1; self.refresh_table()
    def next_page(self):
        total=len(self.get_filtered_data()); total_pages=max(1,(total+self.page_size-1)//self.page_size)
        if self.current_page<total_pages:self.current_page+=1; self.refresh_table()

    def export_csv(self):
        path,_=QFileDialog.getSaveFileName(self,tr("export_csv"),"客户列表.csv","CSV Files (*.csv)")
        if not path:return
        try:
            with open(path,"w",newline='',encoding="utf-8-sig") as f:
                writer=csv.writer(f)
                writer.writerow([tr("customer_id"),tr("name"),tr("phone"),tr("is_corporate"),tr("status"),tr("remark")])
                for c in self.get_filtered_data():
                    writer.writerow([c["id"],c["name"],c["phone"],tr("yes") if c["is_corporate"] else tr("no"),tr(c["status"]),c["remark"]])
            QMessageBox.information(self,tr("export_csv"),tr("export_success"))
        except Exception as e:
            QMessageBox.critical(self,tr("export_csv"),tr("export_failed")+"\n"+str(e))