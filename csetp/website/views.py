from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import json

from .models import Employee, Project
from .validators import SQLValidator, QueryComparator, QueryHintGenerator
from .executor import QueryExecutor
from .query_configs import QUERY_CONFIGS


def home(request):
    """Render the home page."""
    return render(request, "home.html")


def primm(request):
    """Render the PRIMM explanation page."""
    return render(request, "primm.html")


def all_questions(request):
    """Render the all questions overview page."""
    return render(request, "all-questions.html")


def primm1(request):
    """Render PRIMM Question Set 1 (Basic SELECT queries)."""
    return render(request, "primm1.html")


def primm2(request):
    """Render PRIMM Question Set 2 (Aggregate functions)."""
    return render(request, "primm2.html")


def primm3(request):
    """Render PRIMM Question Set 3 (JOIN queries)."""
    return render(request, "primm3.html")


def database_view(request):
    """Display both employee and project database tables."""
    employees = Employee.objects.all()
    projects = Project.objects.all()
    return render(request, "database.html", {
        'employees': employees,
        'projects': projects
    })


# ============================================================================
# API Views - Query Execution
# ============================================================================

@require_http_methods(["GET"])
def run_sql_query(request):
    """
    Execute the predefined SQL query for Predict and Run section.
    Returns filtered employees (Software Engineers).
    """
    try:
        result = list(
            Employee.objects.filter(job_title="Software Engineer")
            .values("first_name", "last_name", "email", "job_title")
        )
        return JsonResponse({"result": result})
    
    except Exception as e:
        return JsonResponse({"error": f"❌ Query Error: {str(e)}"}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def run_modified_query(request):
    """
    Execute user's modified query for PRIMM1 Modify section.
    Validates and compares with expected result (IT department employees).
    """
    config = QUERY_CONFIGS['primm1_modify']
    return _execute_user_query(request, config)


@csrf_exempt
@require_http_methods(["POST"])
def run_make_query(request):
    """
    Execute user's custom query for PRIMM1 Make section.
    Checks if query matches expected solution.
    """
    config = QUERY_CONFIGS['primm1_make']
    return _execute_make_query(request, config)


@require_http_methods(["GET"])
def run_sql_query_aggregate(request):
    """
    Execute predefined aggregate query for PRIMM2 Predict and Run.
    Returns count of Operations department employees.
    """
    try:
        count = Employee.objects.filter(department="Operations").count()
        return JsonResponse({"result": count})
    
    except Exception as e:
        return JsonResponse({"error": f"❌ Query Error: {str(e)}"}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def run_modified_query_aggregate(request):
    """
    Execute user's modified aggregate query for PRIMM2 Modify section.
    Validates and compares count of Data Scientists.
    """
    config = QUERY_CONFIGS['primm2_modify']
    return _execute_user_query_aggregate(request, config)


@csrf_exempt
@require_http_methods(["POST"])
def run_make_query_aggregate(request):
    """
    Execute user's custom aggregate query for PRIMM2 Make section.
    Checks SUM of Marketing department salaries.
    """
    config = QUERY_CONFIGS['primm2_make']
    return _execute_make_query_aggregate(request, config)


@require_http_methods(["GET"])
def run_sql_query_join(request):
    """
    Execute predefined JOIN query for PRIMM3 Predict and Run.
    Returns employees with their projects.
    """
    try:
        query = '''
    SELECT employees.first_name, employees.last_name, 
           projects.project_name
    FROM employees
    INNER JOIN projects ON employees.id = projects.employee_id;
'''
        success, result = QueryExecutor.execute_query(query)
        
        if success:
            return JsonResponse({"result": result})
        else:
            return JsonResponse({"error": result}, status=500)
    
    except Exception as e:
        return JsonResponse({"error": f"❌ Query Error: {str(e)}"}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def run_modified_query_join(request):
    """
    Execute user's modified JOIN query for PRIMM3 Modify section.
    Validates JOIN with date filter.
    """
    config = QUERY_CONFIGS['primm3_modify']
    return _execute_user_query(request, config)


@csrf_exempt
@require_http_methods(["POST"])
def run_make_query_primm3(request):
    """
    Execute user's custom JOIN query for PRIMM3 Make section.
    Checks LEFT JOIN for employees without projects.
    """
    config = QUERY_CONFIGS['primm3_make']
    return _execute_user_query(request, config)


# ============================================================================
# Helper Functions
# ============================================================================

def _execute_user_query(request, config):
    """
    Generic function to execute user queries that return multiple rows.
    
    Args:
        request: Django request object
        config: Dictionary with validation and comparison configuration
    
    Returns:
        JsonResponse with results or error
    """
    try:
        data = json.loads(request.body)
        user_query = data.get("query", "").strip()
        
        # Validate query
        validator = SQLValidator(user_query)
        is_valid, error_message = validator.validate()
        
        if not is_valid:
            return JsonResponse({"error": error_message, "correct": False})
        
        # Normalize table names
        normalized_query = validator.normalize_table_names(config['table_mapping'])
        
        # Execute query
        success, result = QueryExecutor.execute_query(normalized_query)
        
        if not success:
            return JsonResponse({"error": result, "correct": False})
        
        # Get expected result
        expected_result = config['get_expected_result']()
        
        # Compare results
        is_correct = QueryComparator.compare_results(
            result, 
            expected_result,
            config.get('rename_fields')
        )
        
        return JsonResponse({"result": result, "correct": is_correct})
    
    except json.JSONDecodeError:
        return JsonResponse({
            "error": "❌ Invalid request format.",
            "correct": False
        }, status=400)
    
    except Exception as e:
        return JsonResponse({
            "error": f"❌ Query Processing Error: {str(e)}",
            "correct": False
        }, status=500)


def _execute_make_query(request, config):
    """
    Generic function for "Make" section queries with hint generation.
    
    Args:
        request: Django request object
        config: Dictionary with validation and hint configuration
    
    Returns:
        JsonResponse with correctness and hints
    """
    try:
        data = json.loads(request.body)
        user_query = data.get("query", "").strip()
        
        # Validate query
        validator = SQLValidator(user_query)
        is_valid, error_message = validator.validate()
        
        if not is_valid:
            return JsonResponse({"error": error_message, "correct": False})
        
        # Normalize table names
        normalized_query = validator.normalize_table_names(config['table_mapping'])
        
        # Test query syntax
        success, error = QueryExecutor.test_query_syntax(normalized_query)
        
        if not success:
            return JsonResponse({
                "error": f"❌ SQL Syntax Error: {error}",
                "correct": False
            })
        
        # Compare with expected query
        is_correct = QueryComparator.compare_queries(
            normalized_query,
            config['expected_query']
        )
        
        if is_correct:
            return JsonResponse({"correct": True})
        
        # Generate hint
        hint = QueryHintGenerator.generate_hint(
            user_query,
            config['hint_keywords']
        )
        
        return JsonResponse({"correct": False, "hint": hint})
    
    except json.JSONDecodeError:
        return JsonResponse({
            "error": "❌ Invalid request format.",
            "correct": False
        }, status=400)
    
    except Exception as e:
        return JsonResponse({
            "error": f"❌ Query Processing Error: {str(e)}",
            "correct": False
        }, status=500)


def _execute_user_query_aggregate(request, config):
    """
    Execute user queries that return aggregate values (COUNT, SUM, etc.).
    
    Args:
        request: Django request object
        config: Dictionary with validation and comparison configuration
    
    Returns:
        JsonResponse with result and correctness
    """
    try:
        data = json.loads(request.body)
        user_query = data.get("query", "").strip()
        
        # Validate query
        validator = SQLValidator(user_query)
        is_valid, error_message = validator.validate()
        
        if not is_valid:
            return JsonResponse({"error": error_message, "correct": False})
        
        # Normalize table names
        normalized_query = validator.normalize_table_names(config['table_mapping'])
        
        # Execute query
        success, result = QueryExecutor.execute_query_single_value(normalized_query)
        
        if not success:
            return JsonResponse({"error": result, "correct": False})
        
        # Get expected result
        expected_result = config['get_expected_result']()
        
        # Compare results
        is_correct = (result == expected_result)
        
        return JsonResponse({"result": result, "correct": is_correct})
    
    except json.JSONDecodeError:
        return JsonResponse({
            "error": "❌ Invalid request format.",
            "correct": False
        }, status=400)
    
    except Exception as e:
        return JsonResponse({
            "error": f"❌ Query Processing Error: {str(e)}",
            "correct": False
        }, status=500)


def _execute_make_query_aggregate(request, config):
    """
    Execute "Make" queries with aggregate functions and hints.
    
    Args:
        request: Django request object
        config: Dictionary with configuration
    
    Returns:
        JsonResponse with correctness and hints
    """
    try:
        data = json.loads(request.body)
        user_query = data.get("query", "").strip()
        
        # Validate query
        validator = SQLValidator(user_query)
        is_valid, error_message = validator.validate()
        
        if not is_valid:
            return JsonResponse({"error": error_message, "correct": False})
        
        # Normalize table names
        normalized_query = validator.normalize_table_names(config['table_mapping'])
        
        # Execute query
        success, result = QueryExecutor.execute_query_single_value(normalized_query)
        
        if not success:
            return JsonResponse({"error": result, "correct": False})
        
        # Get expected result
        expected_result = config['get_expected_result']()
        
        # Compare results
        is_correct = (result == expected_result)
        
        if is_correct:
            return JsonResponse({"correct": True})
        
        # Generate hint
        hint = QueryHintGenerator.generate_hint(
            user_query,
            config['hint_keywords']
        )
        
        return JsonResponse({"correct": is_correct, "hint": hint})
    
    except json.JSONDecodeError:
        return JsonResponse({
            "error": "❌ Invalid request format.",
            "correct": False
        }, status=400)
    
    except Exception as e:
        return JsonResponse({
            "error": f"❌ Query Processing Error: {str(e)}",
            "correct": False
        }, status=500)
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