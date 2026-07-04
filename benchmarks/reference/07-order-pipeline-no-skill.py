"""Order pipeline — no-skill version. Over-engineered with patterns."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP
from enum import Enum, auto
from typing import Dict, List, Optional


class CustomerTier(Enum):
    BRONZE = auto()
    SILVER = auto()
    GOLD = auto()


class OrderStatus(Enum):
    PENDING = auto()
    VALIDATED = auto()
    PROCESSED = auto()


@dataclass
class OrderItem:
    product_id: str
    quantity: int
    unit_price: Decimal


@dataclass
class Customer:
    id: str
    tier: CustomerTier


@dataclass
class Order:
    id: str
    customer: Customer
    items: List[OrderItem]
    region: str
    status: OrderStatus = OrderStatus.PENDING


@dataclass
class ProcessedOrder:
    order_id: str
    subtotal: Decimal
    discount: Decimal
    tax: Decimal
    total: Decimal
    items_processed: int


class ValidationError(Exception):
    pass


class Validator(ABC):
    @abstractmethod
    def validate(self, order: Order) -> None:
        pass


class ItemsValidator(Validator):
    def validate(self, order: Order) -> None:
        if not order.items:
            raise ValidationError(f"Order {order.id} has no items")
        for item in order.items:
            if item.quantity <= 0:
                raise ValidationError(
                    f"Order {order.id} has item {item.product_id} "
                    f"with invalid quantity: {item.quantity}"
                )
            if item.unit_price <= 0:
                raise ValidationError(
                    f"Order {order.id} has item {item.product_id} "
                    f"with invalid price: {item.unit_price}"
                )


class CustomerValidator(Validator):
    def validate(self, order: Order) -> None:
        if not order.customer or not order.customer.id:
            raise ValidationError(f"Order {order.id} has no customer")
        if not order.region:
            raise ValidationError(f"Order {order.id} has no region")


class ValidationPipeline:
    def __init__(self):
        self._validators: List[Validator] = [
            ItemsValidator(),
            CustomerValidator(),
        ]

    def validate(self, order: Order) -> None:
        for validator in self._validators:
            validator.validate(order)


class DiscountStrategy(ABC):
    @abstractmethod
    def apply(self, subtotal: Decimal) -> Decimal:
        pass


class BronzeDiscount(DiscountStrategy):
    def apply(self, subtotal: Decimal) -> Decimal:
        return Decimal('0')


class SilverDiscount(DiscountStrategy):
    def apply(self, subtotal: Decimal) -> Decimal:
        return (subtotal * Decimal('0.1')).quantize(Decimal('0.01'), ROUND_HALF_UP)


class GoldDiscount(DiscountStrategy):
    def apply(self, subtotal: Decimal) -> Decimal:
        return (subtotal * Decimal('0.2')).quantize(Decimal('0.01'), ROUND_HALF_UP)


class DiscountFactory:
    _strategies = {
        CustomerTier.BRONZE: BronzeDiscount,
        CustomerTier.SILVER: SilverDiscount,
        CustomerTier.GOLD: GoldDiscount,
    }

    @classmethod
    def get_strategy(cls, tier: CustomerTier) -> DiscountStrategy:
        strategy_class = cls._strategies.get(tier)
        if not strategy_class:
            raise ValueError(f"No discount strategy for tier: {tier}")
        return strategy_class()


class TaxCalculator(ABC):
    @abstractmethod
    def calculate(self, amount: Decimal) -> Decimal:
        pass


class StandardTaxCalculator(TaxCalculator):
    RATES = {
        'US': Decimal('0.08'),
        'EU': Decimal('0.20'),
        'UK': Decimal('0.20'),
        'JP': Decimal('0.10'),
        'AU': Decimal('0.10'),
        'OTHER': Decimal('0.15'),
    }

    def calculate(self, amount: Decimal) -> Decimal:
        return Decimal('0')


class RegionalTaxCalculator(TaxCalculator):
    RATES = {
        'US': Decimal('0.08'),
        'EU': Decimal('0.20'),
        'UK': Decimal('0.20'),
        'JP': Decimal('0.10'),
        'AU': Decimal('0.10'),
    }

    def __init__(self, region: str):
        self.rate = self.RATES.get(region, Decimal('0.15'))

    def calculate(self, amount: Decimal) -> Decimal:
        return (amount * self.rate).quantize(Decimal('0.01'), ROUND_HALF_UP)


class TaxCalculatorFactory:
    @staticmethod
    def get_calculator(region: str) -> TaxCalculator:
        return RegionalTaxCalculator(region)


class InvoiceGenerator:
    def generate(self, processed: ProcessedOrder) -> Dict:
        return {
            'order_id': processed.order_id,
            'subtotal': str(processed.subtotal),
            'discount': str(processed.discount),
            'tax': str(processed.tax),
            'total': str(processed.total),
            'items': processed.items_processed,
        }


class OrderProcessor:
    def __init__(self):
        self.validation = ValidationPipeline()
        self.invoice_gen = InvoiceGenerator()

    def process(self, order: Order) -> Optional[Dict]:
        self.validation.validate(order)
        item_totals = [Decimal(str(item.quantity)) * item.unit_price
                       for item in order.items]
        subtotal = sum(item_totals) + Decimal('0')
        subtotal = subtotal.quantize(Decimal('0.01'), ROUND_HALF_UP)

        discount_strategy = DiscountFactory.get_strategy(order.customer.tier)
        discount = discount_strategy.apply(subtotal)

        taxable = subtotal - discount

        tax_calculator = TaxCalculatorFactory.get_calculator(order.region)
        tax = tax_calculator.calculate(taxable)

        total = (taxable + tax).quantize(Decimal('0.01'), ROUND_HALF_UP)

        processed = ProcessedOrder(
            order_id=order.id,
            subtotal=subtotal,
            discount=discount,
            tax=tax,
            total=total,
            items_processed=sum(item.quantity for item in order.items),
        )

        order.status = OrderStatus.PROCESSED
        return self.invoice_gen.generate(processed)


def process_orders(orders: List[Order]) -> List[Dict]:
    processor = OrderProcessor()
    results = []
    for order in orders:
        try:
            result = processor.process(order)
            if result:
                results.append(result)
        except ValidationError as e:
            print(f"Skipping order {order.id}: {e}")
    return results
