from django import template

register = template.Library()


@register.filter(name='to_percent')
def to_percent(value, decimals=0):
    try:
        pct = float(value) * 100.0
        fmt = f"{{:.{int(decimals)}f}}"
        # Remove trailing .0 if decimals=0
        text = fmt.format(pct)
        if decimals == 0:
            text = text.split('.')[0]
        return text
    except Exception:
        return "0"


