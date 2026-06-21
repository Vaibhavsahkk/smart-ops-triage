import os, sys
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(PROJECT_ROOT)
sys.path.insert(0, PROJECT_ROOT)

import pandas as pd
from config import EXPORT_DIR

os.makedirs(EXPORT_DIR, exist_ok=True)

dates = pd.date_range(start='2024-01-01', end='2026-12-31', freq='D')
df_calendar = pd.DataFrame({
    'Date': dates,
    'Day': dates.day,
    'Month': dates.month,
    'MonthName': dates.strftime('%B'),
    'Quarter': dates.quarter,
    'Year': dates.year,
    'Week': dates.isocalendar().week,
    'DayOfWeek': dates.day_name()
})
df_calendar.to_csv(os.path.join(EXPORT_DIR, 'calendar.csv'), index=False)
print(f"Calendar generated with {len(df_calendar)} dates.")
