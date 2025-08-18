# ALX Backend GraphQL CRM

A simple Django GraphQL endpoint implementation.

## Setup

1. **Install dependencies**
   ```bash
   pip install django graphene-django django-filter
   ```

2. **Create project**
   ```bash
   django-admin startproject alx_backend_graphql_crm
   cd alx_backend_graphql_crm
   python manage.py startapp crm
   ```

3. **Run migrations**
   ```bash
   python manage.py migrate
   ```

4. **Start server**
   ```bash
   python manage.py runserver
   ```

## Usage

Visit `http://localhost:8000/graphql/` and run:

```graphql
{
  hello
}
```

Expected response:
```json
{
  "data": {
    "hello": "Hello, GraphQL!"
  }
}
```