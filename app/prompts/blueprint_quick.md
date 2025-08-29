# 五行计算指令

## 任务
基于用户出生信息计算五行元素分布。

## 输入
- 性别：${gender}
- 出生日期：${birth_date}  
- 出生时间：${birth_time}
- 出生地点：${birth_location}

## 计算要求
1. 计算八字四柱的五行强度
2. 生成五行分布图表数据

## 输出格式
严格按照以下JSON格式输出：

```json
{
  "core_energy_field": {
    "title": "Elemental Composition",
    "description": "These are the five fundamental energies that form your inner world.",
    "chart_data": [
      {"axis": "金 | Metal", "value": 数值},
      {"axis": "木 | Wood", "value": 数值},
      {"axis": "水 | Water", "value": 数值},
      {"axis": "火 | Fire", "value": 数值},
      {"axis": "土 | Earth", "value": 数值}
    ]
  }
}
```

## 要求
- 只输出五行计算，不要其他内容
- 数值范围：0-100
- 严格按照JSON格式
- 确保输出的所有内容是英文。这非常重要
