# Five Elements Calculation Instructions

## Task
Calculate Five Elements distribution based on user's birth information.

## Input
- Gender: ${gender}
- Birth Date: ${birth_date}
- Birth Time: ${birth_time}
- Birth Location: ${birth_location}

## Calculation Requirements
1. Calculate Five Elements strength of the four pillars (Ba Zi)
2. Generate Five Elements distribution chart data

## Output Format
Strictly follow this JSON format:

```json
{
  "core_energy_field": {
    "title": "Elemental Composition",
    "description": "These are the five fundamental energies that form your inner world.",
    "chart_data": [
      {"axis": "Metal", "value": numeric_value},
      {"axis": "Wood", "value": numeric_value},
      {"axis": "Water", "value": numeric_value},
      {"axis": "Fire", "value": numeric_value},
      {"axis": "Earth", "value": numeric_value}
    ]
  }
}
```

## Requirements
- Output only Five Elements calculation, no other content
- Value range: 0-100
- Strictly follow JSON format
- All output content must be in English
