from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem,
    QPushButton, QHBoxLayout, QDialog, QFormLayout, QLineEdit, QDateEdit, QTextEdit, QMessageBox, QFileDialog
)
from PyQt5.QtCore import QDate
from PyQt5.QtGui import QColor, QBrush
import csv
from i18n import tr, register_page
from data import save_all_data, vehicle_data

# ========== 辅助 ==========
def generate_new_vehicle_id():
    if not vehicle_data:
        return 1
    return max(int(v.get("id", 0)) for v in vehicle_data) + 1

def find_vehicle_by_id(vid):
    for i, v in enumerate(vehicle_data):
        if str(v.get("id")) == str(vid):
            return i, v
    return None

# ========== 新增/编辑对话框 ==========
class AddVehicleDialog(QDialog):
    def __init__(self, parent=None, data=None):
        super().__init__(parent)
        self.setWindowTitle(tr("add_vehicle"))
        self.setFixedSize(400, 400)
        layout = QFormLayout(self)

        self.plate_number = QLineEdit()
        self.plate_number.textChanged.connect(lambda: self.plate_number.setText(self.plate_number.text().upper()))
        layout.addRow(tr("license_plate"), self.plate_number)

        self.model = QLineEdit(); layout.addRow(tr("model"), self.model)
        self.year = QLineEdit(); layout.addRow(tr("year"), self.year)

        self.insurance_date = QDateEdit()
        self.insurance_date.setCalendarPopup(True)
        self.insurance_date.setDate(QDate.currentDate())
        layout.addRow(tr("insurance_expiry"), self.insurance_date)

        self.mileage = QLineEdit(); layout.addRow(tr("mileage"), self.mileage)
        self.monthly_price = QLineEdit(); layout.addRow(tr("monthly_price"), self.monthly_price)
        self.deposit = QLineEdit(); layout.addRow(tr("deposit"), self.deposit)
        self.remark = QTextEdit(); layout.addRow(tr("remark"), self.remark)

        btn_layout = QHBoxLayout()
        self.btn_ok = QPushButton(tr("ok")); self.btn_cancel = QPushButton(tr("cancel"))
        btn_layout.addWidget(self.btn_ok); btn_layout.addWidget(self.btn_cancel)
        layout.addRow(btn_layout)
        self.btn_ok.clicked.connect(self.accept); self.btn_cancel.clicked.connect(self.reject)

        self.vid = None
        if data:
            self.vid = data.get("id")
            self.plate_number.setText(data["plate"])
            self.model.setText(data["model"])
            self.year.setText(data["year"])
            self.insurance_date.setDate(QDate.fromString(data["insurance"], "yyyy-MM-dd"))
            self.mileage.setText(data["mileage"])
            self.monthly_price.setText(data["monthly_price"])
            self.deposit.setText(data["deposit"])
            self.remark.setPlainText(data["remark"])

    def get_data(self):
        return {
            "id": self.vid,
            "plate": self.plate_number.text().upper(),
            "model": self.model.text(),
            "year": self.year.text(),
            "insurance": self.insurance_date.date().toString("yyyy-MM-dd"),
            "mileage": self.mileage.text(),
            "monthly_price": self.monthly_price.text(),
            "deposit": self.deposit.text(),
            "remark": self.remark.toPlainText(),
        }

# ========== 主页面 ==========
class VehiclePage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.page_size = 10
        self.current_page = 1
        self.search_text = ""
        self.sort_reverse = False

        layout = QVBoxLayout(self)
        self.title = QLabel(tr("vehicle_manage"))
        self.title.setStyleSheet("font-size: 22px; font-weight: bold;")
        layout.addWidget(self.title)

        self.remind_label = QLabel()
        self.remind_label.setStyleSheet("color: red; font-weight: bold;")
        layout.addWidget(self.remind_label)

        # 搜索
        search_layout = QHBoxLayout()
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText(tr("search_placeholder"))
        search_btn = QPushButton(tr("search"))
        self.search_btn = search_btn
        search_btn.clicked.connect(self.do_search)
        search_layout.addWidget(self.search_edit)
        search_layout.addWidget(search_btn)
        search_layout.addStretch()
        layout.addLayout(search_layout)

        # 按钮
        btn_layout = QHBoxLayout()
        self.btn_add = QPushButton(tr("add_vehicle"))
        self.btn_delete = QPushButton(tr("delete_vehicle"))
        self.btn_export = QPushButton(tr("export_csv"))
        btn_layout.addWidget(self.btn_add)
        btn_layout.addWidget(self.btn_delete)
        btn_layout.addWidget(self.btn_export)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        # 表格
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            tr("vehicle_id"), tr("license_plate"), tr("model"), tr("year"), 
            tr("insurance_expiry"), tr("mileage"), tr("monthly_price"), tr("deposit")
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
        page_layout.addWidget(self.btn_prev); page_layout.addWidget(self.lbl_page); page_layout.addWidget(self.btn_next)
        page_layout.addStretch()
        layout.addLayout(page_layout)

        # 信号
        self.btn_add.clicked.connect(self.add_vehicle)
        self.btn_delete.clicked.connect(self.delete_vehicle)
        self.btn_export.clicked.connect(self.export_csv)
        self.table.cellDoubleClicked.connect(self.edit_vehicle)
        self.btn_prev.clicked.connect(self.prev_page)
        self.btn_next.clicked.connect(self.next_page)
        self.table.horizontalHeader().sectionClicked.connect(self.sort_by_column)

        register_page(self)
        self.refresh_table()

    # ===== 多语言刷新 =====
    def refresh_texts(self):
        self.title.setText(tr("vehicle_manage"))
        self.btn_add.setText(tr("add_vehicle"))
        self.btn_delete.setText(tr("delete_vehicle"))
        self.btn_export.setText(tr("export_csv"))
        self.btn_prev.setText(tr("prev_page"))
        self.btn_next.setText(tr("next_page"))
        self.search_edit.setPlaceholderText(tr("search_placeholder"))
        self.search_btn.setText(tr("search"))
        self.table.setHorizontalHeaderLabels([
            tr("vehicle_id"), tr("license_plate"), tr("model"), tr("year"), 
            tr("insurance_expiry"), tr("mileage"), tr("monthly_price"), tr("deposit")
        ])
        self.refresh_table()

    # ===== 排序 =====
    def sort_by_column(self, column):
        self.sort_reverse = not getattr(self, "sort_reverse", False)
        col_map = {0:"id",1:"plate",2:"model",3:"year",4:"insurance",5:"mileage",6:"monthly_price",7:"deposit"}
        key = col_map.get(column)
        if not key: return
        def sort_key(x):
            val = x.get(key, "")
            if isinstance(val,str) and val.isdigit(): return int(val)
            return str(val).lower()
        vehicle_data.sort(key=sort_key, reverse=self.sort_reverse)
        self.refresh_table()

    # ===== 搜索 =====
    def do_search(self):
        self.search_text = self.search_edit.text().strip()
        self.current_page=1
        self.refresh_table()

    def get_filtered_data(self):
        if not self.search_text: return vehicle_data
        return [v for v in vehicle_data if self.search_text.lower() in v["plate"].lower() or self.search_text.lower() in v["model"].lower()]

    def get_selected_vehicle(self,row):
        item=self.table.item(row,0)
        if not item:return None
        vid=item.text()
        return find_vehicle_by_id(vid)

    def refresh_table(self):
        today = QDate.currentDate()
        expired = [v["plate"] for v in vehicle_data if QDate.fromString(v["insurance"],"yyyy-MM-dd")<today]
        self.remind_label.setText(tr("insurance_expired")+" "+"、".join(expired) if expired else "")
        filtered=self.get_filtered_data()
        total=len(filtered); total_pages=max(1,(total+self.page_size-1)//self.page_size)
        self.current_page=min(self.current_page,total_pages)
        start=(self.current_page-1)*self.page_size; end=min(start+self.page_size,total)
        page_data=filtered[start:end]
        self.table.setRowCount(len(page_data))
        for row,v in enumerate(page_data):
            values=[str(v.get("id","")),v["plate"],v["model"],v["year"],v["insurance"],v["mileage"],v["monthly_price"],v["deposit"]]
            for col,val in enumerate(values):
                item=QTableWidgetItem(val)
                if col==4:
                    ins_qdate=QDate.fromString(v["insurance"],"yyyy-MM-dd")
                    if ins_qdate<today:
                        item.setBackground(QBrush(QColor("#ff4d4f"))); item.setForeground(QBrush(QColor("#ffffff")))
                self.table.setItem(row,col,item)

        self.lbl_page.setText(tr("page_info").format(self.current_page,total_pages,total))
        self.btn_prev.setEnabled(self.current_page>1)
        self.btn_next.setEnabled(self.current_page<total_pages)

    # ===== CRUD =====
    def add_vehicle(self):
        dialog=AddVehicleDialog(self)
        if dialog.exec_():
            data=dialog.get_data()
            if not data["plate"]or not data["model"]or not data["year"]:
                QMessageBox.warning(self,tr("tip"),tr("plate_required"));return
            if not data["year"].isdigit():
                QMessageBox.warning(self,tr("tip"),tr("year_number"));return
            if any(v["plate"]==data["plate"] for v in vehicle_data):
                QMessageBox.warning(self,tr("tip"),tr("plate_exists"));return
            data["id"]=generate_new_vehicle_id()
            vehicle_data.append(data); save_all_data(); self.refresh_table()

    def delete_vehicle(self):
        row=self.table.currentRow()
        if row==-1:
            QMessageBox.warning(self,tr("tip"),tr("select_vehicle"));return
        result=self.get_selected_vehicle(row)
        if not result:return
        idx,vehicle=result
        reply=QMessageBox.question(self,tr("delete_vehicle"),tr("confirm_delete").format(vehicle["plate"]),QMessageBox.Yes|QMessageBox.No)
        if reply==QMessageBox.Yes:
            del vehicle_data[idx]; save_all_data(); self.refresh_table()

    def edit_vehicle(self,row,column):
        result=self.get_selected_vehicle(row)
        if not result:return
        idx,vehicle=result
        dialog=AddVehicleDialog(self,vehicle)
        if dialog.exec_():
            data=dialog.get_data()
            if not data["plate"]or not data["model"]or not data["year"]:
                QMessageBox.warning(self,tr("tip"),tr("plate_required"));return
            if not data["year"].isdigit():
                QMessageBox.warning(self,tr("tip"),tr("year_number"));return
            if any(v["plate"]==data["plate"] and v is not vehicle for v in vehicle_data):
                QMessageBox.warning(self,tr("tip"),tr("plate_exists"));return
            data["id"]=vehicle["id"]
            vehicle_data[idx]=data; save_all_data(); self.refresh_table()

    def prev_page(self):
        if self.current_page>1:self.current_page-=1; self.refresh_table()
    def next_page(self):
        total=len(self.get_filtered_data()); total_pages=max(1,(total+self.page_size-1)//self.page_size)
        if self.current_page<total_pages:self.current_page+=1; self.refresh_table()

    def export_csv(self):
        path,_=QFileDialog.getSaveFileName(self,tr("export_csv"),"车辆列表.csv","CSV Files (*.csv)")
        if not path:return
        try:
            with open(path,"w",newline='',encoding="utf-8-sig")as f:
                writer=csv.writer(f)
                writer.writerow([tr("vehicle_id"),tr("license_plate"),tr("model"),tr("year"),tr("insurance_expiry"),tr("mileage"),tr("monthly_price"),tr("deposit")])
                for v in self.get_filtered_data():
                    writer.writerow([v.get("id"),v["plate"],v["model"],v["year"],v["insurance"],v["mileage"],v["monthly_price"],v["deposit"]])
            QMessageBox.information(self,tr("export_csv"),tr("export_success"))
        except Exception as e:
            QMessageBox.critical(self,tr("export_csv"),tr("export_failed")+"\n"+str(e))