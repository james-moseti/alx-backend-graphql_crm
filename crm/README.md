# CRM Celery Setup

## Installation
1. Install Redis:
   ```bash
   sudo apt update
   sudo apt install redis-server
   ```
2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Setup
1. Run migrations:
   ```bash
   python manage.py migrate
   ```
2. Start Redis server:
   ```bash
   sudo service redis-server start
   ```
3. Start Celery worker:
   ```bash
   celery -A crm worker -l info
   ```
4. Start Celery Beat:
   ```bash
   celery -A crm beat -l info
   ```

## Verification
- Check the log file for the weekly report:
  ```bash
  cat /tmp/crm_report_log.txt
  ```
