#!/bin/bash

python manage.py shell <<EOF
from datetime import timedelta
from django.utils import timezone
from crm.models import Customer, Order
import logging

logger = logging.getLogger('deletion_logger')
logger.setLevel(logging.INFO)

fh = logging.FileHandler('crm/tmp/customer_cleanup_log.txt')

formatter = logging.Formatter('%(asctime)s - %(message)s')
fh.setFormatter(formatter)

logger.addHandler(fh)

one_year_old = timezone.now() - timedelta(days=365)

recent_customers = Customer.objects.filter(orders__order_date__gte=one_year_old).distinct()

to_delete = Customer.objects.exclude(id__in=recent_customers)

for customer in to_delete:
    logger.info(f"Deleting Customer ID: {customer.id}, Email: {customer.email}")
    customer.delete

if not to_delete.exists():
    logger.info("No customers matched the deletion criteria today.")
EOF