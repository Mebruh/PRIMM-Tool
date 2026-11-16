"""
Let a custom question set choose its section of the All Questions page.

Existing question sets stay in the Custom section.
"""

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0004_customquestionset_database'),
    ]

    operations = [
        migrations.AddField(
            model_name='customquestionset',
            name='section',
            field=models.CharField(
                choices=[('custom', 'Custom set'), ('cs209', 'CS209')],
                default='custom',
                help_text='Section of the All Questions page this set appears in',
                max_length=20,
            ),
        ),
    ]