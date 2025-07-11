from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport
from datetime import datetime, timedelta
import logging

logger = logging.getLogger('deletion_logger')
logger.setLevel(logging.INFO)

fh = logging.FileHandler('crm/tmp/order_reminders_log.txt')

formatter = logging.Formatter('%(asctime)s - %(message)s')
fh.setFormatter(formatter)

logger.addHandler(fh)

transport = RequestsHTTPTransport(
    url="http://localhost:8000/graphql/",
    headers={"Content-Type": "application/json"},
    verify=False,
    retries=3,
)

client = Client(
    transport=transport,
    fetch_schema_from_transport=True
)

seven_days_ago = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')

query = gql(f"""
query {{
    allOrders(status: "pending", orderDate_Gte: "{seven_days_ago}" ) {{
        edges {{
            node {{
                id
                orderDate
                totalAmount
                customer {{
                    email
                }}
            }}
        }}
    }}
}}
""")

result = client.execute(query)

for edge in result["allOrders"]["edges"]:
    order = edge["node"]
    order_id = order["id"]
    customer_email = order["customer"]["email"] if order["customer"] else "N/A"

    logger.info(f"Order ID: {order_id} - Customer Email: {customer_email}")

if not result["allOrders"]["edges"]:
    logger.info("No orders found in the last 7 days.")

logger.info("Order reminders processed!")