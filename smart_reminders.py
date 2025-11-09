from collections import defaultdict
from datetime import datetime
from typing import List, Dict
from models import PurchaseRecord

def update_purchase_patterns(history: List[PurchaseRecord]) -> Dict[str, float]:
    item_dates = defaultdict(list)
    for record in history:
        item_name = record.item_name.lower().strip()
        item_dates[item_name].append(record.purchase_date)

    patterns = {}
    
    #calculate pattern
    for item_name, dates in item_dates.items():
        if len(dates) < 2:
            continue
            
        dates.sort()
        
        intervals = []
        for i in range(len(dates) - 1):
            time_delta = dates[i+1] - dates[i]
            intervals.append(time_delta.days)
            
        if not intervals:
            continue
            
        avg_interval = sum(intervals) / len(intervals)
        
        patterns[item_name] = avg_interval
        
    return patterns

def get_latest_purchase_dates(history: List[PurchaseRecord]) -> Dict[str, datetime]:
    """Finds the most recent purchase date for every item."""
    latest_dates = {}
    for record in history:
        item_name = record.item_name.lower().strip()
        if item_name not in latest_dates or record.purchase_date > latest_dates[item_name]:
            latest_dates[item_name] = record.purchase_date
    return latest_dates