import random
from datetime import timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.catalog.models import Category, Product
from apps.customers.models import Customer
from apps.orders.models import Order, OrderItem, Payment, Refund


class Command(BaseCommand):
    help = "Seed the database with deterministic ecommerce demo data"

    def handle(self, *args, **options):
        random.seed(42)

        self.stdout.write("Clearing existing demo data...")

        Refund.objects.all().delete()
        Payment.objects.all().delete()
        OrderItem.objects.all().delete()
        Order.objects.all().delete()
        Product.objects.all().delete()
        Category.objects.all().delete()
        Customer.objects.all().delete()

        self.stdout.write("Creating categories...")

        category_names = [
            "Electronics",
            "Home",
            "Clothing",
            "Books",
            "Sports",
            "Beauty",
        ]

        categories = [Category(name=name) for name in category_names]

        Category.objects.bulk_create(categories)

        categories = list(Category.objects.all())

        self.stdout.write("Creating products...")

        products = []

        for category in categories:
            for index in range(20):
                products.append(
                    Product(
                        name=f"{category.name} Product {index + 1}",
                        category=category,
                        price=Decimal(random.randint(1000, 100000)) / 100,
                    )
                )

        Product.objects.bulk_create(products)

        products = list(Product.objects.select_related("category"))

        self.stdout.write("Creating customers...")

        countries = [
            "United States",
            "Germany",
            "United Kingdom",
            "France",
            "Poland",
            "Ukraine",
        ]

        customers = [
            Customer(
                email=f"customer{i}@example.com",
                country=random.choice(countries),
            )
            for i in range(1000)
        ]

        Customer.objects.bulk_create(customers)

        customers = list(Customer.objects.all())

        self.stdout.write("Creating orders...")

        now = timezone.now()

        orders = []

        for _ in range(5000):
            created_at = now - timedelta(
                days=random.randint(0, 365),
                hours=random.randint(0, 23),
            )

            orders.append(
                Order(
                    customer=random.choice(customers),
                    status=Order.Status.COMPLETED,
                    created_at=created_at,
                )
            )

        Order.objects.bulk_create(orders)

        orders = list(Order.objects.all())

        self.stdout.write("Creating order items...")

        order_items = []

        for order in orders:
            for _ in range(random.randint(1, 5)):
                product = random.choice(products)

                order_items.append(
                    OrderItem(
                        order=order,
                        product=product,
                        quantity=random.randint(1, 3),
                        unit_price=product.price,
                    )
                )

        OrderItem.objects.bulk_create(order_items)

        self.stdout.write("Creating payments...")

        payments = []

        items_by_order = {}

        for item in order_items:
            items_by_order.setdefault(
                item.order_id,
                [],
            ).append(item)

        for order in orders:
            items = items_by_order.get(order.id, [])

            total = sum(item.unit_price * item.quantity for item in items)

            payments.append(
                Payment(
                    order=order,
                    amount=total,
                    status=Payment.Status.SUCCESS,
                    paid_at=order.created_at,
                )
            )

        Payment.objects.bulk_create(payments)

        self.stdout.write(self.style.SUCCESS("Demo data created successfully."))
