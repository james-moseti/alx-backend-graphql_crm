import os
from datetime import datetime
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport
from celery import shared_task
import requests

@shared_task
def generate_crm_report():
    """Generates a weekly CRM report and logs it."""
    LOG_FILE = "/tmp/crm_report_log.txt"
    TIMESTAMP = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    GRAPHQL_ENDPOINT = "http://localhost:8000/graphql"
    transport = RequestsHTTPTransport(url=GRAPHQL_ENDPOINT)
    client = Client(transport=transport, fetch_schema_from_transport=True)

    query = gql("""
        query CRMReport {
            customers {
                id
            }
            orders {
                id
                totalAmount
            }
        }
    """)

    try:
        response = client.execute(query)
        total_customers = len(response['customers'])
        total_orders = len(response['orders'])
        total_revenue = sum(order['totalAmount'] for order in response['orders'])

        with open(LOG_FILE, 'a') as log_file:
            log_file.write(f"{TIMESTAMP} - Report: {total_customers} customers, {total_orders} orders, {total_revenue} revenue\n")

        print("CRM report generated successfully!")

    except Exception as e:
        error_msg = f"{TIMESTAMP} - Error generating CRM report: {str(e)}\n"
        with open(LOG_FILE, 'a') as log_file:
            log_file.write(error_msg)
        print(f"Error: {str(e)}")
