"""国内油价集成的常量定义."""

# 集成域名
DOMAIN = "Oil_Price"

# 默认配置
DEFAULT_PROVINCE = "广东"
DEFAULT_SCAN_INTERVAL = 3600
DEFAULT_TANK_SIZE = 50
DEFAULT_CAR_MODEL = ""
DEFAULT_FUEL_TYPE = "gasoline_92"
DEFAULT_ENABLE_FORECAST = True

# 配置键名称
CONF_PROVINCE = "province"
CONF_SCAN_INTERVAL = "scan_interval"
CONF_CAR_MODEL = "car_model"
CONF_TANK_SIZE = "tank_size"
CONF_FUEL_TYPE = "fuel_type"
CONF_ENABLE_FORECAST = "enable_forecast"

# 油品类型映射
OIL_TYPES = {
    "gasoline_92": "92号汽油",
    "gasoline_95": "95号汽油",
    "gasoline_98": "98号汽油",
    "diesel_0": "0号柴油",
}

# 支持的省份列表
PROVINCE_LIST = [
    "北京", "上海", "天津", "重庆",
    "河北", "山西", "内蒙古",
    "辽宁", "吉林", "黑龙江",
    "江苏", "浙江", "安徽", "福建", "江西", "山东",
    "河南", "湖北", "湖南", "广东", "广西", "海南",
    "四川", "贵州", "云南", "西藏",
    "陕西", "甘肃", "青海", "宁夏", "新疆",
]

# 数据源URL
DATA_SOURCE_URL = "http://www.qiyoujiage.com/"

# 传感器属性键
ATTR_UPDATE_TIME = "update_time"
ATTR_PROVINCE = "province"
ATTR_NEXT_ADJUSTMENT = "next_adjustment"
