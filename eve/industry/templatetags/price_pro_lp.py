from django import template

register = template.Library()

@register.filter
def price_pro_lp(value):
    isk_income = (value.type_id.market_prices.adjusted_price
        if value.type_id and hasattr(value.type_id, 'market_prices')
        else 0)
    blueprint_cost = getattr(value, 'isk_cost', 0)
    other_costs = getattr(value, 'material_cost', 0)

    if other_costs is None:
        other_costs = 0
    else:
        other_costs = other_costs
    lp = getattr(value, 'lp_cost', 1)
    if lp == 0:
        lp = 1
    result = (isk_income - blueprint_cost - other_costs)/lp

    return result