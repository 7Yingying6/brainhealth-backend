from django import template

register = template.Library()

@register.filter(name='uv_index_level')
def uv_index_level(uv_index):
    if uv_index < 3:
        return "Low"
    elif 3 <= uv_index < 6:
        return "Moderate"
    elif 6 <= uv_index < 8:
        return "High"
    elif 8 <= uv_index < 11:
        return "Very High"
    else:
        return "Extreme"