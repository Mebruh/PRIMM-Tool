from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import Employee, Project
from django.db import connection
from django.db.models import Sum
from django.db.models import F




def home(request):
    return render(request, "home.html", {})

def primm(request):
    return render(request, "primm.html", {})

def database_employee(request):
    employees = Employee.objects.all()
    return render(request, "database.html", {'employees': employees})

def all_questions(request):
    return render(request, "all-questions.html", {})

def primm1(request):
    return render(request, "primm1.html", {})

def primm2(request):
    return render(request, "primm2.html", {})

def primm3(request):
    return render(request, "primm3.html", {})

def run_sql_query(request):
    query_result = list(Employee.objects.filter(job_title="Software Engineer").values("first_name", "last_name", "email", "job_title"))
    return JsonResponse({"result": query_result})

@csrf_exempt
def run_modified_query(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            user_query = data.get("query", "").strip()

            if any(word in user_query.upper() for word in ["DROP", "DELETE", "UPDATE", "INSERT"]):
                return JsonResponse({"error": "❌ Unsafe query detected. Only SELECT statements are allowed.", "correct": False})

            corrected_query = user_query.replace("employees", "website_employee")

            with connection.cursor() as cursor:
                cursor.execute(corrected_query)
                columns = [col[0] for col in cursor.description]  # Get column names
                result = [dict(zip(columns, row)) for row in cursor.fetchall()]

            expected_result = list(Employee.objects.filter(department="IT").values("first_name", "last_name", "email"))

            is_correct = result == expected_result

            return JsonResponse({"result": result, "correct": is_correct})

        except Exception as e:
            return JsonResponse({"error": f"❌ Query Error: {str(e)}", "correct": False})

    return JsonResponse({"error": "❌ Invalid request method.", "correct": False})

@csrf_exempt
def run_make_query(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            user_query = data.get("query", "").strip().lower()
            user_query = user_query.replace("employees", "website_employee")
            correct_query = 'select * from website_employee where salary < 80000;'

            with connection.cursor() as cursor:
                try:
                    cursor.execute(user_query)
                except Exception as e:
                    return JsonResponse({"error": f"❌ SQL Syntax Error: {str(e)}", "correct": False})

            is_correct = user_query.replace(" ", "").replace("\n", "") == correct_query.replace(" ", "").replace("\n", "")

            if is_correct:
                return JsonResponse({"correct": True})  # Will trigger success popup on frontend

            hint = ""
            if "salary" not in user_query:
                hint = "It looks like you're not filtering by salary."
            elif "<" not in user_query:
                hint = "Are you using the correct comparison operator?"
            elif "website_employee" not in user_query and "from employees" not in user_query:
                hint = "Check your table name. Django may prefix it with the app name."

            return JsonResponse({"correct": False, "hint": hint})

        except Exception as e:
            return JsonResponse({"error": f"❌ Query Execution Error: {str(e)}", "correct": False})

    return JsonResponse({"error": "❌ Invalid request method.", "correct": False})


@csrf_exempt
def run_sql_query_aggregate(request):
    """Executes the COUNT() SQL query and returns the result as JSON."""
    try:
        with connection.cursor() as cursor:
            cursor.execute('SELECT COUNT(email) FROM website_employee WHERE department = "Operations";')
            result = cursor.fetchone()[0]  

        return JsonResponse({"result": result})

    except Exception as e:
        return JsonResponse({"error": f"❌ Query Error: {str(e)}"})
    
@csrf_exempt
def run_modified_query_aggregate(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            user_query = data.get("query", "").strip()

            if not user_query:
                return JsonResponse({"error": "❌ Query is empty. Please enter a valid SQL query.", "correct": False})

            if any(word in user_query.upper() for word in ["DROP", "DELETE", "UPDATE", "INSERT"]):
                return JsonResponse({"error": "❌ Unsafe query detected. Only SELECT statements are allowed.", "correct": False})

            correct_query = 'SELECT COUNT(email) FROM website_employee WHERE job_title = "Data Scientist";'

            user_query = user_query.replace("employees", "website_employee")

            with connection.cursor() as cursor:
                try:
                    cursor.execute(user_query)
                    result = cursor.fetchone()[0]  # Extract count result
                except Exception as e:
                    return JsonResponse({"error": f"❌ SQL Execution Error: {str(e)}", "correct": False})

            expected_result = Employee.objects.filter(job_title="Data Scientist").count()

            is_correct = result == expected_result

            return JsonResponse({"result": result, "correct": is_correct})

        except Exception as e:
            return JsonResponse({"error": f"❌ Query Processing Error: {str(e)}", "correct": False})

    return JsonResponse({"error": "❌ Invalid request method.", "correct": False})


@csrf_exempt
def run_make_query_aggregate(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            user_query = data.get("query", "").strip()

            correct_query = 'SELECT SUM(salary) FROM website_employee WHERE department = "Marketing";'

            if any(word in user_query.upper() for word in ["DROP", "DELETE", "UPDATE", "INSERT"]):
                return JsonResponse({"error": "❌ Unsafe query detected. Only SELECT statements are allowed.", "correct": False})

            user_query = user_query.replace("employees", "website_employee")

            with connection.cursor() as cursor:
                try:
                    cursor.execute(user_query)
                    result = cursor.fetchone()[0]  # Extract the SUM result
                except Exception as e:
                    return JsonResponse({"error": f"❌ SQL Syntax Error: {str(e)}", "correct": False})

            expected_result = Employee.objects.filter(department="Marketing").aggregate(Sum("salary"))["salary__sum"]

            is_correct = result == expected_result

            hint = ""
            if "sum" not in user_query.lower():
                hint = "It looks like you're not using SUM()."
            elif "salary" not in user_query.lower():
                hint = "Are you summing the correct column?"
            elif "marketing" not in user_query.lower():
                hint = "Check if you're filtering by the 'Marketing' department."

            return JsonResponse({"correct": is_correct, "hint": hint})

        except Exception as e:
            return JsonResponse({"error": f"❌ Query Processing Error: {str(e)}", "correct": False})

    return JsonResponse({"error": "❌ Invalid request method.", "correct": False})


def database_projects(request):
    projects = Project.objects.all()
    return render(request, "database2.html", {'projects': projects})

@csrf_exempt
def run_sql_query_join(request):
    """Executes an INNER JOIN SQL query and returns the result as JSON."""
    try:
        with connection.cursor() as cursor:
            cursor.execute('''
                SELECT website_employee.first_name, website_employee.last_name, website_project.project_name
                FROM website_employee
                INNER JOIN website_project ON website_employee.id = website_project.employee_id;
            ''')
            columns = [col[0] for col in cursor.description]  # Get column names
            result = [dict(zip(columns, row)) for row in cursor.fetchall()]

        return JsonResponse({"result": result})

    except Exception as e:
        return JsonResponse({"error": f"❌ Query Error: {str(e)}"})
    


@csrf_exempt
def run_modified_query_join(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            user_query = data.get("query", "").strip()

            if not user_query:
                return JsonResponse({"error": "❌ Query is empty. Please enter a valid SQL query.", "correct": False})

            if any(word in user_query.upper() for word in ["DROP", "DELETE", "UPDATE", "INSERT"]):
                return JsonResponse({"error": "❌ Unsafe query detected. Only SELECT statements are allowed.", "correct": False})

            corrected_query = (
                user_query
                .replace("employees", "website_employee")
                .replace("projects", "website_project")
            )

            with connection.cursor() as cursor:
                try:
                    cursor.execute(corrected_query)
                    columns = [col[0] for col in cursor.description]
                    user_result = [dict(zip(columns, row)) for row in cursor.fetchall()]
                except Exception as e:
                    return JsonResponse({"error": f"❌ SQL Execution Error: {str(e)}", "correct": False})

            expected_result = list(
                Project.objects.filter(start_date__gt="2023-01-01")
                .values(
                    first_name=F("employee__first_name"), 
                    last_name=F("employee__last_name"), 
                    expected_project_name=F("project_name")  # Different alias to avoid conflicts
                )
            )

            def normalize_data(data, rename_field=False):
                normalized = []
                for d in data:
                    new_dict = {k: str(v).strip().lower() for k, v in d.items()}
                    if rename_field and "expected_project_name" in new_dict:
                        new_dict["project_name"] = new_dict.pop("expected_project_name")  # Rename back for comparison
                    normalized.append(new_dict)
                return sorted(normalized, key=lambda x: tuple(x.values()))

            user_result_normalized = normalize_data(user_result)
            expected_result_normalized = normalize_data(expected_result, rename_field=True)

            is_correct = user_result_normalized == expected_result_normalized

            return JsonResponse({"result": user_result, "correct": is_correct})

        except json.JSONDecodeError:
            return JsonResponse({"error": "❌ JSON Decode Error: Invalid request format.", "correct": False})
        except Exception as e:
            return JsonResponse({"error": f"❌ Query Processing Error: {str(e)}", "correct": False})

    return JsonResponse({"error": "❌ Invalid request method.", "correct": False})


@csrf_exempt
def run_make_query_primm3(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            user_query = data.get("query", "").strip()

            if not user_query:
                return JsonResponse({"error": "❌ Query is empty. Please enter a valid SQL query.", "correct": False})

            if any(word in user_query.upper() for word in ["DROP", "DELETE", "UPDATE", "INSERT", "ALTER"]):
                return JsonResponse({"error": "❌ Unsafe query detected. Only SELECT statements are allowed.", "correct": False})


            corrected_query = (
                user_query
                .replace("employees", "website_employee")
                .replace("projects", "website_project")
                .replace("employee_email", "employee_id")  # Fix incorrect column references
            )

            with connection.cursor() as cursor:
                try:
                    cursor.execute(corrected_query)
                    columns = [col[0] for col in cursor.description]
                    user_result = [dict(zip(columns, row)) for row in cursor.fetchall()]
                except Exception as e:
                    return JsonResponse({"error": f"❌ SQL Execution Error: {str(e)}", "correct": False})

            expected_result = list(
                Employee.objects.filter(project__isnull=True)
                .values("first_name", "last_name")
            )



            def normalize_data(data):
                return sorted(
                    [{k: str(v).strip().lower() for k, v in d.items()} for d in data],
                    key=lambda x: tuple(x.values())
                )

            user_result_normalized = normalize_data(user_result)
            expected_result_normalized = normalize_data(expected_result)


            is_correct = user_result_normalized == expected_result_normalized

            if not is_correct and "IS NULL" not in user_query.upper():
                return JsonResponse({"error": "❌ Hint: Make sure you use `WHERE projects.employee_email IS NULL`.", "correct": False})

            return JsonResponse({"result": user_result, "correct": is_correct})

        except json.JSONDecodeError:
            return JsonResponse({"error": "❌ JSON Decode Error: Invalid request format.", "correct": False})
        except Exception as e:
            return JsonResponse({"error": f"❌ Query Processing Error: {str(e)}", "correct": False})

    return JsonResponse({"error": "❌ Invalid request method.", "correct": False})