from celery import Celery
from django.conf import settings
import logging
from .celery import app
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport
import os

os.makedirs('crm/tmp', exist_ok=True)

reports_logger = logging.getLogger('crm_reports')
reports_logger.setLevel(logging.INFO)

reports_log_path = 'crm/tmp/crm_report_log.txt'
reports_fh = logging.FileHandler(reports_log_path)
reports_formatter = logging.Formatter('%(asctime)s - %(message)s')
reports_fh.setFormatter(reports_formatter)

if not reports_logger.hasHandlers():
    reports_logger.addHandler(reports_fh)


transport = RequestsHTTPTransport(
    url='http://localhost:8000/graphql/',
    headers={"Content-Type": "application/json"},
    use_json=True,
    )
client = Client(transport=transport, fetch_schema_from_transport=True)

@app.task(bind=True, max_retries=3)
def generate_crm_report(self):
    query = gql("""
    query {
        totalCustomers
        totalOrders
        totalRevenue
    }
    """)

    try:
        result = client.execute(query)
        total_customers = result["totalCustomers"]
        total_orders = result["totalOrders"]
        total_revenue = result["totalRevenue"]

        reports_logger.info(f"Report: {total_customers} customers, {total_orders} orders, {total_revenue:,.2f} revenue")
    except Exception as exc:
        reports_logger.error(f"reports logging failed: {exc}")
        self.retry(countdown=60, exc=exc)
