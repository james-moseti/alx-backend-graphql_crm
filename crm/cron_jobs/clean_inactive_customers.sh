#!/bin/bash
# Script to delete inactive customers (no orders in the past year) and log the result

LOG_FILE="/tmp/customer_cleanup_log.txt"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

cd "$(dirname "$0")/../../.."

DELETED_COUNT=$(python3 manage.py shell -c "from crm.models import Customer, Order; from django.utils import timezone; from datetime import timedelta; one_year_ago = timezone.now() - timedelta(days=365); customers = Customer.objects.exclude(order__date__gte=one_year_ago).distinct(); count = customers.count(); customers.delete(); print(count)")

if [ "$DELETED_COUNT" -gt 0 ]; then
    echo "$TIMESTAMP - Deleted $DELETED_COUNT inactive customers" >> "$LOG_FILE"
else
    echo "$TIMESTAMP - No inactive customers deleted" >> "$LOG_FILE"
fi
