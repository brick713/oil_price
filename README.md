# 国内油价 - Home Assistant 集成

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)

一个用于获取中国各省市实时油价的 Home Assistant 自定义集成组件，支持配置车型和油箱容量，自动计算加满油费用。

## ✨ 功能特点

| 功能 | 描述 |
|------|------|
| 🗺️ 全国覆盖 | 支持31个省市自治区 |
| ⛽ 多种油品 | 92#、95#、98# 汽油和 0# 柴油 |
| 🚗 车型配置 | 支持设置车型名称和油箱容量 |
| 💰 费用计算 | 自动计算加满一箱油的预计费用 |
| 🔄 自动更新 | 可配置更新间隔（10分钟 ~ 24小时） |
| 🎨 UI 配置 | 支持通过 Home Assistant 界面添加 |
| 🌐 多语言 | 支持中文和英文界面 |

## 📦 安装方法

### 方法一：HACS 安装（推荐）

1. 打开 HACS → 集成
2. 点击右上角菜单 → 自定义存储库
3. 添加存储库 URL，类别选择「集成」
4. 搜索「国内油价」并安装
5. 重启 Home Assistant

### 方法二：手动安装

1. 下载 `custom_components/oil_price` 文件夹
2. 复制到 Home Assistant 配置目录的 `custom_components` 下
3. 重启 Home Assistant

## ⚙️ 配置方法

1. 进入 **设置** → **设备与服务** → **添加集成**
2. 搜索「**国内油价**」或「**Oil Price**」
3. 填写配置信息：
   - **省份**：选择你所在的省份
   - **车型名称**：例如 `奔驰GLC300L`（可选）
   - **油箱容量**：例如 `66` 升
   - **常用油品类型**：选择你常用的油品
   - **更新间隔**：默认 3600 秒（1小时）

## 📊 传感器实体

### 油价传感器

| 实体 ID | 描述 | 单位 |
|---------|------|------|
| `sensor.省份_92号汽油` | 92# 汽油价格 | 元/升 |
| `sensor.省份_95号汽油` | 95# 汽油价格 | 元/升 |
| `sensor.省份_98号汽油` | 98# 汽油价格 | 元/升 |
| `sensor.省份_0号柴油` | 0# 柴油价格 | 元/升 |

### 加满油费用传感器

| 实体 ID | 描述 | 单位 |
|---------|------|------|
| `sensor.车型名称_加满油费用` | 加满一箱油的预计费用 | 元 |

**传感器属性：**
- `car_model` - 车型名称
- `tank_size` - 油箱容量
- `fuel_type` - 油品类型
- `unit_price` - 当前单价
- `update_time` - 最后更新时间

## 📝 使用示例

### 仪表盘卡片

```yaml
type: entities
title: 奔驰GLC300L 加油信息
entities:
  - entity: sensor.benzglc300l_jiamanfei
    name: 加满油费用
  - entity: sensor.guangdong_95_qiyou
    name: 95# 汽油单价
```

### 自动化：油价变动通知

```yaml
automation:
  - alias: "油价变动通知"
    trigger:
      - platform: state
        entity_id: sensor.guangdong_95号汽油
    condition:
      - condition: template
        value_template: >
          {{ trigger.from_state.state not in ['unknown', 'unavailable'] 
             and trigger.to_state.state != trigger.from_state.state }}
    action:
      - service: notify.mobile_app_your_phone
        data:
          title: "⛽ 油价变动"
          message: >
            95# 汽油：{{ trigger.from_state.state }} → {{ trigger.to_state.state }} 元/升
            加满一箱油约需：{{ states('sensor.benzglc300l_jiamanfei') }} 元
```

### 自动化：每周一早上发送加油提醒

```yaml
automation:
  - alias: "每周加油提醒"
    trigger:
      - platform: time
        at: "08:00:00"
    condition:
      - condition: time
        weekday:
          - mon
    action:
      - service: notify.mobile_app_your_phone
        data:
          title: "🚗 每周加油提醒"
          message: >
            当前 95# 油价：{{ states('sensor.guangdong_95号汽油') }} 元/升
            奔驰GLC300L 加满预计：{{ states('sensor.benzglc300l_jiamanfei') }} 元
```

## 🗺️ 支持的省份

<details>
<summary>点击查看完整列表</summary>

**直辖市**：北京、上海、天津、重庆

**华北**：河北、山西、内蒙古

**东北**：辽宁、吉林、黑龙江

**华东**：江苏、浙江、安徽、福建、江西、山东

**中南**：河南、湖北、湖南、广东、广西、海南

**西南**：四川、贵州、云南、西藏

**西北**：陕西、甘肃、青海、宁夏、新疆

</details>

## 📌 数据来源

油价数据来源于 [汽油价格网](http://www.qiyoujiage.com/)，数据仅供参考，请以加油站实际价格为准。

## ⚠️ 注意事项

- 油价数据来源于公开网页，可能存在更新延迟
- 加满油费用为预估值，实际费用可能因油箱剩余油量而异
- 建议更新间隔不要低于 10 分钟，避免频繁请求
- 如遇数据获取失败，传感器将显示为不可用状态

## 📄 许可证

MIT License

## 🙏 致谢

感谢 [汽油价格网](http://www.qiyoujiage.com/) 提供的油价数据。
