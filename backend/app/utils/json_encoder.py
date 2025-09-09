"""
Custom JSON encoder for handling numpy and pandas data types
"""
import json
import numpy as np
import pandas as pd
from datetime import datetime, date
from typing import Any
import math

class CustomJSONEncoder(json.JSONEncoder):
    """Custom JSON encoder to handle numpy and pandas data types"""
    
    def default(self, obj: Any) -> Any:
        # Handle numpy data types
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            # Handle NaN and Inf values
            if np.isnan(obj) or np.isinf(obj):
                return None
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, np.bool_):
            return bool(obj)
        
        # Handle pandas data types
        elif isinstance(obj, pd.Timestamp):
            return obj.isoformat()
        elif isinstance(obj, pd.Series):
            return obj.to_dict()
        elif isinstance(obj, pd.DataFrame):
            return obj.to_dict('records')
        
        # Handle Python datetime objects
        elif isinstance(obj, (datetime, date)):
            return obj.isoformat()
        
        # Handle float NaN and Inf values
        elif isinstance(obj, float):
            if math.isnan(obj) or math.isinf(obj):
                return None
            return obj
            
        return super().default(obj)

def clean_data_for_json(data: Any) -> Any:
    """
    Recursively clean data to make it JSON serializable
    """
    if isinstance(data, dict):
        return {key: clean_data_for_json(value) for key, value in data.items()}
    elif isinstance(data, (list, tuple)):
        return [clean_data_for_json(item) for item in data]
    elif isinstance(data, np.integer):
        return int(data)
    elif isinstance(data, np.floating):
        if np.isnan(data) or np.isinf(data):
            return None
        return float(data)
    elif isinstance(data, np.ndarray):
        return clean_data_for_json(data.tolist())
    elif isinstance(data, np.bool_):
        return bool(data)
    elif isinstance(data, pd.Timestamp):
        return data.isoformat()
    elif isinstance(data, (datetime, date)):
        return data.isoformat()
    elif isinstance(data, float):
        if math.isnan(data) or math.isinf(data):
            return None
        return data
    else:
        return data
