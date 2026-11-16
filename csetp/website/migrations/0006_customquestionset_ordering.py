"""
Show created question sets oldest first.

This only changes Django's default ordering; the database is not altered.
"""

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0005_customquestionset_section'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='customquestionset',
            options={'ordering': ['created_at', 'pk']},
        ),
    ]