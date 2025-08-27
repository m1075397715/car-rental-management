from data import load_all_data
load_all_data()
import os
import shutil
import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QStackedWidget, QLabel, QMessageBox, QFileDialog
)
from PyQt5.QtCore import Qt, QTimer, QDateTime, QSettings
from PyQt5.QtGui import QFont, QIcon
from i18n import tr, LANG, current_lang

from vehicle_page import VehiclePage
from customer_page import CustomerPage
from order_page import OrderPage
from fine_page import FinePage

import pytz
from datetime import datetime

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()
        # 恢复窗口大小和位置
        settings = QSettings("Ezown", "CarRental")
        geometry = settings.value("geometry")
        if geometry:
            self.restoreGeometry(geometry)
        window_state = settings.value("windowState")
        if window_state:
            self.restoreState(window_state)

    def closeEvent(self, event):
        settings = QSettings("Ezown", "CarRental")
        settings.setValue("geometry", self.saveGeometry())
        settings.setValue("windowState", self.saveState())
        super().closeEvent(event)

    def init_ui(self):
        self.setWindowTitle(tr("title"))
        self.setWindowIcon(QIcon())  # 你可以设置自己的ico
        self.setMinimumSize(1100, 700)
        self.setStyleSheet("""
    QMainWindow {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
            stop:0 #f5f7fa, stop:1 #c3cfe2);
    }
    QWidget#sidebar {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
            stop:0 #232526, stop:1 #414345);
        border-right: 2px solid #e0e0e0;
    }
    QPushButton {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 #43e97b, stop:1 #009975);
        color: white;
        border-radius: 8px;
        font-size: 15px;
        font-family: 'Segoe UI', 'Microsoft YaHei', Arial;
        padding: 4px 0;
        margin: 4px 0;
        min-height: 28px;
        min-width: 80px;
        font-weight: 500;
        letter-spacing: 0.5px;
    }
    QPushButton:hover {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 #009975, stop:1 #43e97b);
        color: #fff;
        font-weight: bold;
    }
    QLabel, QLineEdit, QComboBox, QDateEdit {
        font-size: 15px;
        font-family: 'Segoe UI', 'Microsoft YaHei', Arial;
    }
    QTableWidget {
        background: #fff;
        border-radius: 8px;
        font-size: 14px;
    }
    QHeaderView::section {
        background: #009975;
        color: #fff;
        font-size: 14px;
        font-weight: bold;
        border: none;
        border-radius: 0;
        padding: 4px;
    }
""")

        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 侧边栏
        sidebar = QWidget()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(210)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setSpacing(18)
        sidebar_layout.setContentsMargins(18, 18, 18, 18)
        sidebar_layout.addWidget(QLabel(f"<h2 style='color:#fff;font-weight:bold;'>{tr('menu')}</h2>"))

        self.btn_vehicle = QPushButton(tr("vehicle"))
        self.btn_customer = QPushButton(tr("customer"))
        self.btn_order = QPushButton(tr("order"))
        self.btn_fine = QPushButton(tr("fine"))

        sidebar_layout.addWidget(self.btn_vehicle)
        sidebar_layout.addWidget(self.btn_customer)
        sidebar_layout.addWidget(self.btn_order)
        sidebar_layout.addWidget(self.btn_fine)
        sidebar_layout.addStretch()

        self.btn_lang = QPushButton(tr("lang"))
        self.btn_backup = QPushButton(tr("backup"))
        sidebar_layout.addWidget(self.btn_lang)
        sidebar_layout.addWidget(self.btn_backup)

        main_layout.addWidget(sidebar)

        # 右侧主内容
        right_panel = QVBoxLayout()
        right_panel.setContentsMargins(0, 0, 0, 0)
        right_panel.setSpacing(0)

        # 顶部工具栏
        top_bar = QHBoxLayout()
        top_bar.setContentsMargins(18, 12, 18, 6)
        top_bar.setSpacing(12)
        top_bar.addStretch()

        # 阿联酋时间显示
        self.time_label = QLabel()
        self.time_label.setStyleSheet("font-size:18px; color:#185a9d; font-weight:bold;")
        self.time_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        top_bar.addWidget(self.time_label)

        right_panel.addLayout(top_bar)

        # 主内容区
        self.stacked_widget = QStackedWidget()
        right_panel.addWidget(self.stacked_widget)

        main_layout.addLayout(right_panel)

        self.vehicle_page = VehiclePage()
        self.customer_page = CustomerPage()
        self.order_page = OrderPage()
        self.fine_page = FinePage()

        self.stacked_widget.addWidget(self.vehicle_page)
        self.stacked_widget.addWidget(self.customer_page)
        self.stacked_widget.addWidget(self.order_page)
        self.stacked_widget.addWidget(self.fine_page)

        self.btn_vehicle.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))
        self.btn_customer.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(1))
        self.btn_order.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(2))
        self.btn_fine.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(3))

        self.btn_lang.clicked.connect(self.switch_language)
        self.btn_backup.clicked.connect(self.backup_database)

        self.stacked_widget.setCurrentIndex(0)

        # 启动阿联酋时间定时器
        self.update_uae_time()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_uae_time)
        self.timer.start(1000)

    def update_uae_time(self):
        # 迪拜时区
        try:
            tz = pytz.timezone("Asia/Dubai")
            now = datetime.now(tz)
            time_str = now.strftime("%Y-%m-%d %H:%M:%S")
            self.time_label.setText(f"🇦🇪 {tr('uae_time') if 'uae_time' in LANG[current_lang] else 'UAE Time'}: {time_str}")
        except Exception as e:
            self.time_label.setText("UAE Time: --:--:--")

    def switch_language(self):
        from i18n import LANG, current_lang
        # 切换语言
        if current_lang == "zh":
            import i18n
            i18n.current_lang = "en"
        else:
            import i18n
            i18n.current_lang = "zh"
        QMessageBox.information(self, tr("lang"), tr("switch_success"))
        self.reload_ui()

    def reload_ui(self):
        # 重新加载界面以刷新所有文字
        self.centralWidget().deleteLater()
        self.init_ui()

    def backup_database(self):
        db_file = "rental.db"
        if not os.path.exists(db_file):
            QMessageBox.warning(self, tr("backup"), "数据库文件不存在！")
            return
        save_path, _ = QFileDialog.getSaveFileName(self, tr("backup"), "rental_backup.db", "Database Files (*.db);;All Files (*)")
        if not save_path:
            return
        try:
            shutil.copyfile(db_file, save_path)
            QMessageBox.information(self, tr("backup"), tr("backup_success"))
        except Exception as e:
            QMessageBox.critical(self, tr("backup"), tr("backup_failed") + "\n" + str(e))

if __name__ == "__main__":
    import pytz  # 确保已安装 pytz
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())