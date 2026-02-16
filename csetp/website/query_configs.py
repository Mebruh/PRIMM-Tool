"""
Query Configurations
Centralizes expected results, table mappings, and hint keywords for all exercises.
"""

from django.db.models import Sum, F
from .models import Employee, Project


# Table name mappings (This was an old issue with the codebase where the names the users gave the names of the actual databes in the code were dofferent. Fixed now.)
EMPLOYEE_TABLE_MAPPING = {'employees': 'employees'}

PROJECT_TABLE_MAPPING = {
    'employees': 'employees',
    'projects': 'projects'
}


# Configuration for each exercise
QUERY_CONFIGS = {
    # ========================================================================
    # PRIMM 1 - Basic SELECT Queries
    # ========================================================================
    'primm1_modify': {
        'table_mapping': EMPLOYEE_TABLE_MAPPING,
        'get_expected_result': lambda: list(
            Employee.objects.filter(department="IT")
            .values("first_name", "last_name", "email")
        ),
        'rename_fields': None
    },
    
    'primm1_make': {
        'table_mapping': EMPLOYEE_TABLE_MAPPING,
        'expected_query': 'select * from employees where salary < 80000;',
        'hint_keywords': {  
            'salary': "It looks like you're not filtering by salary.",
            '<': "Are you using the correct comparison operator?",
        }   
    },
    
    # ========================================================================
    # PRIMM 2 - Aggregate Functions
    # ========================================================================
    'primm2_modify': {
        'table_mapping': EMPLOYEE_TABLE_MAPPING,
        'get_expected_result': lambda: Employee.objects.filter(
            job_title="Data Scientist"
        ).count()
    },
    
    'primm2_make': {
        'table_mapping': EMPLOYEE_TABLE_MAPPING,
        'get_expected_result': lambda: Employee.objects.filter(
            department="Marketing"
        ).aggregate(Sum("salary"))["salary__sum"],
        'hint_keywords': {
            'sum': "It looks like you're not using SUM().",
            'salary': "Are you summing the correct column?",
            'marketing': "Check if you're filtering by the 'Marketing' department."
        }
    },
    
    # ========================================================================
    # PRIMM 3 - JOIN Queries
    # ========================================================================
    'primm3_modify': {
        'table_mapping': PROJECT_TABLE_MAPPING,
        'get_expected_result': lambda: list(
            Project.objects.filter(start_date__gt="2023-01-01")
            .values(
                first_name=F("employee__first_name"),
                last_name=F("employee__last_name"),
                expected_project_name=F("project_name")
            )
        ),
        'rename_fields': {'expected_project_name': 'project_name'}
    },
    
    'primm3_make': {
        'table_mapping': PROJECT_TABLE_MAPPING,
        'get_expected_result': lambda: list(
            Employee.objects.filter(project__isnull=True)
            .values("first_name", "last_name")
        ),
        'rename_fields': None,
        'hint_keywords': {
            'IS NULL': "Hint: Make sure you use `WHERE projects.employee_id IS NULL`."
        }
    }
}
