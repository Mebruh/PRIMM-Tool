"""
Let custom question sets choose a database.

Adds `database` and `tables` to CustomQuestionSet, copies the old
uses_employees / uses_projects checkboxes into `tables` so existing question
sets keep their table list, then removes the old checkbox fields.
"""

from django.db import migrations, models


def copy_table_flags(apps, schema_editor):
    CustomQuestionSet = apps.get_model('website', 'CustomQuestionSet')
    for question_set in CustomQuestionSet.objects.all():
        tables = []
        if question_set.uses_employees:
            tables.append('employees')
        if question_set.uses_projects:
            tables.append('projects')
        question_set.database = 'company'
        question_set.tables = ','.join(tables)
        question_set.save(update_fields=['database', 'tables'])


def restore_table_flags(apps, schema_editor):
    CustomQuestionSet = apps.get_model('website', 'CustomQuestionSet')
    for question_set in CustomQuestionSet.objects.all():
        tables = question_set.tables.split(',')
        question_set.uses_employees = 'employees' in tables
        question_set.uses_projects = 'projects' in tables
        question_set.save(update_fields=['uses_employees', 'uses_projects'])


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0003_store_database'),
    ]

    operations = [
        migrations.AddField(
            model_name='customquestionset',
            name='database',
            field=models.CharField(
                choices=[('company', 'Company Database'), ('store', 'Store Database')],
                default='company',
                help_text='Which sample database the questions use',
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name='customquestionset',
            name='tables',
            field=models.CharField(
                blank=True,
                default='',
                help_text='Comma-separated names of the tables the questions use',
                max_length=255,
            ),
        ),
        migrations.RunPython(copy_table_flags, restore_table_flags),
        migrations.RemoveField(
            model_name='customquestionset',
            name='uses_employees',
        ),
        migrations.RemoveField(
            model_name='customquestionset',
            name='uses_projects',
        ),
    ]