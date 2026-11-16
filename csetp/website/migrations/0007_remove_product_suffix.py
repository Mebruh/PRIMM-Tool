"""
Remove the suffix column from the Store database's product table.

The table is rebuilt (create new table, copy rows, drop old, rename) instead of
using ALTER TABLE ... DROP COLUMN, which only exists in SQLite 3.35 and later.
Django switches off foreign key checks while migrations run on SQLite, so the
shoppinglist, purchase and inventory tables keep pointing at product(pID).
"""

from django.db import migrations


REMOVE_SUFFIX = [
    """
    CREATE TABLE product_new (
        pID DECIMAL(5,0) PRIMARY KEY,
        pName VARCHAR(255) NOT NULL
    )
    """,
    "INSERT INTO product_new (pID, pName) SELECT pID, pName FROM product",
    "DROP TABLE product",
    "ALTER TABLE product_new RENAME TO product",
]

RESTORE_SUFFIX = [
    """
    CREATE TABLE product_new (
        pID DECIMAL(5,0) PRIMARY KEY,
        pName VARCHAR(255) NOT NULL,
        suffix VARCHAR(255)
    )
    """,
    "INSERT INTO product_new (pID, pName, suffix) SELECT pID, pName, NULL FROM product",
    "DROP TABLE product",
    "ALTER TABLE product_new RENAME TO product",
]


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0006_customquestionset_ordering'),
    ]

    operations = [
        migrations.RunSQL(sql=REMOVE_SUFFIX, reverse_sql=RESTORE_SUFFIX),
    ]