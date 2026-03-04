"""国内油价传感器平台."""
from __future__ import annotations

import logging
import re
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
    CONF_CAR_MODEL,
    CONF_TANK_SIZE,
    CONF_FUEL_TYPE,
    DEFAULT_TANK_SIZE,
    DEFAULT_FUEL_TYPE,
    OIL_TYPES,
    OIL_TYPE_KEY_MAP,
    PROVINCE_PINYIN_MAP,
    DATA_SOURCE_URL,
    ATTR_UPDATE_TIME,
    ATTR_PROVINCE,
    ATTR_NEXT_ADJUSTMENT,
    CONF_ENABLE_FORECAST, 
    DEFAULT_ENABLE_FORECAST,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """设置国内油价传感器."""
    province = entry.data.get(CONF_PROVINCE)
    car_model = entry.data.get(CONF_CAR_MODEL, "")
    tank_size = entry.data.get(CONF_TANK_SIZE, DEFAULT_TANK_SIZE)
    fuel_type = entry.data.get(CONF_FUEL_TYPE, DEFAULT_FUEL_TYPE)
    enable_forecast = entry.data.get(CONF_ENABLE_FORECAST, DEFAULT_ENABLE_FORECAST)

    coordinator = OilPriceDataCoordinator(hass, province, enable_forecast)
    sensors = []
    
    for oil_type_key, oil_type_name in OIL_TYPES.items():
        sensors.append(OilPriceSensor(
            coordinator=coordinator,
            province=province,
            oil_type_key=oil_type_key,
            oil_type_name=oil_type_name,
            entry_id=entry.entry_id,
        ))
    
    sensors.append(FullTankCostSensor(
        coordinator=coordinator,
        province=province,
        car_model=car_model,
        tank_size=tank_size,
        fuel_type=fuel_type,
        entry_id=entry.entry_id,
    ))
    
    if enable_forecast:
        sensors.append(OilPriceForecastSensor(
            coordinator=coordinator,
            province=province,
            entry_id=entry.entry_id,
        ))
    
    async_add_entities(sensors, True)


class OilPriceDataCoordinator:
    """油价数据协调器."""
    
    def __init__(self, hass: HomeAssistant, province: str, enable_forecast: bool = True) -> None:
        self._hass = hass
        self._province = province
        self._enable_forecast = enable_forecast
        self._prices: dict[str, float] = {}
        self._update_time: str | None = None
        self._last_fetch_success = False
        self._forecast_info: str | None = None

    @property
    def forecast_info(self) -> str | None:
        return self._forecast_info

    @property
    def prices(self) -> dict[str, float]:
        return self._prices

    @property
    def update_time(self) -> str | None:
        return self._update_time

    @property
    def available(self) -> bool:
        return self._last_fetch_success and bool(self._prices)

    async def async_update(self) -> None:
        session = async_get_clientsession(self._hass)
        
        try:
            province_pinyin = PROVINCE_PINYIN_MAP.get(self._province, "beijing")
            url = f"{DATA_SOURCE_URL}{province_pinyin}.shtml"
            
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
            
            async with session.get(url, timeout=30, headers=headers) as response:
                if response.status != 200:
                    _LOGGER.warning("获取油价数据失败，状态码: %s", response.status)
                    self._last_fetch_success = False
                    return
                
                html = await response.text()
                self._prices = self._parse_prices(html)
                
                if self._prices:
                    self._update_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    self._last_fetch_success = True
                else:
                    _LOGGER.warning("解析油价数据失败")
                    self._last_fetch_success = False
            
            if self._enable_forecast:
                await self._update_forecast_info(session)
                    
        except aiohttp.ClientError as err:
            _LOGGER.error("HTTP请求错误: %s", err)
            self._last_fetch_success = False
        except Exception as err:
            _LOGGER.error("获取油价时发生错误: %s", err)
            self._last_fetch_success = False

    async def _update_forecast_info(self, session: aiohttp.ClientSession) -> None:
        try:
            async with session.get(DATA_SOURCE_URL, timeout=30) as response:
                if response.status != 200:
                    _LOGGER.warning("获取预告信息失败，状态码: %s", response.status)
                    return
                
                html = await response.text()
                self._parse_forecast(html)
        except Exception as err:
            _LOGGER.warning("获取预告信息失败: %s", err)

    def _parse_forecast(self, text: str) -> None:
        try:
            soup = BeautifulSoup(text, "html.parser")
            hint_text = str()
            for text_node in soup.find_all(text=True):
                textinfo = text_node.strip()
                _LOGGER.debug("检查文本节点: %s", textinfo)
                time_match = re.search(r'油价\s*(\d{1,2}月\d{1,2}日)\s*(\d{1,2})\s*时\s*调整', textinfo)
                if not time_match:
                    hint_text.append(textinfo)
                if '预计上调' in textinfo:
                    hint_text.append(textinfo)
            else:
                _LOGGER.debug("未找到包含预告信息的文本")
                return
            _LOGGER.debug("找到预告信息文本: %s", hint_text)
            time_match = re.search(r'油价\s*(\d{1,2}月\d{1,2}日)\s*(\d{1,2})\s*时\s*调整', hint_text)
            if not time_match:
                time_match = re.search(r'油价\s*(\d{1,2}月\d{1,2}日)\s*(\d{1,2})\s*时', hint_text)
            _LOGGER.debug("解析错误时间信息: %s", time_match)
            if not time_match:
                _LOGGER.debug("未找到时间信息")
                return
            
            date_str = time_match.group(1)
            hour = int(time_match.group(2))
            
            if hour == 24:
                date_match = re.match(r'(\d{1,2})月(\d{1,2})日', date_str)
                if date_match:
                    month = int(date_match.group(1))
                    day = int(date_match.group(2))
                    day += 1
                    
                    month_days = {1:31, 2:28, 3:31, 4:30, 5:31, 6:30, 7:31, 8:31, 9:30, 10:31, 11:30, 12:31}
                    
                    if day > month_days.get(month, 31):
                        day = 1
                        month += 1
                        if month > 12:
                            month = 1
                    
                    date_str = f"{month}月{day}日"
            
            price_match = re.search(r'(上调|上涨|下跌)([\d.]+元/升-[\d.]+元/升)', hint_text)
            if not price_match:
                _LOGGER.debug("解析错误时间信息")
                return
            
            direction = price_match.group(1)
            amount = price_match.group(2)
            amount = re.sub(r'\s+', '', amount)
            
            self._forecast_info = f"{date_str}{direction}{amount}"
            
        except Exception as err:
            _LOGGER.error("解析预告信息时发生错误: %s", err)
            self._forecast_info = "解析预告信息失败"

    def _parse_prices(self, html: str) -> dict[str, float]:
        prices = {}
        
        try:
            soup = BeautifulSoup(html, "html.parser")
            youjia_div = soup.find("div", id="youjia")
            
            if not youjia_div:
                _LOGGER.warning("未找到油价数据容器")
                return prices
            
            for dl in youjia_div.find_all("dl"):
                dt = dl.find("dt")
                dd = dl.find("dd")
                
                if not (dt and dd):
                    continue
                
                oil_name = dt.get_text(strip=True)
                price_text = dd.get_text(strip=True)
                
                try:
                    price = float(price_text)
                    
                    if "92#" in oil_name or "92号" in oil_name:
                        prices["92#"] = price
                    elif "95#" in oil_name or "95号" in oil_name:
                        prices["95#"] = price
                    elif "98#" in oil_name or "98号" in oil_name:
                        prices["98#"] = price
                    elif "0#" in oil_name or "0号" in oil_name or "柴油" in oil_name:
                        prices["0#"] = price
                        
                except ValueError:
                    continue
                    
        except Exception as err:
            _LOGGER.error("解析油价时发生错误: %s", err)
        
        return prices


class OilPriceSensor(SensorEntity):
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
        self._coordinator = coordinator
        self._province = province
        self._oil_type_key = oil_type_key
        self._oil_type_name = oil_type_name
        self._entry_id = entry_id

        self._attr_unique_id = f"{DOMAIN}_{province}_{oil_type_key}"
        self._attr_name = f"{province}{oil_type_name}"

    @property
    def native_value(self) -> float | None:
        price_key = OIL_TYPE_KEY_MAP.get(self._oil_type_key, "")
        return self._coordinator.prices.get(price_key)

    @property
    def available(self) -> bool:
        price_key = OIL_TYPE_KEY_MAP.get(self._oil_type_key, "")
        return self._coordinator.available and price_key in self._coordinator.prices

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        return {
            ATTR_PROVINCE: self._province,
            ATTR_UPDATE_TIME: self._coordinator.update_time,
            "oil_type": self._oil_type_name,
        }

    async def async_update(self) -> None:
        await self._coordinator.async_update()


class FullTankCostSensor(SensorEntity):
    _attr_has_entity_name = True
    _attr_state_class = SensorStateClass.TOTAL
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
        self._coordinator = coordinator
        self._province = province
        self._car_model = car_model or "我的车"
        self._tank_size = tank_size
        self._fuel_type = fuel_type
        self._entry_id = entry_id
        self._fuel_type_name = OIL_TYPES.get(fuel_type, "92号汽油")
        
        self._attr_unique_id = f"{DOMAIN}_{province}_full_tank_cost_{entry_id}"
        self._attr_name = f"{self._car_model}加满油费用"

    @property
    def native_value(self) -> float | None:
        price_key = OIL_TYPE_KEY_MAP.get(self._fuel_type, "92#")
        price = self._coordinator.prices.get(price_key)
        
        if price is None:
            return None
        
        return round(price * self._tank_size, 2)

    @property
    def available(self) -> bool:
        price_key = OIL_TYPE_KEY_MAP.get(self._fuel_type, "92#")
        return self._coordinator.available and price_key in self._coordinator.prices

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
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
        await self._coordinator.async_update()


class OilPriceForecastSensor(SensorEntity):
    _attr_has_entity_name = True
    _attr_icon = "mdi:calendar-clock"

    def __init__(self, coordinator: OilPriceDataCoordinator, province: str, entry_id: str) -> None:
        self._coordinator = coordinator
        self._province = province
        self._entry_id = entry_id

        self._attr_unique_id = f"{DOMAIN}_{province}_forecast"
        self._attr_name = f"{province}油价预告信息"
    
    @property
    def native_value(self) -> str:
        return self._coordinator.forecast_info or "暂无预告信息"
    
    @property
    def available(self) -> bool:
        return self._coordinator.available
    
    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        return {
            ATTR_PROVINCE: self._province,
            ATTR_UPDATE_TIME: self._coordinator.update_time,
            ATTR_NEXT_ADJUSTMENT: self._coordinator.forecast_info,
        }
    
    async def async_update(self) -> None:
        await self._coordinator.async_update()
