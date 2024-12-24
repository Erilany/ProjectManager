from django import template
from datetime import datetime, timedelta

register = template.Library()

@register.filter
def debug(value):
    print(f"Debug value: {value}")
    return value

@register.filter
def multiply(value, arg):
    """Multiplie la valeur par l'argument"""
    try:
        result = int(value) * int(arg)
        print(f"Multiply: {value} * {arg} = {result}")
        return result
    except (ValueError, TypeError):
        return ''

@register.filter
def is_start_day(subtask, date):
    if isinstance(date, datetime):
        date = date.date()
    result = subtask.start_date == date
    print(f"DEBUG - is_start_day: subtask={subtask.subject}, date={date}, start_date={subtask.start_date}, result={result}")
    return result

@register.filter
def is_active_day(subtask, date):
    if isinstance(date, datetime):
        date = date.date()
    if not subtask.start_date or not subtask.end_date:
        return False
    return subtask.start_date <= date <= subtask.end_date

@register.filter
def duration_days(subtask):
    if not subtask.start_date or not subtask.end_date:
        return 1
    duration = (subtask.end_date - subtask.start_date).days + 1
    print(f"DEBUG - duration_days: subtask={subtask.subject}, start={subtask.start_date}, end={subtask.end_date}, duration={duration}")
    return duration