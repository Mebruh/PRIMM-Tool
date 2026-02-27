import os
import django
from datetime import date

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "csetp.settings")
django.setup()
from website.models import Employee, Project



EMPLOYEES = [
    ("John", "Smith", "john.smith@company.com", "555-1234", "Software Engineer", "IT", 75000.00),
    ("Emma", "Johnson", "emma.johnson@company.com", "555-5678", "Data Scientist", "IT", 85000.00),
    ("Michael", "Brown", "michael.brown@company.com", "555-9876", "Project Manager", "Operations", 90000.00),
    ("Sophia", "Taylor", "sophia.taylor@company.com", "555-5432", "HR Specialist", "HR", 70000.00),
    ("David", "Anderson", "david.anderson@company.com", "555-6543", "Marketing Manager", "Marketing", 78000.00),
    ("Olivia", "Thomas", "olivia.thomas@company.com", "555-7890", "Sales Executive", "Sales", 72000.00),
    ("James", "Jackson", "james.jackson@company.com", "555-4321", "Software Engineer", "IT", 76000.00),
    ("Ava", "White", "ava.white@company.com", "555-8765", "Data Scientist", "IT", 86000.00),
    ("Daniel", "Harris", "daniel.harris@company.com", "555-3456", "Project Manager", "Operations", 92000.00),
    ("Emily", "Martin", "emily.martin@company.com", "555-9012", "HR Specialist", "HR", 71000.00),
    ("Ethan", "Clark", "ethan.clark@company.com", "555-2345", "Marketing Manager", "Marketing", 79000.00),
    ("Mia", "Lewis", "mia.lewis@company.com", "555-6789", "Sales Executive", "Sales", 73000.00),
    ("Alexander", "Walker", "alexander.walker@company.com", "555-3457", "Software Engineer", "IT", 77000.00),
    ("Isabella", "Allen", "isabella.allen@company.com", "555-8901", "Data Scientist", "IT", 87000.00),
    ("William", "Young", "william.young@company.com", "555-4567", "Project Manager", "Operations", 93000.00),
    ("Charlotte", "King", "charlotte.king@company.com", "555-6780", "HR Specialist", "HR", 72000.00),
    ("Benjamin", "Wright", "benjamin.wright@company.com", "555-1235", "Marketing Manager", "Marketing", 80000.00),
    ("Amelia", "Lopez", "amelia.lopez@company.com", "555-5679", "Sales Executive", "Sales", 74000.00),
    ("Lucas", "Hill", "lucas.hill@company.com", "555-9877", "Software Engineer", "IT", 78000.00),
    ("Harper", "Scott", "harper.scott@company.com", "555-5433", "Data Scientist", "IT", 88000.00)
]

def populate():
    for first_name, last_name, email, phone_number, job_title, department, salary in EMPLOYEES:
        if not Employee.objects.filter(email=email).exists():
            Employee.objects.create(
                first_name=first_name,
                last_name=last_name,
                email=email,
                phone_number=phone_number,
                job_title=job_title,
                department=department,
                salary=salary,
            )
    print("Successfully added employees!")


PROJECTS = [
    ("Legacy System Upgrade", "2022-03-15", "2022-12-20", "james.jackson@company.com"),
    ("Website Redesign", "2022-06-01", "2022-11-30", "ava.white@company.com"),
    ("Database Optimization", "2022-09-10", None, "daniel.harris@company.com"),
    ("AI Research", "2023-01-10", "2023-12-10", "john.smith@company.com"),
    ("Data Analytics", "2023-03-15", None, "emma.johnson@company.com"),
    ("Marketing Campaign", "2023-06-01", None, "david.anderson@company.com"),
    ("HR Recruitment", "2023-04-20", "2023-09-30", "sophia.taylor@company.com"),
    ("Product Development", "2023-05-01", None, "alexander.walker@company.com"),
    ("Cloud Migration", "2023-07-01", "2023-11-30", "lucas.hill@company.com")
]

def populate_projects():
    for project_name, start_date, end_date, employee_email in PROJECTS:
        employee = Employee.objects.filter(email=employee_email).first()
        if employee and not Project.objects.filter(project_name=project_name, employee=employee).exists():
            Project.objects.create(
                project_name=project_name,
                start_date=date.fromisoformat(start_date),
                end_date=date.fromisoformat(end_date) if end_date else None,
                employee=employee
            )
    print("Successfully added projects!")

if __name__ == "__main__":
    populate()
    populate_projects()