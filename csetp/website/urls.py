from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name="home"),
    path('primm/', views.primm, name="primm"),
    path('database/', views.database_view, name="database-view"),
    path('all-questions/', views.all_questions, name="all-questions"), 
    path('primm1/', views.primm1, name="primm1"),
    path('primm2/', views.primm2, name="primm2"),
    path('primm3/', views.primm3, name="primm3"),
    path('run-sql-query/', views.run_sql_query, name="run_sql_query"),
    path('run-modified-query/', views.run_modified_query, name="run_modified_query"),
    path('run-make-query/', views.run_make_query, name="run_make_query"),
    path('run-sql-query-aggregate/', views.run_sql_query_aggregate, name="run_sql_query_aggregate"),
    path('run-modified-query-aggregate/', views.run_modified_query_aggregate, name="run_modified_query_aggregate"),
    path('run-make-query-aggregate/', views.run_make_query_aggregate, name="run_make_query_aggregate"),
    path('run-sql-query-join/', views.run_sql_query_join, name="run_sql_query_join"),
    path('run-modified-query-join/', views.run_modified_query_join, name="run_modified_query_join"),
    path('run_make_query_primm3/', views.run_make_query_primm3, name="run_make_query_primm3"),
    path('add-question-set/', views.add_question_set, name='add-question-set'),
    path('custom-question/<int:pk>/', views.view_custom_question_set, name='custom-question-set'),
    path('delete-question-set/<int:pk>/', views.delete_question_set, name='delete-question-set'),
    path('api/custom-question/<int:pk>/run-predict/', views.custom_question_run_predict, name='custom-question-run-predict'),
    path('api/custom-question/<int:pk>/run-modify/', views.custom_question_run_modify, name='custom-question-run-modify'),
    path('api/custom-question/<int:pk>/run-make/', views.custom_question_run_make, name='custom-question-run-make'),
]