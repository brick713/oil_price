'''
Author: brick713 hibrick713@gmail.com
Date: 2026-01-30 11:06:37
LastEditors: brick713 hibrick713@gmail.com
LastEditTime: 2026-02-06 17:56:14
FilePath: /oil_price/custom_components/oil_price/const.py
Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
'''
"""国内油价集成的常量定义."""

# 集成域名
DOMAIN = "Oil_Price"

# 预告传感器属性键（简化版）
ATTR_NEXT_ADJUSTMENT = "next_adjustment"  # 整合的预告信息
ATTR_IS_ADJUSTMENT_TODAY = "is_adjustment_today"
CONF_ENABLE_FORECAST = "enable_forecast"  # 配置项：是否启用预告信息
DEFAULT_ENABLE_FORECAST = True

# 默认配置
DEFAULT_PROVINCE = "广东"  # 默认省份
DEFAULT_SCAN_INTERVAL = 3600  # 默认更新间隔：1小时（秒）
DEFAULT_TANK_SIZE = 50  # 默认油箱容量：50升
DEFAULT_CAR_MODEL = ""  # 默认车型名称
DEFAULT_FUEL_TYPE = "gasoline_92"  # 默认油品类型

# 配置键名称
CONF_PROVINCE = "province"
CONF_SCAN_INTERVAL = "scan_interval"
CONF_CAR_MODEL = "car_model"
CONF_TANK_SIZE = "tank_size"
CONF_FUEL_TYPE = "fuel_type"

# 油品类型映射
OIL_TYPES = {
    "gasoline_92": "92号汽油",
    "gasoline_95": "95号汽油",
    "gasoline_98": "98号汽油",
    "diesel_0": "0号柴油",
}

# 支持的省份列表（共31个省市自治区）
PROVINCE_LIST = [
    # 直辖市
    "北京", "上海", "天津", "重庆",
    # 华北地区
    "河北", "山西", "内蒙古",
    # 东北地区
    "辽宁", "吉林", "黑龙江",
    # 华东地区
    "江苏", "浙江", "安徽", "福建", "江西", "山东",
    # 中南地区
    "河南", "湖北", "湖南", "广东", "广西", "海南",
    # 西南地区
    "四川", "贵州", "云南", "西藏",
    # 西北地区
    "陕西", "甘肃", "青海", "宁夏", "新疆",
]

# 数据源URL（汽油价格网）
DATA_SOURCE_URL = "http://www.qiyoujiage.com/"

# 传感器属性键
ATTR_GASOLINE_92 = "gasoline_92"
ATTR_GASOLINE_95 = "gasoline_95"
ATTR_GASOLINE_98 = "gasoline_98"
ATTR_DIESEL_0 = "diesel_0"
ATTR_UPDATE_TIME = "update_time"
ATTR_PROVINCE = "province"
