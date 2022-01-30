from datetime import datetime, date, timedelta


def candle_interval_generator(start_date, end_date):
    diff = (end_date - start_date).days
    if diff <= 2:
        labels = ['1m', '3m', '5m']
    elif diff <= 7:
        labels = ['3m', '5m', '15m']
    elif diff <= 14:
        labels = ['5m', '15m', '30m', '45m', '1h']
    else:
        labels = ['15m', '30m', '45m', '1h']

    return [{'label': x, 'value': x} for x in labels]


def get_db_timestamp(interval: str):
    """Generates formatted-timestamp for db queries based on an interval"""
    if interval == 'today':
        dt = date.today()
    elif interval == 'week':
        dt = date.today()
        dt = dt - timedelta(days=dt.weekday())
    elif interval == 'month':
        dt = date.today().replace(day=1)
    else:
        dt = date.today().replace(day=1, month=1)
    
    dt = datetime.combine(dt, datetime.min.time())
    tmstmp = dt.timestamp() * 1000

    return tmstmp