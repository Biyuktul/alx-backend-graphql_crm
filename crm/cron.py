import logging
import os
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

os.makedirs('crm/tmp', exist_ok=True)

logger = logging.getLogger(__name__)

logger.setLevel(logging.INFO)

fh = logging.FileHandler('crm/tmp/crm_heartbeat_log.txt')

formatter = logging.Formatter('%(asctime)s - %(message)s')
fh.setFormatter(formatter)

if not logger.handlers:
    logger.addHandler(fh)

transport = RequestsHTTPTransport(url='http://localhost:8000/graphql/')
client = Client(transport=transport, fetch_schema_from_transport=True)

query = gql("""
query {
  hello
}
""")

result = client.execute(query)
print(result)

def log_crm_heartbeat():
    logger.info("CRM is alive")

if __name__ == "__main__":
    log_crm_heartbeat()