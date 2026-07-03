from django import template

register = template.Library()


@register.filter
def pkr(amount):
    try:
        val = float(amount)
        return f"PKR {val:,.2f}"
    except (ValueError, TypeError):
        return "PKR 0.00"


@register.filter
def category_color(category):
    colors = {
        "Food": "bg-orange-100 text-orange-800",
        "Transport": "bg-blue-100 text-blue-800",
        "Shopping": "bg-purple-100 text-purple-800",
        "Utility": "bg-yellow-100 text-yellow-800",
        "Health": "bg-red-100 text-red-800",
        "Other": "bg-gray-100 text-gray-800",
    }
    return colors.get(category, "bg-gray-100 text-gray-800")
