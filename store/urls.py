from django.urls import path
from . import views


urlpatterns = [
    path('', views.dashboard, name='dashboard'),

    path('dashboard/', views.dashboard, name='dashboard'),

    path('', views.product_list, name='product_list'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('add-product/', views.add_product, name='add_product'),
    path('billing/', views.billing, name='billing'),
    path('reports/', views.sales_report, name='sales_report'),
path('reports/pdf/', views.export_sales_pdf, name='export_sales_pdf'),

]

