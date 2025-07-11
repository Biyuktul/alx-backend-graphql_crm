import graphene
from graphene_django.types import DjangoObjectType
from .models import Customer, Product, Order
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from graphql import GraphQLError
from decimal import Decimal
from django.utils import timezone
from django.db import transaction
from graphene_django.filter import DjangoFilterConnectionField
from .filters import CustomerFilter, ProductFilter, OrderFilter
from graphene import relay

# ----------------------
# GraphQL TYPES
# ----------------------

class CustomerType(DjangoObjectType):
    name = graphene.String()

    class Meta:
        model = Customer
        interfaces = (relay.Node,)

        filter_fields = {
            'email': ['icontains'],
            'first_name': ['icontains'],
            'created_at': ['gte', 'lte'],
            'phone': ['icontains'],
        }


    def resolve_name(self, info):
        return f"{self.first_name} {self.last_name}".strip()

class ProductType(DjangoObjectType):
    class Meta:
        model = Product
        interfaces = (relay.Node,)

        filter_fields = {
            'name': ['icontains'],
            'price': ['gte', 'lte'],
            'stock': ['gte', 'lte'],
        }

class OrderType(DjangoObjectType):
    class Meta:
        model = Order
        interfaces = (relay.Node,)

        filter_fields = {
            'status': ['exact'],
            'total_amount': ['gte', 'lte'],
            'order_date': ['gte', 'lte', 'exact', 'range'],
            'customer__first_name': ['icontains'],
            'customer__email': ['icontains'],
            'products__name': ['icontains'],
            'products__id': ['exact'],
        }

# ----------------------
# INPUT TYPES
# ----------------------

class CustomerInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    email = graphene.String(required=True)
    phone = graphene.String()

class BulkCustomerInput(graphene.InputObjectType):
    customers = graphene.List(CustomerInput, required=True)

class ProductInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    price = graphene.Decimal(required=True)
    stock = graphene.Int(default_value=0)

class CreateOrderInput(graphene.InputObjectType):
    customer_id = graphene.UUID(required=True)
    product_ids = graphene.List(graphene.UUID, required=True)
    order_date = graphene.DateTime()

# ----------------------
# MUTATIONS
# ----------------------

class CreateCustomer(graphene.Mutation):
    class Arguments:
        input = CustomerInput(required=True)

    customer = graphene.Field(CustomerType)
    message = graphene.String()

    def mutate(self, info, input):
        if Customer.objects.filter(email=input.email).exists():
            raise GraphQLError("Email already exists")

        phone_validator = RegexValidator(r'^(\+\d{1,15}|\d{3}-\d{3}-\d{4})$',
                                         "Invalid phone number format.")
        if input.phone:
            try:
                phone_validator(input.phone)
            except ValidationError:
                raise GraphQLError("Invalid phone number format")

        customer = Customer.objects.create_user(
            username=input.email,
            email=input.email,
            password="default123",
            first_name=input.name,
            phone=input.phone or ""
        )
        return CreateCustomer(customer=customer, message="Customer created successfully.")

class BulkCreateCustomers(graphene.Mutation):
    class Arguments:
        input = BulkCustomerInput(required=True)

    created = graphene.List(CustomerType)
    errors = graphene.List(graphene.String)

    def mutate(self, info, input):
        created = []
        errors = []

        with transaction.atomic():
            for data in input.customers:
                try:
                    if Customer.objects.filter(email=data.email).exists():
                        raise GraphQLError(f"Email {data.email} already exists")

                    customer = Customer.objects.create_user(
                        username=data.email,
                        email=data.email,
                        password="default123",
                        first_name=data.name,
                        phone=data.phone or ""
                    )
                    created.append(customer)
                except Exception as e:
                    errors.append(str(e))

        return BulkCreateCustomers(created=created, errors=errors)

class CreateProduct(graphene.Mutation):
    class Arguments:
        input = ProductInput(required=True)

    product = graphene.Field(ProductType)

    def mutate(self, info, input):
        if input.price <= 0:
            raise GraphQLError("Price must be greater than zero")
        if input.stock < 0:
            raise GraphQLError("Stock cannot be negative")

        product = Product.objects.create(
            name=input.name,
            price=input.price,
            stock=input.stock,
            slug=f"{input.name.lower().replace(' ', '-')}-{Product.objects.count()+1}",
            sku=f"SKU-{Product.objects.count()+1}"
        )
        return CreateProduct(product=product)

class CreateOrder(graphene.Mutation):
    class Arguments:
        input = CreateOrderInput(required=True)

    order = graphene.Field(OrderType)

    def mutate(self, info, input):
        try:
            customer = Customer.objects.get(id=input.customer_id)
        except Customer.DoesNotExist:
            raise GraphQLError("Customer not found")

        products = Product.objects.filter(id__in=input.product_ids)
        if not products:
            raise GraphQLError("No valid products found")

        total = sum([product.price for product in products])

        order = Order.objects.create(
            customer=customer,
            order_number=f"ORD-{Order.objects.count()+1}",
            subtotal=total,
            total_amount=total,
            order_date=input.order_date or timezone.now(),
        )
        order.products.set(products)
        return CreateOrder(order=order)

class UpdateLowStockProducts(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        input = ProductInput(required=True)

    product = graphene.Field(ProductType)
    message = graphene.String()

    def mutate(self, info, name, input):
        try:
            product = Product.objects.get(name=name)
        except Product.DoesNotExist:
            raise GraphQLError("Product with that name does not exist!!")

        product.name = input.name
        product.price = input.price
        product.stock = input.stock

        #Update Stock levels
        if product.stock < 10:
            product.stock += 10
        
        product.save()
        return UpdateLowStockProducts(
            product=product,
            message="Product updated (Stock bumped if below 10)."
            )

# ----------------------
# ROOT QUERY + MUTATION
# ----------------------

class Query(graphene.ObjectType):
    all_customers = DjangoFilterConnectionField(CustomerType, filterset_class=CustomerFilter)
    all_products = DjangoFilterConnectionField(ProductType, filterset_class=ProductFilter)
    all_orders = DjangoFilterConnectionField(OrderType, filterset_class=OrderFilter)

    customers = all_customers
    products = all_products
    orders = all_orders

class Mutation(graphene.ObjectType):
    create_customer = CreateCustomer.Field()
    bulk_create_customers = BulkCreateCustomers.Field()
    create_product = CreateProduct.Field()
    create_order = CreateOrder.Field()
    update_low_stock_products = UpdateLowStockProducts.Field()
