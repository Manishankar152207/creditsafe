from django.contrib import admin
from django.urls import path
from mainapp import views
urlpatterns = [
    path('', views.index, name="index"),
    path('fetch-company-list/', views.fetch_company_list, name="fetch-company-list"),
    path('fetch-company-list-db/', views.fetch_company_list_db, name="fetch-company-list-db"),
    path('fetch-order-list-db/', views.fetch_order_list_db, name="fetch-order-list-db"),
]
