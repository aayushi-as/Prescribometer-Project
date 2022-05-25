from tkinter import CASCADE
from django.db import models
from pymysql import NULL

# Create your models here.
class Doctor(models.Model):
    doctor_id = models.AutoField(primary_key=True)
    d_email = models.EmailField(max_length=50, unique=True)
    d_name = models.TextField(max_length=25)
    d_contactNo = models.CharField(max_length=12)
    state = models.TextField(max_length=25)
    city = models.TextField(max_length=25)
    hospital_name = models.TextField(max_length=50)
    specialization = models.TextField(max_length=25, default=NULL)

    def __str__(self):
        return self.doctor_id

class Patients(models.Model):
    patient_id = models.AutoField(primary_key=True)
    doctor_id = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    name = models.TextField(max_length=25)
    email = models.EmailField(max_length=50, unique=True)
    contactNo = models.IntegerField(unique= True)
    dob = models.DateField()

    def __str__(self):
        return self.patient_id

# class Specialization(models.Model):
#     s_id = models.AutoField(primary_key=True)
#     doctor_id = models.ForeignKey(Doctor, on_delete=models.CASCADE)
#     description = models.TextField(max_length=25)

#     def __str__(self):
#         return self.s_id
