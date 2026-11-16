from django.db import models

from .database_registry import DATABASE_CHOICES, DEFAULT_DATABASE, get_database


# Sections of the All Questions page that a created question set can go in
SECTION_CUSTOM = 'custom'
SECTION_CS209 = 'cs209'
SECTION_CHOICES = [
    (SECTION_CUSTOM, 'Custom set'),
    (SECTION_CS209, 'CS209'),
]


class Employee(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    job_title = models.CharField(max_length=100)
    department = models.CharField(max_length=100)
    salary = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        db_table = 'employees'

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.job_title}"

class Project(models.Model):
    project_name = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE) 


    class Meta:
        db_table = 'projects'

    def __str__(self):
        return f"{self.project_name} - {self.employee.first_name} {self.employee.last_name}"
    


class CustomQuestionSet(models.Model):
    
    name = models.CharField(max_length=200, help_text="Question set name")
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey('auth.User', on_delete=models.CASCADE, null=True, blank=True)
    
    # Which section of the All Questions page the set appears in
    section = models.CharField(
        max_length=20,
        choices=SECTION_CHOICES,
        default=SECTION_CUSTOM,
        help_text="Section of the All Questions page this set appears in",
    )

    # Database and Table Selection
    database = models.CharField(
        max_length=20,
        choices=DATABASE_CHOICES,
        default=DEFAULT_DATABASE,
        help_text="Which sample database the questions use",
    )
    tables = models.CharField(
        max_length=255,
        blank=True,
        default='',
        help_text="Comma-separated names of the tables the questions use",
    )

    # Predict and Run Section
    predict_query = models.TextField(help_text="SQL query for predict section")
    predict_option1 = models.CharField(max_length=500)
    predict_option2 = models.CharField(max_length=500)
    predict_option3 = models.CharField(max_length=500)
    predict_option4 = models.CharField(max_length=500)
    predict_correct_answer = models.IntegerField(choices=[(1,'1'),(2,'2'),(3,'3'),(4,'4')])
    
    # Investigate Section
    investigate_q1 = models.TextField(help_text="Investigation question 1")
    investigate_a1 = models.TextField(help_text="Correct answer 1")
    investigate_q2 = models.TextField(help_text="Investigation question 2")
    investigate_a2 = models.TextField(help_text="Correct answer 2")
    investigate_q3 = models.TextField(help_text="Investigation question 3")
    investigate_a3 = models.TextField(help_text="Correct answer 3")
    
    # Modify Section
    modify_task = models.TextField(help_text="What should students modify?")
    modify_initial_query = models.TextField(help_text="Semi-correct query to modify")
    modify_correct_query = models.TextField(help_text="Correct query after modification")
    
    # Make Section
    make_task = models.TextField(help_text="Task for make section")
    make_correct_query = models.TextField(help_text="Correct SQL query for make section")
    
    class Meta:
        db_table = 'custom_question_sets'
        # Oldest first, so the newest set appears last in its section
        ordering = ['created_at', 'pk']
    
    def __str__(self):
        return self.name

    @property
    def table_list(self):
        """The tables used, as a list of names."""
        return [name for name in self.tables.split(',') if name]

    @property
    def database_info(self):
        """The registry entry for this question set's database."""
        return get_database(self.database)