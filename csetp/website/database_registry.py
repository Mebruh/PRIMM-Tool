"""
Database Registry
Describes the sample databases students can query.

Both databases live in the same SQLite file. This registry only groups the
tables into named databases so the site can show them separately and so
question sets can say which database they use.
"""

DATABASES = {
    'company': {
        'key': 'company',
        'name': 'Company Database',
        'short_name': 'Company',
        'icon': 'bi-building',
        'url_name': 'database-view',
        'description': 'Employees of a company and the projects they are assigned to.',
        'tables': [
            {
                'name': 'employees',
                'description': 'Each employee with their contact details, job title, department and salary.',
            },
            {
                'name': 'projects',
                'description': 'Projects with start and end dates. employee_id links each project to an employee.',
            },
        ],
    },
    'store': {
        'key': 'store',
        'name': 'Store Database',
        'short_name': 'Store',
        'icon': 'bi-shop',
        'url_name': 'database-store',
        'description': 'Customers, supermarkets, products, shopping lists, purchases and store inventory.',
        'tables': [
            {
                'name': 'customer',
                'description': 'Customers and the street and city they live on.',
                'primary_key': ['cID'],
            },
            {
                'name': 'store',
                'description': 'Supermarket branches and the street and city they are on.',
                'primary_key': ['sID'],
            },
            {
                'name': 'product',
                'description': 'Products that can be bought.',
                'primary_key': ['pID'],
            },
            {
                'name': 'shoppinglist',
                'description': 'Products customers plan to buy. cID links to customer, pID links to product.',
                'primary_key': ['cID', 'pID'],
            },
            {
                'name': 'purchase',
                'description': 'Products customers have bought, in which store, on which date and at what price.',
                'primary_key': ['tID'],
            },
            {
                'name': 'inventory',
                'description': 'How many of each product a store had in stock on a given date, and the unit price.',
                'primary_key': ['sID', 'pID', 'date'],
            },
        ],
    },
}

DEFAULT_DATABASE = 'company'

DATABASE_CHOICES = [(key, info['name']) for key, info in DATABASES.items()]


def get_database(key):
    """Return the registry entry for a database key, falling back to the default."""
    return DATABASES.get(key, DATABASES[DEFAULT_DATABASE])


def table_names(key):
    """Return the table names that belong to a database."""
    return [table['name'] for table in get_database(key)['tables']]