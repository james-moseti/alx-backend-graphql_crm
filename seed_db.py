import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alx_backend_graphql_crm.settings')
django.setup()

from crm.models import Customer, Product, Order

# Create customers
customers = [
    Customer.objects.create(name="John", email="john@example.com", phone="+1234867890"),
    Customer.objects.create(name="Bob", email="bob@example.com", phone="123-456-7890"),
    Customer.objects.create(name="Carol", email="carol@example.com"),
]

# Create products
products = [
    Product.objects.create(name="Laptop", price=999.99, stock=10),
    Product.objects.create(name="Mouse", price=25.50, stock=50),
    Product.objects.create(name="Keyboard", price=75.00, stock=30),
]

# Create orders
order1 = Order.objects.create(customer=customers[0])
order1.products.set([products[0], products[1]])

order2 = Order.objects.create(customer=customers[1])
order2.products.set([products[2]])

print("Database seeded successfully!")
print(f"Created {len(customers)} customers, {len(products)} products, and 2 orders.")