import os
from datetime import datetime
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

def log_crm_heartbeat():
    """Logs a heartbeat message to confirm CRM health."""
    LOG_FILE = "/tmp/crm_heartbeat_log.txt"
    TIMESTAMP = datetime.now().strftime('%d/%m/%Y-%H:%M:%S')

    # Log the heartbeat message
    with open(LOG_FILE, 'a') as log_file:
        log_file.write(f"{TIMESTAMP} CRM is alive\n")

    # Optionally, verify GraphQL endpoint
    GRAPHQL_ENDPOINT = "http://localhost:8000/graphql"
    transport = RequestsHTTPTransport(url=GRAPHQL_ENDPOINT)
    client = Client(transport=transport, fetch_schema_from_transport=True)

    query = gql("""
        query {
            hello
        }
    """)

    try:
        response = client.execute(query)
        print(f"GraphQL Response: {response}")
    except Exception as e:
        print(f"GraphQL Endpoint Error: {e}")

def update_low_stock():
    """Updates low-stock products and logs the changes."""
    LOG_FILE = "/tmp/low_stock_updates_log.txt"
    TIMESTAMP = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    GRAPHQL_ENDPOINT = "http://localhost:8000/graphql"
    transport = RequestsHTTPTransport(url=GRAPHQL_ENDPOINT)
    client = Client(transport=transport, fetch_schema_from_transport=True)

    mutation = gql("""
        mutation RestockLowStockProducts($increment: Int!) {
            updateLowStockProducts(increment: $increment) {
                success
                updatedProducts {
                    name
                    stock
                }
            }
        }
    """)

    try:
        response = client.execute(mutation, variable_values={"increment": 10})
        updated_products = response['updateLowStockProducts']['updatedProducts']

        with open(LOG_FILE, 'a') as log_file:
            log_file.write(f"\n{TIMESTAMP} - Updated low-stock products:\n")
            for product in updated_products:
                log_file.write(f"{product['name']} - New Stock: {product['stock']}\n")

        print("Low-stock products updated successfully!")

    except Exception as e:
        error_msg = f"{TIMESTAMP} - Error updating low-stock products: {str(e)}\n"
        with open(LOG_FILE, 'a') as log_file:
            log_file.write(error_msg)
        print(f"Error: {str(e)}")
