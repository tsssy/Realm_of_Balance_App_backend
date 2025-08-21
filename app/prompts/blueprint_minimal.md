# 个人蓝图生成

根据用户信息生成个人蓝图：

性别：${gender}
出生日期：${birth_date}
出生时间：${birth_time}
出生地点：${birth_location}

请输出JSON格式：

```json
{
  "bazi": {
    "year_pillar": {"heavenly_stem": "天干", "earthly_branch": "地支"},
    "month_pillar": {"heavenly_stem": "天干", "earthly_branch": "地支"},
    "day_pillar": {"heavenly_stem": "天干", "earthly_branch": "地支"},
    "hour_pillar": {"heavenly_stem": "天干", "earthly_branch": "地支"}
  },
  "elemental_profile": {
    "metal": {"strength": 25, "characteristics": ["精确", "逻辑"]},
    "wood": {"strength": 15, "characteristics": ["生长", "创造"]},
    "water": {"strength": 30, "characteristics": ["智慧", "适应"]},
    "fire": {"strength": 20, "characteristics": ["热情", "领导"]},
    "earth": {"strength": 10, "characteristics": ["稳定", "承载"]}
  },
  "core_analysis": {
    "dominant_element": "water",
    "weakest_element": "earth",
    "personality_traits": ["深刻的同理心", "灵活的适应力", "卓越的沟通力"],
    "life_guidance": "你的人生指导内容"
  }
}
```
