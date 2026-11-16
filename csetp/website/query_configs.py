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
            'WHERE': "You need a WHERE clause to filter the results.",
            '80000': "The salary threshold is $80,000.",
            'FROM employees': "Make sure you're selecting FROM the employees table.",
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
            'sum': "You need to use the SUM() aggregate function to calculate total salaries.",
            'salary': "Are you summing the correct column?",
            'marketing': "Check if you're filtering by the 'Marketing' department.",
            'FROM employees': "Don't forget to specify which table you are using",
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
            'LEFT JOIN': "You need a LEFT JOIN to include employees without projects. INNER JOIN will exclude them.",
            'JOIN': "This query requires a JOIN to combine the employees and projects tables.",
            'WHERE': "Don't forget the WHERE clause to filter for employees without projects.",
            'projects': "Make sure you're joining with the projects table.",
            'IS NULL': "Hint: Make sure you use `WHERE projects.employee_id IS NULL`."
        }
    }
}


# ============================================================================
# Built-in question sets that run on the shared question set page
# ============================================================================
# These use the same page and checking as custom question sets, so a new
# set only needs an entry here (plus a card on all-questions.html).

class BuiltInQuestionSet:
    """A built-in question set, with the same fields as CustomQuestionSet."""

    def __init__(self, **fields):
        self.__dict__.update(fields)

    @property
    def table_list(self):
        return self.tables.split(',')


BUILTIN_QUESTION_SETS = {
    # ========================================================================
    # CS209 Question Set 1 - Self-joins (Store database)
    # ========================================================================
    'cs209-1': BuiltInQuestionSet(
        slug='cs209-1',
        url_name='cs209-1',
        section='cs209',
        name='CS209 Question Set 1',
        intro='This question set uses the Store database and focuses on self-joins: joining a table to itself.',
        database='store',
        tables='customer',

        predict_query=(
            'SELECT c1.cID, c2.cID, c1.street\n'
            'FROM customer c1\n'
            'JOIN customer c2 ON c1.street = c2.street;'
        ),
        predict_option1='It will return only the pair of different customers who live on the same street.',
        predict_option2=(
            'It will return every customer paired with themselves, plus each pair of '
            'different customers on the same street, in both orders.'
        ),
        predict_option3='It will return every possible pair of customers.',
        predict_option4='It will return an error, because the same table cannot be used twice in one query.',
        predict_correct_answer=2,

        investigate_q1='Why are the aliases c1 and c2 needed in this query?',
        investigate_a1=(
            'The query uses the customer table twice, once for each customer in a pair. '
            'The aliases give each copy its own name, so the query can say which copy a column '
            'comes from (c1.street or c2.street). Without them, customer.street would be ambiguous.'
        ),
        investigate_q2='Why do some rows match a customer with themselves?',
        investigate_a2=(
            'The join condition only checks that the streets are equal. Every customer lives on '
            'the same street as themselves, so each row in c1 also matches the same row in c2.'
        ),
        investigate_q3='Customers 0 and 4 appear twice, once as (0, 4) and once as (4, 0). Why does this happen?',
        investigate_a3=(
            'The join compares every row of c1 with every row of c2, so the pair is found once with '
            'Noah as c1 and once with Mila as c1. Both rows satisfy the condition. To keep only one '
            'row per pair, you can require one customer ID to be smaller than the other.'
        ),

        modify_task='Add a condition to the query so that customers are not matched with themselves.',
        modify_initial_query=(
            'SELECT c1.cID, c2.cID, c1.street\n'
            'FROM customer c1\n'
            'JOIN customer c2 ON c1.street = c2.street;'
        ),
        # Either answer meets the task: <> keeps both orders of each pair,
        # < also removes the duplicate order.
        modify_correct_queries=[
            'SELECT c1.cID, c2.cID, c1.street FROM customer c1 '
            'JOIN customer c2 ON c1.street = c2.street WHERE c1.cID <> c2.cID;',
            'SELECT c1.cID, c2.cID, c1.street FROM customer c1 '
            'JOIN customer c2 ON c1.street = c2.street WHERE c1.cID < c2.cID;',
        ],

        make_task=(
            'List all pairs of customer IDs whose owners live on streets with the same name '
            'but in different cities. List each pair only once.'
        ),
        make_correct_query=(
            'SELECT c1.cID, c2.cID FROM customer c1 '
            'JOIN customer c2 ON c1.street = c2.street '
            'WHERE c1.city <> c2.city AND c1.cID < c2.cID;'
        ),
        make_hint_rules=[
            (r'customer\b[\s\S]*\bcustomer\b',
             'This needs a self-join: use the customer table twice, with a different alias each time (e.g. c1 and c2).'),
            (r'\bstreet\b',
             'Match the two customers on their street.'),
            (r'\bcity\b',
             "You also need to compare the two customers' cities."),
            (r'city\s*(<>|!=)|(<>|!=)\s*\w+\.city',
             "The cities must be different. Which operator means 'not equal to'?"),
            (r'cid\s*[<>]\s*\w+\.cid',
             'Each pair is listed twice, e.g. (0, 4) and (4, 0). Keep only one by requiring one customer ID to be smaller than the other.'),
        ],
    ),
}