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
