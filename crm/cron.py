import logging
import os
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

os.makedirs('crm/tmp', exist_ok=True)

#Heartbeat Logger
heartbeat_logger = logging.getLogger('heartbeat')
heartbeat_logger.setLevel(logging.INFO)

heartbeat_log_path = 'crm/tmp/crm_heartbeat_log.txt'
heartbeat_fh = logging.FileHandler(heartbeat_log_path)
heartbeat_formatter = logging.Formatter('%(asctime)s - %(message)s')
heartbeat_fh.setFormatter(heartbeat_formatter)

if not heartbeat_logger.hasHandlers():
    heartbeat_logger.addHandler(heartbeat_fh)

#Stock Update Logger
stock_logger = logging.getLogger('stock_update')
stock_logger.setLevel(logging.INFO)

stock_log_path = 'crm/tmp/low_stock_updates_log.txt'
stock_fh = logging.FileHandler(stock_log_path)
stock_formatter = logging.Formatter('%(asctime)s - %(message)s')
stock_fh.setFormatter(stock_formatter)

if not stock_logger.hasHandlers():
    stock_logger.addHandler(stock_fh)


transport = RequestsHTTPTransport(
    url='http://localhost:8000/graphql/',
    headers={"Content-Type": "application/json"},
    use_json=True,
    )
client = Client(transport=transport, fetch_schema_from_transport=True)


def log_crm_heartbeat():
    query = gql("""
    query {
        hello
    }
    """)
    try:
        result = client.execute(query)
        heartbeat_logger.info("CRM is alive")
    except Exception as e:
        heartbeat_logger.error(f"Heartbeat check failed: {e}")

def update_low_stock():
    query = gql("""
    mutation {
        updateLowStockProducts(restockAmount: 10) {
            updatedProducts {
                id
                name
                stock
            }
            message
        }
    }
    """)

    try:
        result = client.execute(query)
        data = result["updateLowStockProducts"]
        stock_logger.info(f"Stock Update: {data['message']}")
        for product in data["updatedProducts"]:
            stock_logger.info(f"Restocked Product - ID: {product['id']}, Name: {product['name']}, New Stock: {product['stock']}")
    except Exception as e:
        stock_logger.error(f"Low stock update failed: {e}")

if __name__ == "__main__":
    log_crm_heartbeat()
    update_low_stock()