from django.urls import path

from eve.cost_calculation import views

app_name = 'cost_calculation'
urlpatterns = [
    path('<int:pk>/', views.CostCalculation.as_view(), name='test'),
]