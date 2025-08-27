from data import save_all_data, vehicle_data, customer_data, fine_data
from PyQt5.QtCore import QUrl, QDate, Qt
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem,
    QPushButton, QHBoxLayout, QDialog, QFormLayout, QLineEdit, QDateEdit, QTextEdit,
    QMessageBox, QFileDialog, QCheckBox, QStackedWidget, QComboBox
)
from PyQt5.QtGui import QColor, QBrush
import csv
from i18n import tr, register_page

try:
    from PyQt5.QtWebEngineWidgets import QWebEngineView
    webengine_available = True
except ImportError:
    webengine_available = False


# ========== 新增/编辑罚款对话框 ==========
class AddFineDialog(QDialog):
    def __init__(self, parent=None, data=None):
        super().__init__(parent)
        self.setWindowTitle(tr("add_fine"))
        self.setFixedSize(400, 400)
        layout = QFormLayout(self)

        self.vehicle = QComboBox()
        self.vehicle.addItems([v["plate"] for v in vehicle_data])
        layout.addRow(tr("vehicle_plate"), self.vehicle)

        self.customer = QComboBox()
        self.customer.addItems([c["name"] for c in customer_data])
        layout.addRow(tr("customer_name"), self.customer)

        self.fine_type = QLineEdit()
        layout.addRow(tr("fine_type"), self.fine_type)

        self.amount = QLineEdit()
        layout.addRow(tr("fine_amount"), self.amount)

        self.fine_date = QDateEdit()
        self.fine_date.setCalendarPopup(True)
        self.fine_date.setDate(QDate.currentDate())
        layout.addRow(tr("fine_date"), self.fine_date)

        self.paid = QCheckBox(tr("fine_paid"))
        layout.addRow(self.paid)

        self.remark = QTextEdit()
        layout.addRow(tr("remark"), self.remark)

        btn_layout = QHBoxLayout()
        self.btn_ok = QPushButton(tr("ok"))
        self.btn_cancel = QPushButton(tr("cancel"))
        btn_layout.addWidget(self.btn_ok)
        btn_layout.addWidget(self.btn_cancel)
        layout.addRow(btn_layout)
        self.btn_ok.clicked.connect(self.accept)
        self.btn_cancel.clicked.connect(self.reject)

        self.fid = None
        if data:
            self.fid = data.get("id")
            self.vehicle.setCurrentText(data["vehicle"])
            self.customer.setCurrentText(data["customer"])
            self.fine_type.setText(data["fine_type"])
            self.amount.setText(data["amount"])
            self.fine_date.setDate(QDate.fromString(data["fine_date"], "yyyy-MM-dd"))
            self.paid.setChecked(data["paid"])
            self.remark.setPlainText(data["remark"])

    def get_data(self):
        return {
            "id": self.fid,
            "vehicle": self.vehicle.currentText(),
            "customer": self.customer.currentText(),
            "fine_type": self.fine_type.text(),
            "amount": self.amount.text(),
            "fine_date": self.fine_date.date().toString("yyyy-MM-dd"),
            "paid": self.paid.isChecked(),
            "remark": self.remark.toPlainText(),
        }


# ========== 主页面 ==========
class FinePage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.page_size = 10
        self.current_page = 1
        self.search_text = ""
        self.sort_reverse = False

        layout = QVBoxLayout(self)
        self.title = QLabel(tr("fine_manage"))
        self.title.setStyleSheet("font-size: 22px; font-weight: bold;")
        layout.addWidget(self.title)

        # 切换 本地 / 官网
        switch_layout = QHBoxLayout()
        self.btn_local = QPushButton(tr("local_fine_record"))
        self.btn_official = QPushButton(tr("official_fine_query"))
        self.btn_local.setCheckable(True)
        self.btn_official.setCheckable(True)
        self.btn_local.setChecked(True)
        switch_layout.addWidget(self.btn_local)
        switch_layout.addWidget(self.btn_official)
        switch_layout.addStretch()
        layout.addLayout(switch_layout)

        self.stacked = QStackedWidget()
        layout.addWidget(self.stacked)

        # 本地罚款记录页
        self.local_widget = QWidget()
        local_layout = QVBoxLayout(self.local_widget)

        # 搜索栏
        search_layout = QHBoxLayout()
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText(tr("search_fine_placeholder"))
        search_btn = QPushButton(tr("search"))
        self.search_btn = search_btn
        search_btn.clicked.connect(self.do_search)
        search_layout.addWidget(self.search_edit)
        search_layout.addWidget(search_btn)
        search_layout.addStretch()
        local_layout.addLayout(search_layout)

        # 按钮
        btn_layout = QHBoxLayout()
        self.btn_add = QPushButton(tr("add_fine"))
        self.btn_delete = QPushButton(tr("delete_fine"))
        self.btn_export = QPushButton(tr("export_csv"))
        btn_layout.addWidget(self.btn_add)
        btn_layout.addWidget(self.btn_delete)
        btn_layout.addWidget(self.btn_export)
        btn_layout.addStretch()
        local_layout.addLayout(btn_layout)

        # 表格
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            tr("fine_id"), tr("vehicle_plate"), tr("customer_name"), tr("fine_type"),
            tr("fine_amount"), tr("fine_date"), tr("fine_paid"), tr("remark")
        ])
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSortingEnabled(False)
        local_layout.addWidget(self.table)

        # 分页控件
        page_layout = QHBoxLayout()
        self.btn_prev = QPushButton(tr("prev_page"))
        self.btn_next = QPushButton(tr("next_page"))
        self.lbl_page = QLabel()
        page_layout.addStretch()
        page_layout.addWidget(self.btn_prev)
        page_layout.addWidget(self.lbl_page)
        page_layout.addWidget(self.btn_next)
        page_layout.addStretch()
        local_layout.addLayout(page_layout)

        self.btn_add.clicked.connect(self.add_fine)
        self.btn_delete.clicked.connect(self.delete_fine)
        self.btn_export.clicked.connect(self.export_csv)
        self.table.cellDoubleClicked.connect(self.edit_fine)
        self.btn_prev.clicked.connect(self.prev_page)
        self.btn_next.clicked.connect(self.next_page)

        self.stacked.addWidget(self.local_widget)

        # 官网页
        if webengine_available:
            self.web_widget = QWidget()
            web_layout = QVBoxLayout(self.web_widget)
            self.web = QWebEngineView()
            self.web.load(QUrl("https://traffic.rta.ae/trfesrv/public_resources/revamp/common/public_request_service_info.do?entityId=-1&serviceCode=301"))
            web_layout.addWidget(self.web)
            self.stacked.addWidget(self.web_widget)
        else:
            no_web = QWidget()
            no_layout = QVBoxLayout(no_web)
            no_layout.addWidget(QLabel(tr("webengine_not_available")))
            self.stacked.addWidget(no_web)

        self.btn_local.clicked.connect(self.show_local)
        self.btn_official.clicked.connect(self.show_official)
        self.table.horizontalHeader().sectionClicked.connect(self.sort_by_column)

        register_page(self)
        self.refresh_table()

    # ===== 多语言刷新 =====
    def refresh_texts(self):
        self.title.setText(tr("fine_manage"))
        self.btn_local.setText(tr("local_fine_record"))
        self.btn_official.setText(tr("official_fine_query"))
        self.btn_add.setText(tr("add_fine"))
        self.btn_delete.setText(tr("delete_fine"))
        self.btn_export.setText(tr("export_csv"))
        self.btn_prev.setText(tr("prev_page"))
        self.btn_next.setText(tr("next_page"))
        self.search_edit.setPlaceholderText(tr("search_fine_placeholder"))
        self.search_btn.setText(tr("search"))
        self.table.setHorizontalHeaderLabels([
            tr("fine_id"), tr("vehicle_plate"), tr("customer_name"), tr("fine_type"),
            tr("fine_amount"), tr("fine_date"), tr("fine_paid"), tr("remark")
        ])
        self.refresh_table()

    # ===== 排序逻辑 =====
    def sort_by_column(self, column):
        self.sort_reverse = not getattr(self, "sort_reverse", False)
        col_map = {0:"id",1:"vehicle",2:"customer",3:"fine_type",4:"amount",5:"fine_date",6:"paid",7:"remark"}
        key = col_map.get(column)
        if not key: return
        def sort_key(x):
            val=x.get(key,"")
            if isinstance(val,(int,float,bool)): return val
            if isinstance(val,str) and val.replace(".","",1).isdigit(): return float(val)
            return str(val).lower()
        fine_data.sort(key=sort_key, reverse=self.sort_reverse)
        self.refresh_table()

    # ===== 逻辑 =====
    def show_local(self): self.stacked.setCurrentIndex(0)
    def show_official(self): self.stacked.setCurrentIndex(1)

    def do_search(self):
        self.search_text=self.search_edit.text().strip(); self.current_page=1; self.refresh_table()

    def get_filtered_data(self):
        if not self.search_text: return fine_data
        return [f for f in fine_data if self.search_text.lower() in f["vehicle"].lower()
                or self.search_text.lower() in f["customer"].lower()
                or self.search_text.lower() in f["fine_type"].lower()]

    def refresh_table(self):
        filtered=self.get_filtered_data()
        total=len(filtered); total_pages=max(1,(total+self.page_size-1)//self.page_size)
        self.current_page=min(self.current_page,total_pages)
        start=(self.current_page-1)*self.page_size; end=min(start+self.page_size,total)
        page_data=filtered[start:end]
        self.table.setRowCount(len(page_data))
        for row,f in enumerate(page_data):
            self.table.setItem(row,0,QTableWidgetItem(str(f.get("id",row+1))))
            self.table.setItem(row,1,QTableWidgetItem(f["vehicle"]))
            self.table.setItem(row,2,QTableWidgetItem(f["customer"]))
            self.table.setItem(row,3,QTableWidgetItem(f["fine_type"]))
            self.table.setItem(row,4,QTableWidgetItem(f["amount"]))
            self.table.setItem(row,5,QTableWidgetItem(f["fine_date"]))
            paid_item=QTableWidgetItem(tr("yes") if f["paid"] else tr("no"))
            if not f["paid"]:
                paid_item.setBackground(QBrush(QColor("#ff4d4f"))); paid_item.setForeground(QBrush(QColor("#ffffff")))
            self.table.setItem(row,6,paid_item)
            self.table.setItem(row,7,QTableWidgetItem(f["remark"]))
        self.lbl_page.setText(tr("page_info").format(self.current_page,total_pages,total))
        self.btn_prev.setEnabled(self.current_page>1)
        self.btn_next.setEnabled(self.current_page<total_pages)

    # ===== CRUD =====
    def add_fine(self):
        if not customer_data or not vehicle_data:
            QMessageBox.warning(self,tr("tip"),tr("add_customer_vehicle_first")); return
        dialog=AddFineDialog(self)
        if dialog.exec_():
            data=dialog.get_data()
            if not data["vehicle"] or not data["customer"] or not data["fine_type"]:
                QMessageBox.warning(self,tr("tip"),tr("fine_required")); return
            if not data["amount"].replace(".","",1).isdigit():
                QMessageBox.warning(self,tr("tip"),tr("amount_invalid")); return
            data["id"]=max([f.get("id",0) for f in fine_data],default=0)+1
            fine_data.append(data); save_all_data(); self.refresh_table()

    def delete_fine(self):
        row=self.table.currentRow()
        if row==-1:
            QMessageBox.warning(self,tr("tip"),tr("select_fine")); return
        filtered=self.get_filtered_data()
        target=filtered[(self.current_page-1)*self.page_size+row]
        fine_id=target.get("id",row+1)
        reply=QMessageBox.question(self,tr("delete_fine"),tr("confirm_delete_fine").format(fine_id),QMessageBox.Yes|QMessageBox.No)
        if reply==QMessageBox.Yes:
            fine_data.remove(target); save_all_data(); self.refresh_table()

    def edit_fine(self,row,column):
        filtered=self.get_filtered_data()
        target=filtered[(self.current_page-1)*self.page_size+row]
        dialog=AddFineDialog(self,target)
        if dialog.exec_():
            new_data=dialog.get_data()
            if not new_data["vehicle"] or not new_data["customer"] or not new_data["fine_type"]:
                QMessageBox.warning(self,tr("tip"),tr("fine_required")); return
            if not new_data["amount"].replace(".","",1).isdigit():
                QMessageBox.warning(self,tr("tip"),tr("amount_invalid")); return
            new_data["id"]=target.get("id")
            idx=fine_data.index(target)
            fine_data[idx]=new_data; save_all_data(); self.refresh_table()

    # ===== 分页 & 导出 =====
    def prev_page(self):
        if self.current_page>1:self.current_page-=1; self.refresh_table()
    def next_page(self):
        total=len(self.get_filtered_data()); total_pages=max(1,(total+self.page_size-1)//self.page_size)
        if self.current_page<total_pages:self.current_page+=1; self.refresh_table()
    def export_csv(self):
        path,_=QFileDialog.getSaveFileName(self,tr("export_csv"),"罚款记录.csv","CSV Files (*.csv)")
        if not path:return
        try:
            with open(path,"w",newline='',encoding="utf-8-sig")as f:
                writer=csv.writer(f)
                writer.writerow([tr("fine_id"),tr("vehicle_plate"),tr("customer_name"),tr("fine_type"),
                                 tr("fine_amount"),tr("fine_date"),tr("fine_paid"),tr("remark")])
                for f_item in self.get_filtered_data():
                    writer.writerow([f_item.get("id"),f_item["vehicle"],f_item["customer"],f_item["fine_type"],
                                     f_item["amount"],f_item["fine_date"],tr("yes") if f_item["paid"] else tr("no"),f_item["remark"]])
            QMessageBox.information(self,tr("export_csv"),tr("export_success"))
        except Exception as e:
            QMessageBox.critical(self,tr("export_csv"),tr("export_failed")+"\n"+str(e))