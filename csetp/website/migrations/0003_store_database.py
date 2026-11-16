"""
Create and populate the Store database tables.

The tables are created with plain SQL rather than Django models so that they
match the schema students are taught exactly: no extra Django `id` columns,
and composite primary keys on shoppinglist and inventory.

Note: the purchases table is called `purchase`, not `transaction`.
TRANSACTION is a reserved word in SQLite, so a table with that name would have
to be written in double quotes in every student query.
"""

from django.db import migrations


CREATE_TABLES = [
    """
    CREATE TABLE customer (
        cID DECIMAL(5,0) PRIMARY KEY,
        cName VARCHAR(255) NOT NULL,
        street VARCHAR(255) NOT NULL,
        city VARCHAR(255) NOT NULL
    )
    """,
    """
    CREATE TABLE store (
        sID DECIMAL(5,0) PRIMARY KEY,
        sName VARCHAR(255) NOT NULL,
        street VARCHAR(255) NOT NULL,
        city VARCHAR(255) NOT NULL
    )
    """,
    """
    CREATE TABLE product (
        pID DECIMAL(5,0) PRIMARY KEY,
        pName VARCHAR(255) NOT NULL,
        suffix VARCHAR(255)
    )
    """,
    """
    CREATE TABLE shoppinglist (
        cID DECIMAL(5,0) REFERENCES customer(cID),
        pID DECIMAL(5,0) REFERENCES product(pID),
        quantity DECIMAL(10,0) NOT NULL,
        date DATE NOT NULL,
        PRIMARY KEY (cID, pID)
    )
    """,
    """
    CREATE TABLE purchase (
        tID DECIMAL(5,0) PRIMARY KEY,
        cID DECIMAL(5,0) NOT NULL REFERENCES customer(cID),
        sID DECIMAL(5,0) NOT NULL REFERENCES store(sID),
        pID DECIMAL(5,0) NOT NULL REFERENCES product(pID),
        date DATE NOT NULL,
        quantity DECIMAL(10,0) NOT NULL,
        price DECIMAL(10,2) NOT NULL
    )
    """,
    """
    CREATE TABLE inventory (
        sID DECIMAL(5,0) REFERENCES store(sID),
        pID DECIMAL(5,0) REFERENCES product(pID),
        date DATE NOT NULL,
        quantity DECIMAL(10,0) NOT NULL,
        unit_price DECIMAL(10,2) NOT NULL,
        PRIMARY KEY (sID, pID, date)
    )
    """,
]

INSERT_DATA = [
    """
    INSERT INTO customer VALUES
        (0, 'Noah', 'Koestraat', 'Utrecht'),
        (1, 'Sem', 'Rozemarijnstraat', 'Breda'),
        (2, 'Lucas', 'Oude Leliestraat', 'Amsterdam'),
        (3, 'Daan', 'Kalverstraat', 'Amsterdam'),
        (4, 'Mila', 'Koestraat', 'Breda')
    """,
    """
    INSERT INTO store VALUES
        (0, 'Coop', 'Kalverstraat', 'Amsterdam'),
        (1, 'Lidl', 'Hoogstraat', 'Utrecht'),
        (2, 'Lidl', 'Molenstraat', 'Eindhoven'),
        (3, 'Hoogvliet', 'Rozemarijnstraat', 'Breda'),
        (4, 'Sligro', 'Stationsplein', 'Breda')
    """,
    """
    INSERT INTO product VALUES
        (1, 'Milk', NULL),
        (2, 'Mushrooms', NULL),
        (3, 'Apples', NULL),
        (4, 'Tea', NULL),
        (5, 'Banana', NULL)
    """,
    """
    INSERT INTO shoppinglist VALUES
        (1, 2, 1, '2020-05-13'),
        (1, 3, 6, '2020-05-13'),
        (3, 1, 2, '2020-05-15')
    """,
    """
    INSERT INTO purchase VALUES
        (0, 0, 4, 3, '2020-05-12', 5, 0.40),
        (1, 0, 0, 1, '2020-05-13', 2, 0.65),
        (2, 2, 4, 4, '2020-05-15', 2, 1.30),
        (3, 3, 0, 1, '2020-05-15', 1, 0.67)
    """,
    """
    INSERT INTO inventory VALUES
        (0, 1, '2020-05-15', 55, 0.55),
        (0, 2, '2020-05-15', 32, 2.30),
        (0, 4, '2020-05-15', 12, 1.80),
        (1, 1, '2020-05-15', 45, 0.60)
    """,
]

# Dropped in reverse order so foreign keys are never left dangling.
DROP_TABLES = [
    f"DROP TABLE IF EXISTS {table}"
    for table in ['inventory', 'purchase', 'shoppinglist', 'product', 'store', 'customer']
]


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0002_customquestionset'),
    ]

    operations = [
        migrations.RunSQL(
            sql=CREATE_TABLES + INSERT_DATA,
            reverse_sql=DROP_TABLES,
        ),
    ]