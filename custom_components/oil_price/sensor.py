"""国内油价传感器平台."""
from __future__ import annotations

import logging
from datetime import datetime
from typing import Any

import aiohttp
from bs4 import BeautifulSoup

from homeassistant.components.sensor import (
    SensorEntity,
    SensorStateClass,
    SensorDeviceClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import (
    DOMAIN,
    CONF_PROVINCE,
    CONF_SCAN_INTERVAL,
    CONF_CAR_MODEL,
    CONF_TANK_SIZE,
    CONF_FUEL_TYPE,
    DEFAULT_SCAN_INTERVAL,
    DEFAULT_TANK_SIZE,
    DEFAULT_FUEL_TYPE,
    OIL_TYPES,
    DATA_SOURCE_URL,
    ATTR_UPDATE_TIME,
    ATTR_PROVINCE,
)

_LOGGER = logging.getLogger(__name__)

# 省份名称到URL路径的拼音映射
PROVINCE_PINYIN_MAP = {
    "北京": "beijing",
    "上海": "shanghai",
    "天津": "tianjin",
    "重庆": "chongqing",
    "河北": "hebei",
    "山西": "shanxi",
    "辽宁": "liaoning",
    "吉林": "jilin",
    "黑龙江": "heilongjiang",
    "江苏": "jiangsu",
    "浙江": "zhejiang",
    "安徽": "anhui",
    "福建": "fujian",
    "江西": "jiangxi",
    "山东": "shandong",
    "河南": "henan",
    "湖北": "hubei",
    "湖南": "hunan",
    "广东": "guangdong",
    "海南": "hainan",
    "四川": "sichuan",
    "贵州": "guizhou",
    "云南": "yunnan",
    "陕西": "shanxi-3",  # 陕西使用 shanxi-3 以区分山西
    "甘肃": "gansu",
    "青海": "qinghai",
    "内蒙古": "neimenggu",
    "广西": "guangxi",
    "西藏": "xizang",
    "宁夏": "ningxia",
    "新疆": "xinjiang",
}

# 油品类型键到价格标识的映射
OIL_TYPE_KEY_MAP = {
    "gasoline_92": "92#",
    "gasoline_95": "95#",
    "gasoline_98": "98#",
    "diesel_0": "0#",
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """设置国内油价传感器.
    
    为所选省份创建传感器：
    - 4个油价传感器（92#、95#、98#汽油和0#柴油）
    - 1个加满油费用传感器（如果配置了车型和油箱容量）
    """
    province = entry.data.get(CONF_PROVINCE)
    car_model = entry.data.get(CONF_CAR_MODEL, "")
    tank_size = entry.data.get(CONF_TANK_SIZE, DEFAULT_TANK_SIZE)
    fuel_type = entry.data.get(CONF_FUEL_TYPE, DEFAULT_FUEL_TYPE)

    # 创建数据协调器（用于共享数据获取，避免重复请求）
    coordinator = OilPriceDataCoordinator(hass, province)

    sensors = []
    
    # 创建油价传感器实体
    for oil_type_key, oil_type_name in OIL_TYPES.items():
        sensors.append(
            OilPriceSensor(
                coordinator=coordinator,
                province=province,
                oil_type_key=oil_type_key,
                oil_type_name=oil_type_name,
                entry_id=entry.entry_id,
            )
        )
    
    # 创建加满油费用传感器
    sensors.append(
        FullTankCostSensor(
            coordinator=coordinator,
            province=province,
            car_model=car_model,
            tank_size=tank_size,
            fuel_type=fuel_type,
            entry_id=entry.entry_id,
        )
    )

    async_add_entities(sensors, True)


class OilPriceDataCoordinator:
    """油价数据协调器.
    
    负责从数据源获取油价数据，多个传感器共享同一个协调器实例，
    避免重复发送HTTP请求。
    """

    def __init__(self, hass: HomeAssistant, province: str) -> None:
        """初始化协调器."""
        self._hass = hass
        self._province = province
        self._prices: dict[str, float] = {}
        self._update_time: str | None = None
        self._last_fetch_success = False

    @property
    def prices(self) -> dict[str, float]:
        """返回当前油价数据."""
        return self._prices

    @property
    def update_time(self) -> str | None:
        """返回最后更新时间."""
        return self._update_time

    @property
    def available(self) -> bool:
        """返回数据是否可用."""
        return self._last_fetch_success and bool(self._prices)

    async def async_update(self) -> None:
        """异步更新油价数据."""
        session = async_get_clientsession(self._hass)
        
        try:
            # 构建请求URL
            province_pinyin = PROVINCE_PINYIN_MAP.get(self._province, "beijing")
            url = f"{DATA_SOURCE_URL}{province_pinyin}.shtml"
            
            # 设置请求头，模拟浏览器访问
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            }
            
            async with session.get(
                url, 
                timeout=aiohttp.ClientTimeout(total=30),
                headers=headers
            ) as response:
                if response.status != 200:
                    _LOGGER.warning("获取油价数据失败，HTTP状态码: %s", response.status)
                    self._last_fetch_success = False
                    return
                
                html = await response.text()
                self._prices = self._parse_prices(html)
                
                if self._prices:
                    self._update_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    self._last_fetch_success = True
                    _LOGGER.debug("成功获取 %s 油价: %s", self._province, self._prices)
                else:
                    _LOGGER.warning("解析油价数据失败，未找到有效数据")
                    self._last_fetch_success = False
                    
        except aiohttp.ClientError as err:
            _LOGGER.error("HTTP请求错误: %s", err)
            self._last_fetch_success = False
        except Exception as err:
            _LOGGER.error("获取油价时发生意外错误: %s", err)
            self._last_fetch_success = False

    def _parse_prices(self, html: str) -> dict[str, float]:
        """解析HTML页面提取油价数据.
        
        网站使用如下HTML结构存储油价:
        <div id="youjia">
            <dl>
                <dt>北京92#汽油</dt>
                <dd>6.77</dd>
            </dl>
            ...
        </div>
        """
        prices = {}
        
        try:
            soup = BeautifulSoup(html, "html.parser")
            
            # 查找油价容器
            youjia_div = soup.find("div", id="youjia")
            
            if not youjia_div:
                _LOGGER.warning("未找到油价数据容器 (#youjia)")
                return prices
            
            # 遍历所有油品条目
            for dl in youjia_div.find_all("dl"):
                dt = dl.find("dt")  # 油品名称
                dd = dl.find("dd")  # 油品价格
                
                if not (dt and dd):
                    continue
                
                oil_name = dt.get_text(strip=True)
                price_text = dd.get_text(strip=True)
                
                try:
                    price = float(price_text)
                    
                    # 根据油品名称识别类型
                    if "92#" in oil_name or "92号" in oil_name:
                        prices["92#"] = price
                    elif "95#" in oil_name or "95号" in oil_name:
                        prices["95#"] = price
                    elif "98#" in oil_name or "98号" in oil_name:
                        prices["98#"] = price
                    elif "0#" in oil_name or "0号" in oil_name or "柴油" in oil_name:
                        prices["0#"] = price
                        
                except ValueError:
                    _LOGGER.debug("无法解析价格: %s", price_text)
                    continue
                    
        except Exception as err:
            _LOGGER.error("解析HTML时发生错误: %s", err)
        
        return prices


class OilPriceSensor(SensorEntity):
    """油价传感器实体.
    
    每个传感器代表一种油品（92#汽油、95#汽油、98#汽油或0#柴油）的价格。
    """

    _attr_has_entity_name = True
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = "元/升"
    _attr_icon = "mdi:gas-station"

    def __init__(
        self,
        coordinator: OilPriceDataCoordinator,
        province: str,
        oil_type_key: str,
        oil_type_name: str,
        entry_id: str,
    ) -> None:
        """初始化传感器."""
        self._coordinator = coordinator
        self._province = province
        self._oil_type_key = oil_type_key
        self._oil_type_name = oil_type_name
        self._entry_id = entry_id

        # 设置实体属性
        self._attr_unique_id = f"{DOMAIN}_{province}_{oil_type_key}"
        self._attr_name = f"{province}{oil_type_name}"

    @property
    def native_value(self) -> float | None:
        """返回传感器当前值（油价）."""
        price_key = OIL_TYPE_KEY_MAP.get(self._oil_type_key, "")
        return self._coordinator.prices.get(price_key)

    @property
    def available(self) -> bool:
        """返回传感器是否可用."""
        price_key = OIL_TYPE_KEY_MAP.get(self._oil_type_key, "")
        return self._coordinator.available and price_key in self._coordinator.prices

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """返回传感器额外属性."""
        return {
            ATTR_PROVINCE: self._province,
            ATTR_UPDATE_TIME: self._coordinator.update_time,
            "oil_type": self._oil_type_name,
        }

    async def async_update(self) -> None:
        """异步更新传感器状态."""
        await self._coordinator.async_update()


class FullTankCostSensor(SensorEntity):
    """加满油费用传感器.
    
    根据配置的车型、油箱容量和油品类型，计算加满一箱油的预计费用。
    """

    _attr_has_entity_name = True
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_device_class = SensorDeviceClass.MONETARY
    _attr_native_unit_of_measurement = "元"
    _attr_icon = "mdi:currency-cny"

    def __init__(
        self,
        coordinator: OilPriceDataCoordinator,
        province: str,
        car_model: str,
        tank_size: int,
        fuel_type: str,
        entry_id: str,
    ) -> None:
        """初始化加满油费用传感器.
        
        参数:
            coordinator: 数据协调器
            province: 省份名称
            car_model: 车型名称（如 奔驰GLC300L）
            tank_size: 油箱容量（升）
            fuel_type: 油品类型（如 gasoline_95）
            entry_id: 配置条目ID
        """
        self._coordinator = coordinator
        self._province = province
        self._car_model = car_model or "我的车"
        self._tank_size = tank_size
        self._fuel_type = fuel_type
        self._entry_id = entry_id

        # 获取油品显示名称
        self._fuel_type_name = OIL_TYPES.get(fuel_type, "92号汽油")
        
        # 设置实体属性
        self._attr_unique_id = f"{DOMAIN}_{province}_full_tank_cost_{entry_id}"
        self._attr_name = f"{self._car_model}加满油费用"

    @property
    def native_value(self) -> float | None:
        """返回加满油的预计费用."""
        price_key = OIL_TYPE_KEY_MAP.get(self._fuel_type, "92#")
        price = self._coordinator.prices.get(price_key)
        
        if price is None:
            return None
        
        # 计算费用并保留2位小数
        return round(price * self._tank_size, 2)

    @property
    def available(self) -> bool:
        """返回传感器是否可用."""
        price_key = OIL_TYPE_KEY_MAP.get(self._fuel_type, "92#")
        return self._coordinator.available and price_key in self._coordinator.prices

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """返回传感器额外属性."""
        price_key = OIL_TYPE_KEY_MAP.get(self._fuel_type, "92#")
        current_price = self._coordinator.prices.get(price_key)
        
        return {
            ATTR_PROVINCE: self._province,
            ATTR_UPDATE_TIME: self._coordinator.update_time,
            "car_model": self._car_model,
            "tank_size": f"{self._tank_size}升",
            "fuel_type": self._fuel_type_name,
            "unit_price": f"{current_price}元/升" if current_price else None,
        }

    async def async_update(self) -> None:
        """异步更新传感器状态."""
        await self._coordinator.async_update()
