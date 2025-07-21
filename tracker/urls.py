from django.urls import path
from . import views

urlpatterns = [
    path('', views.project_list, name='project_list'),
    path('projects/new/', views.create_project, name='create_project'),
    path('projects/<int:pk>/', views.project_detail, name='project_detail'),
    path('projects/<int:pk>/checklist/add/', views.add_checklist_item, name='add_checklist_item'),
    path('projects/<int:pk>/stakeholders/assign/', views.assign_stakeholder, name='assign_stakeholder'),
    path('stakeholders/new/', views.create_stakeholder, name='create_stakeholder'),
    path('projects/<int:pk>/documents/upload/', views.upload_document, name='upload_document'),
]

