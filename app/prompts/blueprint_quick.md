# 五行计算

## 输入
性别：${gender}
出生日期：${birth_date}  
出生时间：${birth_time}
出生地点：${birth_location}

## 输出
直接输出JSON，不要思考过程：

```json
{
  "core_energy_field": {
    "title": "核心能量场 | Elemental Composition",
    "description": "这是构成你内在世界的五种基本能量。",
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
