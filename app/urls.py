from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('userLogin', views.userLogin, name='userLogin'),
    path('register/', views.register, name='register'),
    path('register/userRegistration', views.userRegistration, name='userRegistration'),
    path('dashboard/',views.dashboard, name='dashboard'),
    path('dashboard/logout', views.logout, name='logout'),
    path('profile/',views.profile, name='profile'),
    path('newPatient/',views.newPatient, name='newPatient'),
    path('newPatient/submit_patient',views.submit_patient, name='submit_patient'),
    path('newPatient/record/',views.record,name = 'record'),
    path('newPatient/record/proceed/',views.proceed,name = 'proceed'),
    path('newPatient/record/proceed/save_changes',views.save_changes,name = 'save_changes'),
    path('newPatient/record/proceed/generate',views.generate,name = 'generate'),
    path('newPatient/record/record',views.record,name = 'record'),
]