import os
import sys
from datetime import datetime, timedelta
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

# Add the project root to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
sys.path.insert(0, project_root)

# Django setup
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alx_backend_graphql_crm.settings')
import django
django.setup()

def main():
    """Main function to process order reminders."""
    
    # Configuration
    GRAPHQL_ENDPOINT = "http://localhost:8000/graphql"
    LOG_FILE = "/tmp/order_reminders_log.txt"
    TIMESTAMP = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # Calculate date 7 days ago
    seven_days_ago = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
    
    try:
        # Setup GraphQL client
        transport = RequestsHTTPTransport(url=GRAPHQL_ENDPOINT)
        client = Client(transport=transport, fetch_schema_from_transport=True)
        
        # GraphQL query to get orders from the last 7 days
        query = gql("""
            query GetRecentOrders {
                orders {
                    id
                    orderDate
                    customer {
                        id
                        email
                        name
                    }
                    totalAmount
                }
            }
        """)
        
        # Execute the query
        result = client.execute(query)
        orders = result.get('orders', [])
        
        # Filter orders from the last 7 days
        recent_orders = []
        for order in orders:
            order_date = datetime.fromisoformat(order['orderDate'].replace('Z', '+00:00'))
            if order_date >= datetime.now() - timedelta(days=7):
                recent_orders.append(order)
        
        # Log the reminders
        with open(LOG_FILE, 'a') as log_file:
            log_file.write(f"\n{TIMESTAMP} - Processing order reminders:\n")
            
            if recent_orders:
                for order in recent_orders:
                    order_id = order['id']
                    customer_email = order['customer']['email']
                    customer_name = order['customer']['name']
                    order_date = order['orderDate']
                    
                    log_entry = f"{TIMESTAMP} - Order ID: {order_id}, Customer: {customer_name} ({customer_email}), Order Date: {order_date}\n"
                    log_file.write(log_entry)
                
                log_file.write(f"{TIMESTAMP} - Total reminders processed: {len(recent_orders)}\n")
            else:
                log_file.write(f"{TIMESTAMP} - No orders found in the last 7 days\n")
        
        print("Order reminders processed!")
        
    except Exception as e:
        error_msg = f"{TIMESTAMP} - Error processing order reminders: {str(e)}\n"
        with open(LOG_FILE, 'a') as log_file:
            log_file.write(error_msg)
        print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
