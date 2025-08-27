import sqlite3, json, os

DB_FILE = "rental.db"

vehicle_data = []
customer_data = []
order_data = []
fine_data = []


def get_conn():
    return sqlite3.connect(DB_FILE)


def init_db():
    """初始化表"""
    conn = get_conn()
    cur = conn.cursor()

    # 车辆表
    cur.execute("""
    CREATE TABLE IF NOT EXISTS vehicles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        plate TEXT NOT NULL UNIQUE,
        model TEXT, year TEXT, insurance TEXT,
        mileage TEXT, monthly_price TEXT,
        deposit TEXT, remark TEXT
    )""")

    # 客户表
    cur.execute("""
    CREATE TABLE IF NOT EXISTS customers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT, phone TEXT UNIQUE,
        is_corporate INTEGER, status TEXT, remark TEXT
    )""")

    # 订单表
    cur.execute("""
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer TEXT, vehicle TEXT,
        start_date TEXT, end_date TEXT,
        status TEXT, amount TEXT, remark TEXT
    )""")

    # 罚款表
    cur.execute("""
    CREATE TABLE IF NOT EXISTS fines (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        vehicle TEXT, customer TEXT,
        fine_type TEXT, amount TEXT,
        fine_date TEXT, paid INTEGER,
        remark TEXT
    )""")

    conn.commit()
    conn.close()


def migrate_json_to_sqlite():
    """如果表是空的，且存在 JSON 文件，就导入数据"""
    conn = get_conn()
    cur = conn.cursor()

    # 检查是否已有数据
    cur.execute("SELECT COUNT(*) FROM customers")
    has_customer = cur.fetchone()[0]
    if has_customer == 0 and os.path.exists("customer_data.json"):
        with open("customer_data.json", "r", encoding="utf-8") as f:
            customers = json.load(f)
        for c in customers:
            cur.execute("INSERT INTO customers (name, phone, is_corporate, status, remark) VALUES (?, ?, ?, ?, ?)",
                        (c["name"], c["phone"], int(c["is_corporate"]), c["status"], c["remark"]))
        print(f"✅ 导入 {len(customers)} 条客户数据")

    cur.execute("SELECT COUNT(*) FROM vehicles")
    has_vehicle = cur.fetchone()[0]
    if has_vehicle == 0 and os.path.exists("vehicle_data.json"):
        with open("vehicle_data.json", "r", encoding="utf-8") as f:
            vehicles = json.load(f)
        for v in vehicles:
            cur.execute("INSERT INTO vehicles (plate, model, year, insurance, mileage, monthly_price, deposit, remark) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                        (v["plate"], v["model"], v["year"], v["insurance"], v["mileage"], v["monthly_price"], v["deposit"], v["remark"]))
        print(f"✅ 导入 {len(vehicles)} 条车辆数据")

    cur.execute("SELECT COUNT(*) FROM orders")
    has_order = cur.fetchone()[0]
    if has_order == 0 and os.path.exists("order_data.json"):
        with open("order_data.json", "r", encoding="utf-8") as f:
            orders = json.load(f)
        for o in orders:
            cur.execute("INSERT INTO orders (customer, vehicle, start_date, end_date, status, amount, remark) VALUES (?, ?, ?, ?, ?, ?, ?)",
                        (o["customer"], o["vehicle"], o["start_date"], o["end_date"], o["status"], o["amount"], o["remark"]))
        print(f"✅ 导入 {len(orders)} 条订单数据")

    cur.execute("SELECT COUNT(*) FROM fines")
    has_fine = cur.fetchone()[0]
    if has_fine == 0 and os.path.exists("fine_data.json"):
        with open("fine_data.json", "r", encoding="utf-8") as f:
            fines = json.load(f)
        for fdata in fines:
            cur.execute("INSERT INTO fines (vehicle, customer, fine_type, amount, fine_date, paid, remark) VALUES (?, ?, ?, ?, ?, ?, ?)",
                        (fdata["vehicle"], fdata["customer"], fdata["fine_type"], fdata["amount"], fdata["fine_date"], int(fdata["paid"]), fdata["remark"]))
        print(f"✅ 导入 {len(fines)} 条罚款数据")

    conn.commit()
    conn.close()


def load_all_data():
    """从数据库加载到全局 list"""
    global vehicle_data, customer_data, order_data, fine_data
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("SELECT * FROM vehicles")
    rows = cur.fetchall()
    vehicle_data[:] = [dict(id=r[0], plate=r[1], model=r[2], year=r[3], insurance=r[4],
                            mileage=r[5], monthly_price=r[6], deposit=r[7], remark=r[8])
                       for r in rows]

    cur.execute("SELECT * FROM customers")
    rows = cur.fetchall()
    customer_data[:] = [dict(id=r[0], name=r[1], phone=r[2], is_corporate=bool(r[3]),
                             status=r[4], remark=r[5]) for r in rows]

    cur.execute("SELECT * FROM orders")
    rows = cur.fetchall()
    order_data[:] = [dict(id=r[0], customer=r[1], vehicle=r[2], start_date=r[3],
                          end_date=r[4], status=r[5], amount=r[6], remark=r[7])
                     for r in rows]

    cur.execute("SELECT * FROM fines")
    rows = cur.fetchall()
    fine_data[:] = [dict(id=r[0], vehicle=r[1], customer=r[2], fine_type=r[3],
                         amount=r[4], fine_date=r[5], paid=bool(r[6]), remark=r[7])
                    for r in rows]

    conn.close()


def save_all_data():
    """把全局 list 写回数据库（粗暴方式：先删再插）"""
    conn = get_conn()
    cur = conn.cursor()

    # vehicles
    cur.execute("DELETE FROM vehicles")
    for v in vehicle_data:
        cur.execute("INSERT INTO vehicles (id, plate, model, year, insurance, mileage, monthly_price, deposit, remark) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (v["id"], v["plate"], v["model"], v["year"], v["insurance"], v["mileage"], v["monthly_price"], v["deposit"], v["remark"]))

    # customers
    cur.execute("DELETE FROM customers")
    for c in customer_data:
        cur.execute("INSERT INTO customers (id, name, phone, is_corporate, status, remark) VALUES (?, ?, ?, ?, ?, ?)",
                    (c["id"], c["name"], c["phone"], int(c["is_corporate"]), c["status"], c["remark"]))

    # orders
    cur.execute("DELETE FROM orders")
    for o in order_data:
        cur.execute("INSERT INTO orders (id, customer, vehicle, start_date, end_date, status, amount, remark) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                    (o["id"], o["customer"], o["vehicle"], o["start_date"], o["end_date"], o["status"], o["amount"], o["remark"]))

    # fines
    cur.execute("DELETE FROM fines")
    for f in fine_data:
        cur.execute("INSERT INTO fines (id, vehicle, customer, fine_type, amount, fine_date, paid, remark) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                    (f["id"], f["vehicle"], f["customer"], f["fine_type"], f["amount"], f["fine_date"], int(f["paid"]), f["remark"]))

    conn.commit()
    conn.close()


# 初始化数据库 & JSON迁移 & 初次加载
init_db()
migrate_json_to_sqlite()
load_all_data()