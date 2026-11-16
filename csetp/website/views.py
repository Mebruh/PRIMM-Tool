from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import json

from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import Http404
from django.urls import reverse

from .models import (
    CustomQuestionSet, Employee, Project,
    SECTION_CHOICES, SECTION_CUSTOM, SECTION_CS209,
)
from .validators import SQLValidator, QueryComparator, QueryHintGenerator
from .executor import QueryExecutor
from .query_configs import QUERY_CONFIGS, BUILTIN_QUESTION_SETS
from .database_registry import DATABASES, DEFAULT_DATABASE, get_database, table_names


def home(request):
    return render(request, "home.html")


def primm(request):
    return render(request, "primm.html")


def all_questions(request):
    question_sets = CustomQuestionSet.objects.all()
    return render(request, "all-questions.html", {
        'cs209_sets': question_sets.filter(section=SECTION_CS209),
        'custom_sets': question_sets.filter(section=SECTION_CUSTOM),
    })


def primm1(request):
    return render(request, "primm1.html")


def primm2(request):
    return render(request, "primm2.html")


def primm3(request):
    return render(request, "primm3.html")


def cs209_set_1(request):
    question_set = BUILTIN_QUESTION_SETS['cs209-1']
    return _render_question_set_page(
        request,
        question_set,
        api_base='/api/question-set/cs209-1/',
        next_set=_next_in_section(question_set.section, reverse(question_set.url_name)),
    )


# ============================================================================
# Database Views
# ============================================================================

def databases(request):
    """Let the user choose which database to view."""
    return render(request, "databases.html", {
        'databases': DATABASES.values(),
    })


def database_view(request):
    """Show the Company database (employees and projects)."""
    employees = Employee.objects.all()
    projects = Project.objects.all()
    return render(request, "database_company.html", {
        'database': get_database('company'),
        'employees': employees,
        'projects': projects
    })


def database_store(request):
    """Show the schema and every table of the Store database."""
    database = get_database('store')
    tables = []

    with QueryExecutor.get_cursor() as cursor:
        for table in database['tables']:
            # Table names come from the registry, never from the user
            cursor.execute(f'SELECT * FROM {table["name"]}')
            columns = [col[0] for col in cursor.description]
            rows = [
                [_format_cell(value) for value in row]
                for row in cursor.fetchall()
            ]
            tables.append({
                **table,
                'columns': [
                    {'name': name, 'is_key': name in table.get('primary_key', [])}
                    for name in columns
                ],
                'rows': rows,
            })

    return render(request, "database_store.html", {
        'database': database,
        'tables': tables,
    })


def _format_cell(value):
    """Format a value for display in a database table."""
    if value is None:
        return None
    if isinstance(value, float):
        return f"{value:.2f}"
    if hasattr(value, 'isoformat'):
        # Show dates as students write them in queries, e.g. 2020-05-13
        return value.isoformat()
    return value


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


# ============================================================================
# Question Set Pages (custom and built-in)
# ============================================================================

# Shown when a student finishes the last question set in a section
SECTION_END_MESSAGES = {
    SECTION_CS209: 'Please remember to return to the survey.',
}
DEFAULT_END_MESSAGE = 'You have finished every question set in this section.'


def _section_sequence(section):
    """
    Every question set in a section, in the order shown on All Questions:
    built-in sets first, then created sets from oldest to newest.

    Returns:
        list: (url, name) pairs
    """
    sequence = [
        (reverse(question_set.url_name), question_set.name)
        for question_set in BUILTIN_QUESTION_SETS.values()
        if question_set.section == section
    ]
    sequence += [
        (reverse('custom-question-set', args=[question_set.pk]), question_set.name)
        for question_set in CustomQuestionSet.objects.filter(section=section)
    ]
    return sequence


def _next_in_section(section, current_url):
    """Return (url, name) of the set after current_url in its section, or None if it is last."""
    sequence = _section_sequence(section)
    urls = [url for url, _ in sequence]
    if current_url in urls:
        position = urls.index(current_url)
        if position + 1 < len(sequence):
            return sequence[position + 1]
    return None


def _render_question_set_page(request, question_set, api_base, subtitle=None, next_set=None):
    """
    Render the shared PRIMM page used by custom and built-in question sets.

    Args:
        question_set: CustomQuestionSet or BuiltInQuestionSet
        api_base: URL prefix for the run-predict/run-modify/run-make endpoints
        subtitle: Text under the title (defaults to the set's intro, if any)
        next_set: (url, name) of the next set in the section, or None if last
    """
    database = get_database(question_set.database)
    tables = question_set.table_list

    if len(tables) == 1:
        tables_phrase = f"the {tables[0]} table"
    elif tables:
        tables_phrase = "the " + ", ".join(tables[:-1]) + f" and {tables[-1]} tables"
    else:
        tables_phrase = "the tables"

    return render(request, "custom_question_set.html", {
        'question_set': question_set,
        'api_base': api_base,
        'subtitle': subtitle or getattr(question_set, 'intro', ''),
        'database': database,
        'database_url': reverse(database['url_name']),
        'tables_phrase': tables_phrase,
        'success_message': getattr(question_set, 'success_message', ''),
        'next_url': next_set[0] if next_set else None,
        'next_name': next_set[1] if next_set else None,
        'end_message': SECTION_END_MESSAGES.get(
            getattr(question_set, 'section', None), DEFAULT_END_MESSAGE
        ),
    })


def _get_builtin_set(slug):
    question_set = BUILTIN_QUESTION_SETS.get(slug)
    if question_set is None:
        raise Http404("Question set not found")
    return question_set


def _read_user_query(request):
    """Return (query, error_response). error_response is None if the query is usable."""
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return None, JsonResponse({"error": "❌ Invalid request format.", "correct": False}, status=400)

    user_query = data.get("query", "").strip()
    is_valid, error_message = SQLValidator(user_query).validate()
    if not is_valid:
        return None, JsonResponse({"error": error_message, "correct": False})

    return user_query, None


def _run_predict(predict_query):
    """Execute a question set's predict query and return its results."""
    success, result = QueryExecutor.execute_query(predict_query)
    if success:
        return JsonResponse({"result": result})
    return JsonResponse({"error": result}, status=500)


def _check_against_expected(request, expected_queries, include_result=True, hint_rules=None):
    """
    Run the student's query and check it against one or more expected queries.

    The answer is correct if its rows match the rows of ANY expected query.

    Args:
        expected_queries: List of correct SQL queries
        include_result: Whether to send the student's rows back for display
        hint_rules: Optional (pattern, hint) pairs used when the answer is wrong
    """
    try:
        user_query, error_response = _read_user_query(request)
        if error_response:
            return error_response

        success, user_result = QueryExecutor.execute_query(user_query)
        if not success:
            return JsonResponse({"error": user_result, "correct": False})

        is_correct = False
        for expected_query in expected_queries:
            success, expected_result = QueryExecutor.execute_query(expected_query)
            if not success:
                return JsonResponse({"error": f"❌ Expected query failed: {expected_result}", "correct": False})
            if QueryComparator.results_match(user_result, expected_result):
                is_correct = True
                break

        response = {"correct": is_correct}
        if include_result:
            response["result"] = user_result
        if not is_correct and hint_rules:
            response["hint"] = QueryHintGenerator.generate_hint_from_rules(user_query, hint_rules)

        return JsonResponse(response)

    except Exception as e:
        return JsonResponse({"error": f"❌ Query Processing Error: {str(e)}", "correct": False}, status=500)


# ============================================================================
# Built-in Question Set API Endpoints
# ============================================================================

@require_http_methods(["GET"])
def builtin_question_run_predict(request, slug):
    return _run_predict(_get_builtin_set(slug).predict_query)


@csrf_exempt
@require_http_methods(["POST"])
def builtin_question_run_modify(request, slug):
    question_set = _get_builtin_set(slug)
    return _check_against_expected(request, question_set.modify_correct_queries)


@csrf_exempt
@require_http_methods(["POST"])
def builtin_question_run_make(request, slug):
    question_set = _get_builtin_set(slug)
    return _check_against_expected(
        request,
        [question_set.make_correct_query],
        include_result=False,
        hint_rules=getattr(question_set, 'make_hint_rules', None),
    )


# ============================================================================
# Custom Question Sets
# ============================================================================

def add_question_set(request):
    """Display form to create a custom question set."""
    form_context = {
        'databases': DATABASES.values(),
        'default_database': DEFAULT_DATABASE,
        'sections': SECTION_CHOICES,
        'default_section': SECTION_CUSTOM,
    }

    if request.method == "POST":
        try:
            # Only accept known databases, and only tables from the chosen one
            database = request.POST.get('database')
            if database not in DATABASES:
                database = DEFAULT_DATABASE
            valid_tables = table_names(database)
            tables = [t for t in request.POST.getlist('tables') if t in valid_tables]

            # Only accept known sections
            section = request.POST.get('section')
            if section not in dict(SECTION_CHOICES):
                section = SECTION_CUSTOM

            # Create new question set from form data
            question_set = CustomQuestionSet(
                # Basic info
                name=request.POST.get('name'),
                created_by=request.user if request.user.is_authenticated else None,
                
                # Section, database and tables
                section=section,
                database=database,
                tables=','.join(tables),
                
                # Predict and Run
                predict_query=request.POST.get('predict_query'),
                predict_option1=request.POST.get('predict_option1'),
                predict_option2=request.POST.get('predict_option2'),
                predict_option3=request.POST.get('predict_option3'),
                predict_option4=request.POST.get('predict_option4'),
                predict_correct_answer=int(request.POST.get('predict_correct_answer')),
                
                # Investigate
                investigate_q1=request.POST.get('investigate_q1'),
                investigate_a1=request.POST.get('investigate_a1'),
                investigate_q2=request.POST.get('investigate_q2'),
                investigate_a2=request.POST.get('investigate_a2'),
                investigate_q3=request.POST.get('investigate_q3'),
                investigate_a3=request.POST.get('investigate_a3'),
                
                # Modify
                modify_task=request.POST.get('modify_task'),
                modify_initial_query=request.POST.get('modify_initial_query'),
                modify_correct_query=request.POST.get('modify_correct_query'),
                
                # Make
                make_task=request.POST.get('make_task'),
                make_correct_query=request.POST.get('make_correct_query'),
            )
            
            question_set.save()
            messages.success(request, f'Question set "{question_set.name}" created successfully!')
            return redirect('all-questions')
            
        except Exception as e:
            messages.error(request, f'Error creating question set: {str(e)}')
            return render(request, "add_question_set.html", form_context)
    
    return render(request, "add_question_set.html", form_context)


def view_custom_question_set(request, pk):
    """Display a custom question set (similar to primm1/2/3)."""
    question_set = get_object_or_404(CustomQuestionSet, pk=pk)
    return _render_question_set_page(
        request,
        question_set,
        api_base=f'/api/custom-question/{question_set.pk}/',
        subtitle=f'{question_set.get_section_display()} PRIMM question set.'
                 if question_set.section == SECTION_CS209 else 'Custom PRIMM question set.',
        next_set=_next_in_section(question_set.section, request.path),
    )


@login_required
def delete_question_set(request, pk):
    """Delete a custom question set (admin only)."""
    if not request.user.is_staff:
        messages.error(request, 'You do not have permission to delete question sets.')
        return redirect('all-questions')
    
    question_set = get_object_or_404(CustomQuestionSet, pk=pk)
    name = question_set.name
    question_set.delete()
    messages.success(request, f'Question set "{name}" deleted successfully.')
    return redirect('all-questions')


@require_http_methods(["GET"])
def custom_question_run_predict(request, pk):
    """Execute the predict query for a custom question set."""
    question_set = get_object_or_404(CustomQuestionSet, pk=pk)
    return _run_predict(question_set.predict_query)


@csrf_exempt
@require_http_methods(["POST"])
def custom_question_run_modify(request, pk):
    """Check the student's modified query against the expected query."""
    question_set = get_object_or_404(CustomQuestionSet, pk=pk)
    return _check_against_expected(request, [question_set.modify_correct_query])


@csrf_exempt
@require_http_methods(["POST"])
def custom_question_run_make(request, pk):
    """Check the student's make query against the expected query."""
    question_set = get_object_or_404(CustomQuestionSet, pk=pk)
    return _check_against_expected(request, [question_set.make_correct_query], include_result=False)