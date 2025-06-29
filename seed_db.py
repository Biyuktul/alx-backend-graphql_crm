# scripts/seed_data.py
import os
import django
import random
from faker import Faker
from decimal import Decimal

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "alx_backend_graphql_crm.settings")
django.setup()

from crm.models import Customer, Product, Order

fake = Faker()

def seed_customers(n=50):
    print(f"Seeding {n} customers...")
    for _ in range(n):
        email = fake.unique.email()
        Customer.objects.create_user(
            username=email,
            email=email,
            password="default123",
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            phone=fake.phone_number()
        )

def seed_products(n=50):
    print(f"Seeding {n} products...")
    for _ in range(n):
        name = fake.unique.word().capitalize() + " " + fake.word().capitalize()
        Product.objects.create(
            name=name,
            slug=f"{name.lower().replace(' ', '-')}-{random.randint(1000, 9999)}",
            sku=f"SKU-{random.randint(1000, 9999)}",
            price=round(Decimal(random.uniform(10.00, 1000.00)), 2),
            stock=random.randint(0, 50),
            category=fake.word().capitalize()
        )

def seed_orders(n=50):
    print(f"Seeding {n} orders...")
    customers = list(Customer.objects.all())
    products = list(Product.objects.all())

    for _ in range(n):
        customer = random.choice(customers)
        order_products = random.sample(products, random.randint(1, 3))
        total = sum([p.price for p in order_products])

        order = Order.objects.create(
            customer=customer,
            order_number=f"ORD-{Order.objects.count()+1}",
            subtotal=total,
            total_amount=total,
        )
        order.products.set(order_products)

if __name__ == "__main__":
    seed_customers(50)
    seed_products(50)
    seed_orders(50)
    print("✅ Seeding complete.")
