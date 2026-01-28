"""国内油价集成入口."""
from __future__ import annotations

import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

# 支持的平台列表
PLATFORMS: list[Platform] = [Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """设置国内油价集成.
    
    当用户通过UI添加集成时，此函数会被调用。
    
    参数:
        hass: Home Assistant 实例
        entry: 配置条目
        
    返回:
        bool: 设置是否成功
    """
    # 初始化数据存储
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = entry.data

    # 加载传感器平台
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """卸载国内油价集成.
    
    当用户删除集成时，此函数会被调用。
    
    参数:
        hass: Home Assistant 实例
        entry: 配置条目
        
    返回:
        bool: 卸载是否成功
    """
    # 卸载所有平台
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
