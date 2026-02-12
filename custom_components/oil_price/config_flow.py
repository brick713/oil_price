"""国内油价集成配置流程."""
from __future__ import annotations

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult

from .const import (
    DOMAIN,
    CONF_PROVINCE,
    CONF_SCAN_INTERVAL,
    CONF_CAR_MODEL,
    CONF_TANK_SIZE,
    CONF_FUEL_TYPE,
    DEFAULT_PROVINCE,
    DEFAULT_SCAN_INTERVAL,
    DEFAULT_CAR_MODEL,
    DEFAULT_TANK_SIZE,
    DEFAULT_FUEL_TYPE,
    PROVINCE_LIST,
    OIL_TYPES,
    CONF_ENABLE_FORECAST,
    DEFAULT_ENABLE_FORECAST,
)

# 油品类型选择列表
FUEL_TYPE_OPTIONS = {
    "gasoline_92": "92号汽油",
    "gasoline_95": "95号汽油",
    "gasoline_98": "98号汽油",
    "diesel_0": "0号柴油",
}


class OilPriceConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """处理国内油价集成的配置流程."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict | None = None
    ) -> FlowResult:
        """处理用户配置步骤."""
        errors = {}

        if user_input is not None:
            user_input.setdefault(CONF_ENABLE_FORECAST, DEFAULT_ENABLE_FORECAST)
            user_input.setdefault(CONF_CAR_MODEL, DEFAULT_CAR_MODEL)
            user_input.setdefault(CONF_TANK_SIZE, DEFAULT_TANK_SIZE)
            user_input.setdefault(CONF_FUEL_TYPE, DEFAULT_FUEL_TYPE)
            user_input.setdefault(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
            
            province = user_input[CONF_PROVINCE]
            car_model = user_input.get(CONF_CAR_MODEL, "")
            # 生成唯一ID
            unique_suffix = f"{province}_{car_model}" if car_model else province
            await self.async_set_unique_id(f"{DOMAIN}_{unique_suffix}")
            self._abort_if_unique_id_configured()
            
            # 生成标题
            if car_model:
                title = f"{car_model} - {province}油价"
            else:
                title = f"国内油价 - {province}"
            
            return self.async_create_entry(title=title, data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_PROVINCE, default=DEFAULT_PROVINCE): vol.In(PROVINCE_LIST),
                    vol.Optional(CONF_CAR_MODEL, description={"suggested_value": "奔驰GLC300L"}): str,
                    vol.Optional(CONF_TANK_SIZE, default=DEFAULT_TANK_SIZE): vol.All(
                        vol.Coerce(int), vol.Range(min=20, max=200)
                    ),
                    vol.Optional(CONF_FUEL_TYPE, default=DEFAULT_FUEL_TYPE): vol.In(FUEL_TYPE_OPTIONS),
                    vol.Optional(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL): vol.All(
                        vol.Coerce(int), vol.Range(min=600, max=86400)
                    ),
                    vol.Optional(CONF_ENABLE_FORECAST, default=DEFAULT_ENABLE_FORECAST): bool,
                }
            ),
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: config_entries.ConfigEntry) -> config_entries.OptionsFlow:
        """获取选项配置流程."""
        return OilPriceOptionsFlow()


class OilPriceOptionsFlow(config_entries.OptionsFlow):
    """处理国内油价集成的选项配置."""
    
    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """初始化选项配置流程."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input: dict | None = None) -> FlowResult:
        """处理选项配置的初始步骤."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_CAR_MODEL, 
                        default=self.config_entry.data.get(CONF_CAR_MODEL, "")
                    ): str,
                    vol.Optional(
                        CONF_TANK_SIZE, 
                        default=self.config_entry.data.get(CONF_TANK_SIZE, DEFAULT_TANK_SIZE)
                    ): vol.All(vol.Coerce(int), vol.Range(min=20, max=200)),
                    vol.Optional(
                        CONF_FUEL_TYPE, 
                        default=self.config_entry.data.get(CONF_FUEL_TYPE, DEFAULT_FUEL_TYPE)
                    ): vol.In(FUEL_TYPE_OPTIONS),
                    vol.Optional(
                        CONF_SCAN_INTERVAL, 
                        default=self.config_entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
                    ): vol.All(vol.Coerce(int), vol.Range(min=600, max=86400)),
                    vol.Optional(
                        CONF_ENABLE_FORECAST, 
                        default=self.config_entry.data.get(CONF_ENABLE_FORECAST, DEFAULT_ENABLE_FORECAST)
                    ): bool,
                }
            ),
        )
