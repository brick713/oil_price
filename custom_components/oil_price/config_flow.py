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


class OilPriceOptionsFlow(config_entries.OptionsFlow):
    """处理选项配置."""

    async def async_step_init(self, user_input: dict | None = None) -> FlowResult:
        """处理选项配置."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Optional(
                    CONF_CAR_MODEL, 
                    default=self.config_entry.data.get(CONF_CAR_MODEL, DEFAULT_CAR_MODEL)
                ): str,
                vol.Optional(
                    CONF_TANK_SIZE, 
                    default=self.config_entry.data.get(CONF_TANK_SIZE, DEFAULT_TANK_SIZE)
                ): vol.All(vol.Coerce(int), vol.Range(min=20, max=200)),
                vol.Optional(
                    CONF_FUEL_TYPE, 
                    default=self.config_entry.data.get(CONF_FUEL_TYPE, DEFAULT_FUEL_TYPE)
                ): vol.In(OIL_TYPES),
                vol.Optional(
                    CONF_SCAN_INTERVAL, 
                    default=self.config_entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
                ): vol.All(vol.Coerce(int), vol.Range(min=600, max=86400)),
                vol.Optional(
                    CONF_ENABLE_FORECAST, 
                    default=self.config_entry.data.get(CONF_ENABLE_FORECAST, DEFAULT_ENABLE_FORECAST)
                ): bool,
            }),
        )


class OilPriceConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """处理配置流程."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict | None = None
    ) -> FlowResult:
        """处理用户配置."""
        if user_input is not None:
            # 设置默认值
            defaults = {
                CONF_ENABLE_FORECAST: DEFAULT_ENABLE_FORECAST,
                CONF_CAR_MODEL: DEFAULT_CAR_MODEL,
                CONF_TANK_SIZE: DEFAULT_TANK_SIZE,
                CONF_FUEL_TYPE: DEFAULT_FUEL_TYPE,
                CONF_SCAN_INTERVAL: DEFAULT_SCAN_INTERVAL,
            }
            
            for key, default in defaults.items():
                if key not in user_input:
                    user_input[key] = default
            
            province = user_input[CONF_PROVINCE]
            car_model = user_input[CONF_CAR_MODEL]
            
            # 生成唯一ID
            unique_suffix = f"{province}_{car_model}" if car_model else province
            await self.async_set_unique_id(f"{DOMAIN}_{unique_suffix}")
            self._abort_if_unique_id_configured()
            
            # 生成标题
            title = f"{car_model} - {province}油价" if car_model else f"国内油价 - {province}"
            
            return self.async_create_entry(title=title, data=user_input)

        # 配置表单
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_PROVINCE, default=DEFAULT_PROVINCE): vol.In(PROVINCE_LIST),
                vol.Optional(CONF_CAR_MODEL, default=DEFAULT_CAR_MODEL): str,
                vol.Optional(CONF_TANK_SIZE, default=DEFAULT_TANK_SIZE): vol.All(
                    vol.Coerce(int), vol.Range(min=20, max=200)
                ),
                vol.Optional(CONF_FUEL_TYPE, default=DEFAULT_FUEL_TYPE): vol.In(OIL_TYPES),
                vol.Optional(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL): vol.All(
                    vol.Coerce(int), vol.Range(min=600, max=86400)
                ),
                vol.Optional(CONF_ENABLE_FORECAST, default=DEFAULT_ENABLE_FORECAST): bool,
            }),
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: config_entries.ConfigEntry) -> config_entries.OptionsFlow:
        """获取选项配置流程."""
        return OilPriceOptionsFlow()
