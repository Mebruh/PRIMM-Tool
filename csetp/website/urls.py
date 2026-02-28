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
]