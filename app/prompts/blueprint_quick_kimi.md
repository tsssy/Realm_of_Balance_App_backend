# Five Elements Calculation

Calculate Five Elements distribution for:
- Gender: ${gender}
- Birth Date: ${birth_date}
- Birth Time: ${birth_time}
- Birth Location: ${birth_location}

Return ONLY this JSON format:

```json
{
  "core_energy_field": {
    "title": "Elemental Composition",
    "description": "These are the five fundamental energies that form your inner world.",
    "chart_data": [
      {"axis": "Metal", "value": 25},
      {"axis": "Wood", "value": 15},
      {"axis": "Water", "value": 30},
      {"axis": "Fire", "value": 20},
      {"axis": "Earth", "value": 10}
    ]
  }
}
```

Requirements:
- Values must be 0-100
- JSON format only
- No other text
