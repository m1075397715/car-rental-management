# i18n.py

LANG = {
    "zh": {
        # 通用
        "ok": "确定",
        "cancel": "取消",
        "tip": "提示",
        "yes": "是",
        "no": "否",
        "search": "搜索",
        "export_csv": "导出CSV",
        "export_success": "已导出！",
        "export_failed": "导出失败",
        "prev_page": "上一页",
        "next_page": "下一页",
        "page_info": "第 {0} / {1} 页（共 {2} 条）",

        # 菜单/主界面
        "vehicle": "车辆管理",
        "customer": "客户管理",
        "order": "订单管理",
        "fine": "罚款记录",
        "menu": "菜单",
        "lang": "中/English",
        "backup": "一键备份",
        "switch_success": "语言切换成功！",
        "backup_success": "备份成功！",
        "backup_failed": "备份失败！",
        "title": "车辆租赁管理系统",
        "uae_time": "阿联酋时间",

        # 车辆管理
        "vehicle_manage": "车辆管理页面",
        "add_vehicle": "添加车辆",
        "delete_vehicle": "删除车辆",
        "license_plate": "车牌号",
        "model": "型号",
        "year": "年份",
        "insurance_expiry": "保险到期日",
        "mileage": "里程数",
        "monthly_price": "月租价",
        "status": "状态",
        "idle": "空闲",
        "rented": "已租",
        "deposit": "押金",
        "remark": "备注",
        "search_placeholder": "输入车牌号/型号搜索",
        "plate_required": "车牌号、型号、年份不能为空！",
        "year_number": "年份必须为数字！",
        "plate_exists": "车牌号已存在！",
        "confirm_delete": "确定要删除车辆 {0} 吗？",
        "insurance_expired": "保险到期车辆：",
        "select_vehicle": "请先选中要删除的车辆！",

        # 客户管理
        "customer_manage": "客户管理页面",
        "add_customer": "添加客户",
        "delete_customer": "删除客户",
        "name": "姓名",
        "phone": "手机号",
        "is_corporate": "企业客户",
        "normal": "普通",
        "vip": "VIP",
        "blacklist": "黑名单",
        "order_history": "历史订单",
        "order_history_list": "该客户所有历史订单：",
        "order_info": "订单信息",
        "view_history": "查看",
        "search_customer_placeholder": "输入姓名/手机号搜索",
        "name_phone_required": "姓名和手机号不能为空！",
        "phone_invalid": "手机号格式不正确！",
        "phone_exists": "手机号已存在！",
        "confirm_delete_customer": "确定要删除客户 {0} 吗？",
        "select_customer": "请先选中要删除的客户！",

        # 订单管理
        "order_manage": "订单管理页面",
        "add_order": "添加订单",
        "delete_order": "删除订单",
        "renew_order": "续租订单",
        "order_id": "订单编号",
        "customer_name": "客户姓名",
        "vehicle_plate": "车牌号",
        "start_date": "起始日期",
        "end_date": "结束日期",
        "order_status": "订单状态",
        "total_amount": "总金额",
        "ongoing": "进行中",
        "completed": "已完成",
        "overdue": "逾期",
        "cancelled": "已取消",
        "search_order_placeholder": "输入客户/车牌/状态搜索",
        "order_expired": "租赁到期订单：",
        "add_customer_vehicle_first": "请先添加客户和车辆！",
        "customer_vehicle_required": "客户和车辆不能为空！",
        "date_invalid": "起止日期不正确！",
        "amount_invalid": "金额格式不正确！",
        "select_order": "请先选中要操作的订单！",
        "confirm_delete_order": "确定要删除订单 {0} 吗？",
        "new_end_date": "新结束日期",
        "renew_date_error": "新结束日期必须大于原结束日期！",

        # 罚款记录
        "fine_manage": "罚款记录页面",
        "add_fine": "添加罚款",
        "delete_fine": "删除罚款",
        "fine_id": "编号",
        "fine_type": "罚款类型",
        "fine_amount": "罚款金额",
        "fine_date": "罚款日期",
        "fine_paid": "已缴纳",
        "fine_required": "车牌号、客户、罚款类型不能为空！",
        "select_fine": "请先选中要删除的罚款记录！",
        "confirm_delete_fine": "确定要删除罚款记录 {0} 吗？",
        "search_fine_placeholder": "输入车牌号/客户/类型搜索",
        "local_fine_record": "本地罚款记录",
        "official_fine_query": "迪拜交警官网查询",
        "webengine_not_available": "未安装WebEngine，无法嵌入官网页面。"
    },
    "en": {
        # 通用（与上面对应，这里不重复）
        "ok": "OK",
        "cancel": "Cancel",
        "tip": "Tip",
        "yes": "Yes",
        "no": "No",
        "search": "Search",
        "export_csv": "Export CSV",
        "export_success": "Exported!",
        "export_failed": "Export failed",
        "prev_page": "Prev",
        "next_page": "Next",
        "page_info": "Page {0} / {1} (Total {2})",
        # ... 省略，其余对应前面 zh 的 key（你已有完整定义）
    }
}

# 当前语言
current_lang = "zh"

# 已注册的页面（便于统一刷新文字）
registered_pages = []


def tr(key):
    """获取翻译文本"""
    return LANG[current_lang].get(key, key)


def tr_reverse(value):
    """通过翻译值找到原始 key"""
    for k, v in LANG[current_lang].items():
        if v == value:
            return k
    return value


def set_language(lang):
    """切换语言并刷新所有页面"""
    global current_lang
    if lang in LANG:
        current_lang = lang
        for page in registered_pages:
            if hasattr(page, "refresh_texts"):
                page.refresh_texts()
        return True
    return False


def register_page(page):
    """页面初始化时调用，用于支持语言切换"""
    registered_pages.append(page)