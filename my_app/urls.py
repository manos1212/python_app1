from . import views
from django.urls import path

urlpatterns = [
    path("createappoint/<int:p_id>",views.create_appoint,name="create_appointment"),#/<str:appoint_date>
    path('', views.home, name='home'),
    path('viewappoints/',views.view_all_appoints,name='viewappoints'),
    path('view/', views.view_all, name='view'),
    path('view/delete/<int:p_id>/', views.delete),
    path('add/', views.add_patient, name="add"),
    path('update/<int:p_id>/', views.update_patient, name="update"),
    path("add-pat/", views.get_id, name="test"),
    path('viewappoints/delete/<int:appoint_id>/', views.delete_appoint),
    path('plots/', views.plots, name="plots"),
    path('tomorrows_dose_csv/', views.tomorrows_dose, name="tomorrows_dose"),
    path('tomorrows_dose_pdf/', views.tomorrows_dose_pdf, name="tomorrows_dose_pdf"),

    # path("test1/", views.get_id_field, name="test1")
    # path('test/<int:p_id>/', views.update_patient, name="test")


    # path('update/', views.update_patients, name="update")
    # path('update/', views.view_all, name="update")
    ]