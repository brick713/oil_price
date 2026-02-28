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

# 油品类型键到价格标识的映射
OIL_TYPE_KEY_MAP = {
    "gasoline_92": "92#",
    "gasoline_95": "95#",
    "gasoline_98": "98#",
    "diesel_0": "0#",
}

# 省份名称到URL路径的拼音映射
PROVINCE_PINYIN_MAP = {
    "北京": "beijing", "上海": "shanghai", "天津": "tianjin", "重庆": "chongqing",
    "河北": "hebei", "山西": "shanxi", "辽宁": "liaoning", "吉林": "jilin", 
    "黑龙江": "heilongjiang", "江苏": "jiangsu", "浙江": "zhejiang", "安徽": "anhui",
    "福建": "fujian", "江西": "jiangxi", "山东": "shandong", "河南": "henan",
    "湖北": "hubei", "湖南": "hunan", "广东": "guangdong", "海南": "hainan",
    "四川": "sichuan", "贵州": "guizhou", "云南": "yunnan", "陕西": "shanxi-3",
    "甘肃": "gansu", "青海": "qinghai", "内蒙古": "neimenggu", "广西": "guangxi",
    "西藏": "xizang", "宁夏": "ningxia", "新疆": "xinjiang",
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
