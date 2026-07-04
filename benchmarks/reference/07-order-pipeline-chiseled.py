"""Order pipeline — chiseled version. Minimum that works."""

from decimal import Decimal, ROUND_HALF_UP

DISCOUNT_RATES = {'bronze': 0, 'silver': 0.1, 'gold': 0.2}
TAX_RATES = {'US': 0.08, 'EU': 0.20, 'UK': 0.20, 'JP': 0.10, 'AU': 0.10}

def process_order(order):
    if not order.get('items'):
        return None
    subtotal = sum(
        Decimal(str(i['qty'])) * Decimal(str(i['price']))
        for i in order['items']
    ) + Decimal('0')
    subtotal = subtotal.quantize(Decimal('0.01'), ROUND_HALF_UP)
    discount_rate = DISCOUNT_RATES.get(order.get('tier', 'bronze'), 0.0)
    discount = (subtotal * Decimal(str(discount_rate))).quantize(Decimal('0.01'), ROUND_HALF_UP)
    taxable = subtotal - discount
    tax_rate = TAX_RATES.get(order.get('region', ''), 0.15)
    tax = (taxable * Decimal(str(tax_rate))).quantize(Decimal('0.01'), ROUND_HALF_UP)
    total = (taxable + tax).quantize(Decimal('0.01'), ROUND_HALF_UP)
    return {
        'order_id': order['id'],
        'subtotal': str(subtotal),
        'discount': str(discount),
        'tax': str(tax),
        'total': str(total),
        'items': sum(i['qty'] for i in order['items']),
    }

def process_orders(orders):
    return [r for o in orders if (r := process_order(o))]
