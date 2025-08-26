# crm/schema.py
import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from django.db import transaction
from django.core.exceptions import ValidationError
from .models import Customer, Product, Order
from .filters import CustomerFilter, ProductFilter, OrderFilter
import re
from decimal import Decimal


# GraphQL Types
class CustomerType(DjangoObjectType):
    class Meta:
        model = Customer
        fields = '__all__'
        interfaces = (graphene.relay.Node,)
        filterset_class = CustomerFilter


class ProductType(DjangoObjectType):
    class Meta:
        model = Product
        fields = '__all__'
        interfaces = (graphene.relay.Node,)
        filterset_class = ProductFilter


class OrderType(DjangoObjectType):
    class Meta:
        model = Order
        fields = '__all__'
        interfaces = (graphene.relay.Node,)
        filterset_class = OrderFilter


# Input Types
class CustomerInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    email = graphene.String(required=True)
    phone = graphene.String()


class ProductInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    price = graphene.Decimal(required=True)
    stock = graphene.Int()


class OrderInput(graphene.InputObjectType):
    customer_id = graphene.ID(required=True)
    product_ids = graphene.List(graphene.ID, required=True)
    order_date = graphene.DateTime()


# Mutation Classes
class CreateCustomer(graphene.Mutation):
    class Arguments:
        input = CustomerInput(required=True)

    customer = graphene.Field(CustomerType)
    message = graphene.String()
    success = graphene.Boolean()
    errors = graphene.List(graphene.String)

    @staticmethod
    def validate_phone(phone):
        """Validate phone number format"""
        if phone:
            phone_pattern = r'^(\+\d{10,15}|\d{3}-\d{3}-\d{4}|\d{10,15})$'
            if not re.match(phone_pattern, phone):
                return False
        return True

    @staticmethod
    def mutate(root, info, input=None):
        errors = []
        
        try:
            # Validate email uniqueness
            if Customer.objects.filter(email=input.email).exists():
                errors.append("Email already exists")
            
            # Validate phone format
            if input.phone and not CreateCustomer.validate_phone(input.phone):
                errors.append("Phone number must be in format +1234567890 or 123-456-7890")
            
            if errors:
                return CreateCustomer(
                    customer=None,
                    message="Validation failed",
                    success=False,
                    errors=errors
                )
            
            # Create customer
            customer = Customer.objects.create(
                name=input.name,
                email=input.email,
                phone=input.phone or None
            )
            
            return CreateCustomer(
                customer=customer,
                message="Customer created successfully",
                success=True,
                errors=[]
            )
            
        except Exception as e:
            return CreateCustomer(
                customer=None,
                message="Failed to create customer",
                success=False,
                errors=[str(e)]
            )


class BulkCreateCustomers(graphene.Mutation):
    class Arguments:
        input = graphene.List(CustomerInput, required=True)

    customers = graphene.List(CustomerType)
    errors = graphene.List(graphene.String)
    success_count = graphene.Int()
    error_count = graphene.Int()

    @staticmethod
    def mutate(root, info, input=None):
        customers_created = []
        errors = []
        
        try:
            with transaction.atomic():
                for i, customer_input in enumerate(input):
                    try:
                        # Validate email uniqueness
                        if Customer.objects.filter(email=customer_input.email).exists():
                            errors.append(f"Row {i+1}: Email {customer_input.email} already exists")
                            continue
                        
                        # Validate phone format
                        if customer_input.phone and not CreateCustomer.validate_phone(customer_input.phone):
                            errors.append(f"Row {i+1}: Invalid phone format for {customer_input.email}")
                            continue
                        
                        # Create customer
                        customer = Customer.objects.create(
                            name=customer_input.name,
                            email=customer_input.email,
                            phone=customer_input.phone or None
                        )
                        customers_created.append(customer)
                        
                    except Exception as e:
                        errors.append(f"Row {i+1}: {str(e)}")
            
            return BulkCreateCustomers(
                customers=customers_created,
                errors=errors,
                success_count=len(customers_created),
                error_count=len(errors)
            )
            
        except Exception as e:
            return BulkCreateCustomers(
                customers=[],
                errors=[str(e)],
                success_count=0,
                error_count=1
            )


class CreateProduct(graphene.Mutation):
    class Arguments:
        input = ProductInput(required=True)

    product = graphene.Field(ProductType)
    message = graphene.String()
    success = graphene.Boolean()
    errors = graphene.List(graphene.String)

    @staticmethod
    def mutate(root, info, input=None):
        errors = []
        
        try:
            # Validate price
            if input.price <= 0:
                errors.append("Price must be positive")
            
            # Validate stock
            stock = input.stock if input.stock is not None else 0
            if stock < 0:
                errors.append("Stock cannot be negative")
            
            if errors:
                return CreateProduct(
                    product=None,
                    message="Validation failed",
                    success=False,
                    errors=errors
                )
            
            # Create product
            product = Product.objects.create(
                name=input.name,
                price=input.price,
                stock=stock
            )
            
            return CreateProduct(
                product=product,
                message="Product created successfully",
                success=True,
                errors=[]
            )
            
        except Exception as e:
            return CreateProduct(
                product=None,
                message="Failed to create product",
                success=False,
                errors=[str(e)]
            )


class CreateOrder(graphene.Mutation):
    class Arguments:
        input = OrderInput(required=True)

    order = graphene.Field(OrderType)
    message = graphene.String()
    success = graphene.Boolean()
    errors = graphene.List(graphene.String)

    @staticmethod
    def mutate(root, info, input=None):
        errors = []
        
        try:
            # Validate customer exists
            try:
                customer = Customer.objects.get(id=input.customer_id)
            except Customer.DoesNotExist:
                errors.append("Customer not found")
            
            # Validate products exist
            if not input.product_ids:
                errors.append("At least one product must be selected")
            else:
                product_ids = [int(pid) for pid in input.product_ids]
                products = Product.objects.filter(id__in=product_ids)
                
                if len(products) != len(product_ids):
                    missing_ids = set(product_ids) - set(products.values_list('id', flat=True))
                    errors.append(f"Products not found: {list(missing_ids)}")
            
            if errors:
                return CreateOrder(
                    order=None,
                    message="Validation failed",
                    success=False,
                    errors=errors
                )
            
            # Create order
            with transaction.atomic():
                order = Order.objects.create(
                    customer=customer,
                    order_date=input.order_date
                )
                
                # Add products to order
                order.products.set(products)
                
                # Calculate and save total amount
                order.total_amount = order.calculate_total()
                order.save(update_fields=['total_amount'])
            
            return CreateOrder(
                order=order,
                message="Order created successfully",
                success=True,
                errors=[]
            )
            
        except Exception as e:
            return CreateOrder(
                order=None,
                message="Failed to create order",
                success=False,
                errors=[str(e)]
            )


class UpdateLowStockProducts(graphene.Mutation):
    class Arguments:
        increment = graphene.Int(required=True)

    success = graphene.String()
    updated_products = graphene.List(ProductType)

    def mutate(self, info, increment):
        low_stock_products = Product.objects.filter(stock__lt=10)
        updated_products = []

        for product in low_stock_products:
            product.stock += increment
            product.save()
            updated_products.append(product)

        return UpdateLowStockProducts(
            success=f"Restocked {len(updated_products)} products.",
            updated_products=updated_products
        )


# Query Class
class Query(graphene.ObjectType):
    hello = graphene.String()
    
    # Simple list queries (existing)
    customers = graphene.List(CustomerType)
    products = graphene.List(ProductType)
    orders = graphene.List(OrderType)
    
    # Single object queries (existing)
    customer = graphene.Field(CustomerType, id=graphene.ID())
    product = graphene.Field(ProductType, id=graphene.ID())
    order = graphene.Field(OrderType, id=graphene.ID())
    
    # Filtered connection queries (new)
    all_customers = DjangoFilterConnectionField(CustomerType)
    all_products = DjangoFilterConnectionField(ProductType)
    all_orders = DjangoFilterConnectionField(OrderType)

    def resolve_hello(self, info):
        return "Hello, GraphQL!"
    
    def resolve_customers(self, info):
        return Customer.objects.all()
    
    def resolve_products(self, info):
        return Product.objects.all()
    
    def resolve_orders(self, info):
        return Order.objects.all()
    
    def resolve_customer(self, info, id):
        try:
            return Customer.objects.get(id=id)
        except Customer.DoesNotExist:
            return None
    
    def resolve_product(self, info, id):
        try:
            return Product.objects.get(id=id)
        except Product.DoesNotExist:
            return None
    
    def resolve_order(self, info, id):
        try:
            return Order.objects.get(id=id)
        except Order.DoesNotExist:
            return None


# Mutation Class
class Mutation(graphene.ObjectType):
    create_customer = CreateCustomer.Field()
    bulk_create_customers = BulkCreateCustomers.Field()
    create_product = CreateProduct.Field()
    create_order = CreateOrder.Field()
    update_low_stock_products = UpdateLowStockProducts.Field()