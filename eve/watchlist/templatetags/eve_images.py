from django import template

register = template.Library()

EVE_IMAGE_SERVER = "https://images.evetech.net"


@register.filter
def eve_icon(type_id, size=32):
    return f"{EVE_IMAGE_SERVER}/types/{type_id}/icon?size={size}"
