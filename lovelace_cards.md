# 🚗 油价仪表盘配置

将以下代码添加到你的 Home Assistant 仪表盘中。

## 方法一：完整油价卡片组

```yaml
type: vertical-stack
cards:
  # 标题卡片
  - type: markdown
    content: |
      ## ⛽ 今日油价
      <ha-icon icon="mdi:map-marker"></ha-icon> 广东省
    card_mod:
      style: |
        ha-card {
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          color: white;
          border-radius: 16px;
        }

  # 油价展示卡片
  - type: horizontal-stack
    cards:
      - type: custom:mushroom-entity-card
        entity: sensor.guangdong_92hao_qiyou
        name: 92#
        icon: mdi:gas-station
        icon_color: green
        primary_info: name
        secondary_info: state
        layout: vertical
        card_mod:
          style: |
            ha-card {
              background: rgba(76, 175, 80, 0.1);
              border: 1px solid rgba(76, 175, 80, 0.3);
              border-radius: 12px;
            }
      
      - type: custom:mushroom-entity-card
        entity: sensor.guangdong_95hao_qiyou
        name: 95#
        icon: mdi:gas-station
        icon_color: blue
        primary_info: name
        secondary_info: state
        layout: vertical
        card_mod:
          style: |
            ha-card {
              background: rgba(33, 150, 243, 0.1);
              border: 1px solid rgba(33, 150, 243, 0.3);
              border-radius: 12px;
            }
      
      - type: custom:mushroom-entity-card
        entity: sensor.guangdong_98hao_qiyou
        name: 98#
        icon: mdi:gas-station
        icon_color: purple
        primary_info: name
        secondary_info: state
        layout: vertical
        card_mod:
          style: |
            ha-card {
              background: rgba(156, 39, 176, 0.1);
              border: 1px solid rgba(156, 39, 176, 0.3);
              border-radius: 12px;
            }
      
      - type: custom:mushroom-entity-card
        entity: sensor.guangdong_0hao_chaiyou
        name: 0#柴油
        icon: mdi:barrel
        icon_color: orange
        primary_info: name
        secondary_info: state
        layout: vertical
        card_mod:
          style: |
            ha-card {
              background: rgba(255, 152, 0, 0.1);
              border: 1px solid rgba(255, 152, 0, 0.3);
              border-radius: 12px;
            }

  # 加满油费用卡片
  - type: custom:mushroom-template-card
    primary: 奔驰GLC300L 加满油
    secondary: |
      💰 预计 {{ states('sensor.benzglc300l_jiaman_you_feiyong') }} 元
    icon: mdi:car
    icon_color: red
    card_mod:
      style: |
        ha-card {
          background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
          color: white;
          border-radius: 12px;
        }
        .primary {
          font-weight: bold;
        }
        .secondary {
          font-size: 1.2em !important;
        }
```

---

## 方法二：简洁表格样式（无需额外插件）

```yaml
type: entities
title: ⛽ 广东今日油价
show_header_toggle: false
entities:
  - entity: sensor.guangdong_92hao_qiyou
    name: 92# 汽油
    icon: mdi:gas-station
  - entity: sensor.guangdong_95hao_qiyou
    name: 95# 汽油
    icon: mdi:gas-station
  - entity: sensor.guangdong_98hao_qiyou
    name: 98# 汽油
    icon: mdi:gas-station
  - entity: sensor.guangdong_0hao_chaiyou
    name: 0# 柴油
    icon: mdi:barrel
  - type: divider
  - entity: sensor.benzglc300l_jiaman_you_feiyong
    name: 🚗 奔驰GLC300L 加满
    icon: mdi:currency-cny
```

---

## 方法三：Gauge 仪表盘样式

```yaml
type: vertical-stack
cards:
  - type: markdown
    content: "## ⛽ 油价监控"
  
  - type: horizontal-stack
    cards:
      - type: gauge
        entity: sensor.guangdong_92hao_qiyou
        name: 92#
        min: 5
        max: 10
        severity:
          green: 5
          yellow: 7
          red: 8
      - type: gauge
        entity: sensor.guangdong_95hao_qiyou
        name: 95#
        min: 5
        max: 10
        severity:
          green: 5
          yellow: 7.5
          red: 8.5
  
  - type: horizontal-stack
    cards:
      - type: gauge
        entity: sensor.guangdong_98hao_qiyou
        name: 98#
        min: 6
        max: 12
        severity:
          green: 6
          yellow: 9
          red: 10
      - type: gauge
        entity: sensor.guangdong_0hao_chaiyou
        name: 0#柴油
        min: 5
        max: 10
        severity:
          green: 5
          yellow: 7
          red: 8
```

---

## 方法四：迷你按钮卡片组

```yaml
type: grid
columns: 2
square: false
cards:
  - type: button
    entity: sensor.guangdong_92hao_qiyou
    name: 92# 汽油
    icon: mdi:gas-station
    show_state: true
    tap_action:
      action: more-info
  - type: button
    entity: sensor.guangdong_95hao_qiyou
    name: 95# 汽油
    icon: mdi:gas-station
    show_state: true
    tap_action:
      action: more-info
  - type: button
    entity: sensor.guangdong_98hao_qiyou
    name: 98# 汽油
    icon: mdi:gas-station
    show_state: true
    tap_action:
      action: more-info
  - type: button
    entity: sensor.benzglc300l_jiaman_you_feiyong
    name: 加满油费用
    icon: mdi:currency-cny
    show_state: true
    tap_action:
      action: more-info
```

---

## 🔧 需要安装的插件（方法一需要）

通过 HACS 安装：
- **Mushroom Cards** - 现代化卡片组件
- **card-mod** - 卡片样式自定义

---

## 📝 注意事项

1. 请根据实际的传感器 entity_id 替换示例中的实体名称
2. 在 Home Assistant → 开发者工具 → 状态 中查看正确的实体ID
3. 方法二不需要任何额外插件，开箱即用
