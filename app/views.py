from email import message
from django.shortcuts import render, redirect
from django.contrib.auth.models import User, auth
from django.contrib import messages
from django.conf import settings
# from django.core.mail import send_mail
from django.core.mail import EmailMessage
from datetime import date
import speech_recognition as sr
import pyaudio
import re
import string
import joblib
import numpy as np
import tensorflow as tf
from tensorflow import keras
from keras.models import load_model
from fpdf import FPDF
import os, sys
import subprocess
from datetime import date
from app.models import Doctor
import re



#joblib imports
word2idx = joblib.load('./model/word2idx.sav')
words = joblib.load('./model/words.sav')
tags = joblib.load('./model/tags.sav')
#model = joblib.load('./model/model.sav')
model = keras.models.load_model('model_weights.h5')




# Create your views here.
global audio_text
global text_area
audio_text = ""
text_area = ""
global count
count = False
global patient_name 
global patient_email
patient_name = ""
patient_email = ""
global data
data = [['DRUG', 'DURATION', 'STRENGTH', 'ROUTE','FORM','DOSAGE','FREQUENCY']]

def get_audio_text():
    return globals()['audio_text']


def set_audio_text(text):
    globals()['audio_text'] = text


def index(request):
    return render(request, 'index.html')


def register(request):
    return render(request, 'register.html')


def profile(request):
    current_user = request.user
    email_id = current_user.email
    
    doctor = Doctor.objects.filter(d_email=email_id).first()

    doctor_name = doctor.d_name
    doctor_contact = doctor.d_contactNo
    hospital_name = doctor.hospital_name
    specialization = doctor.specialization
    return render(request, 'profile.html',{'doctor_contact' : doctor_contact,'hospital_name' : hospital_name,'specialization':specialization, 'doctor_name':doctor_name})


def dashboard(request):
    return render(request, 'dashboard.html')


def newPatient(request):
    return render(request, 'new-patient.html')


def userLogin(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = auth.authenticate(username=username, password=password)

        if user is not None:
            auth.login(request, user)
            return render(request, 'dashboard.html')
        else:
            messages.error(request, "Invalid credentials! Try again with correct email id and password")
            print("Invalid credentials!")
            return redirect('/')
            
    else:
        return render(request, 'index.html')

# Minimum eight characters, at least one letter and one number

def passwordCheck(request, password):
    regex = "^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$"
    pattern = re.compile(regex)
    match = re.search(pattern, password)

    if not match:
        messages.error(request, "Password should contain : minimum eight characters, at least one letter and one number")
        return 0
    else:
        return 1

def textValidation(request, text):
    regex = "^[a-zA-Z ]*$"
    pattern = re.compile(regex)
    match = re.search(pattern, text)

    if not match:
        messages.error(request, "Only text is allowed!")
        return 0
    else:
        return 1

def contactValidation(request, num):
    regex = "^\d{10}$"
    pattern = re.compile(regex)
    match = re.search(pattern, num)

    if not match:
        messages.error(request, "Enter contact number properly!")
        return 0
    else:
        return 1

def userRegistration(request):
    if request.method == 'POST':
        name = request.POST['name']
        # username = request.POST['username']
        email = request.POST['email']
        contact_no = request.POST['contact_no']
        password = request.POST['password']
        state = request.POST['state']
        city = request.POST['city']
        speciality = request.POST['speciality']
        username = email
        hospital = request.POST['hospital']
        
        if((not textValidation(request, name)) or  (not textValidation(request, city)) or (not textValidation(request, hospital))):
            return render(request, 'register.html')

        elif(not contactValidation(request, contact_no)):
            return render(request, 'register.html')

        elif(not passwordCheck(request, password)):
            return render(request, 'register.html')

        else:
            user = User.objects.create_user(
                password=password,
                email=email,
                first_name=name,
                username=username
            )

            user.save()

            doctor = Doctor(d_email=email, d_name=name, d_contactNo=contact_no, state=state, city=city, hospital_name=hospital, specialization=speciality)
            doctor.save()

            print('User created: ', doctor.doctor_id)
            return redirect('/')
    else:
        return render(request, 'register.html')


def logout(request):
    print("Logout called")
    auth.logout(request)
    return redirect('/')


def record(request):
    globals()['count'] = not globals()['count']
    while globals()['count'] == True:
        r = sr.Recognizer()
        with sr.Microphone() as source:
            r.adjust_for_ambient_noise(source, duration=0.1)
            audio_data = r.listen(source)
            print("Recognizing...")
            try:
                audio_text = r.recognize_google(audio_data)
                globals()['audio_text'] = globals()['audio_text'] + audio_text
                print("Text: "+globals()['audio_text'])
            except:
                audio_text = ""
                globals()['audio_text'] = globals()['audio_text'] + audio_text
                print("Sorry, I did not get that")
    return render(request, 'new-patient.html', {'audio_text': globals()['audio_text']})


def proceed(request):
    return render(request, 'record-proceed.html', {'audio_text': globals()['audio_text']})
    
def save_changes(request):
    if request.method == 'GET':
         data = request.GET['fulltextarea']
         globals()['text_area'] = data
         globals()['audio_text'] = globals()['text_area']
    print(globals()['audio_text'])
    test_input = globals()['audio_text']
    extract_ner(test_input.lower())
    return render(request, 'signature.html')

def extract_ner(text):
    re_tok = re.compile(f"([{string.punctuation}“”¨«»®´·º½¾¿¡§£₤‘’])")
    sentence_test = re_tok.sub(r"  ", text).split()
    padded_sentence = sentence_test + [word2idx["ENDPAD"]] * (50 - len(sentence_test))
    padded_sentence = [word2idx.get(w, 0) for w in padded_sentence]
    loaded_model = keras.models.load_model('model_weights.h5')
    pred = loaded_model.predict(np.array([padded_sentence]))
    pred = np.argmax(pred, axis=-1)
    print("{:15}\t {}\n".format("Word","Pred"))
    print("-" *30)
    ne_tagged = []
    for w, pre in zip(padded_sentence, pred[0]):
        if words[w-1] in text:
            print("{:15}\t{}".format(words[w-1], tags[pre]))
            ne_tagged.append((words[w-1],tags[pre]))
    bio_tagged = []
    prev_tag = "O"
    for token, tag in ne_tagged:
        if tag == "O": #O
            bio_tagged.append((token, tag))
            prev_tag = tag
            continue
        if tag != "O" and prev_tag == "O": # Begin NE
            bio_tagged.append((token, tag))
            prev_tag = tag
        elif prev_tag != "O" and prev_tag == tag: # Inside NE
            l1 = bio_tagged.pop()
            bio_tagged.append((l1[0]+" "+token, tag))
            prev_tag = tag
        elif prev_tag != "O" and prev_tag != tag: # Adjacent NE
            bio_tagged.append((token, tag))
            prev_tag = tag
    print(bio_tagged)
    sentence_list = []
    i = 0
    temp = []
    count = 0
    while i < len(bio_tagged):
        token,tag = bio_tagged[i]
        print(token)
        if token == 'take':
            count = count + 1
            print(count)
            if count == 1:
                temp.append(bio_tagged[i])
                i = i + 1 
            else:
                sentence_list.append(temp)
                temp = []
                temp.append(bio_tagged[i])
                i = i + 1
        else:
            temp.append(bio_tagged[i])
            i = i + 1
    sentence_list.append(temp)
    print(sentence_list)
    data = [['DRUG', 'DURATION', 'STRENGTH', 'ROUTE','FORM','DOSAGE','FREQUENCY']]
    for sentence in sentence_list:
        row = ['','','','','','','']
        for token,tag in sentence:
            if tag == 'B-Drug' or tag == 'I-Drug':
                row[0] += " "+token
            elif tag == 'B-Duration' or tag == 'I-Duration':
                row[1] += " "+token
            elif tag == 'B-Strength' or tag == 'I-Strength':
                row[2] += " "+token
            elif tag == 'B-Route' or tag == 'I-Route':
                row[3] += " "+token
            elif tag == 'B-Form' or tag == 'I-Form':
                row[4] += " "+token
            elif tag == 'B-Dosage' or tag == 'I-Dosage':
                row[5] += " "+token
            elif tag == 'B-Frequency' or tag == 'I-Frequency':
                row[6] += " "+token
        data.append(row)
    for i in range(len(data)):
        for j in range(len(data[i])):
            if data[i][j] == '':
                data[i][j] = ' NA'
    
    globals()['data'] = data
    #print(globals()['data'])
    #return null
#test_input = "Take crocin for two days and paracetamol for 3 days"
#test_input = "The patient has Type 2 diabetes.Take Metformin Fortamet Glumetza twice a day for 6 months."
#extract_ner(test_input)

def mailPrescription():
    # receiver gmail id
    # sender : prescribometer / doctor
    # attachment
    dated = date.today()
    patient = globals()['patient_name']
    email = globals()['patient_email']
    # email = 'aayushisutaria017@gmail.com'
    subject = f'Prescribometer: Prescription {dated}'
    message = f"""
        Hi {patient}, 
        PFA prescription..
        Get Well Soon ...'
    """
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [email, ]
    msg = EmailMessage(subject, message, email_from, recipient_list)
    msg.content_subtype = "html"  
    msg.attach_file('prescription.pdf')
    msg.send()

    

def generate(request):
    if request.method == 'GET':

        current_user = request.user
        email_id = current_user.email
        
        # doctor = Doctor.objects.get(d_email=email_id)
        doctor = Doctor.objects.filter(d_email=email_id).first()

        doctor_name = doctor.d_name
        doctor_contact = doctor.d_contactNo
        hospital_name = doctor.hospital_name
        specialization = doctor.specialization

        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size = 15)
        pdf.set_fill_color(102,224,255)
        pdf.cell(190, 20,'PRESCRIBOMETER', 0, 1, 'C', fill=True)
        # pdf.cell(200, 10, txt = "",ln = 1, align = 'C')

        current_date = date.today()
        pdf.set_font("Arial", size = 15)
        pdf.cell(190, 10, txt = hospital_name.upper() ,ln = 1, align = 'C')
        pdf.set_font("Arial", size = 12)
        pdf.cell(190, 10, txt = "Dr. " + doctor_name ,ln = 1, align = 'L')
        pdf.cell(190, 10, txt = specialization, ln = 1, align = 'L')
        # pdf.cell(190, 10, txt = "Date: ", ln = 1, align = 'L')
        pdf.cell(190, 10, txt = "Email: " + email_id ,ln = 1, align = 'L')
        pdf.cell(190, 10, txt = "Contact: " + str(doctor_contact) ,ln = 1, align = 'L')
        pdf.cell(190, 10, txt = "",ln = 1, align = 'C')
        pdf.cell(190, 10,txt = "Patient Name :" + str(globals()['patient_name']), ln = 1,align = 'R')
        pdf.cell(190, 10, txt = "Diagnosed with :",ln = 1, align = 'L')
        pdf.cell(190, 10, txt = "",ln = 1, align = 'C')


        # Table
        spacing = 2
        pdf.set_font("Times", size=10)
   
        col_width = pdf.w / 8.0
        row_height = pdf.font_size
        print(globals()['data'])
        for row in globals()['data']:
            for item in row:
                pdf.cell(col_width, row_height*spacing,txt=item, border=1)
            pdf.ln(row_height*spacing)
        
        for i in range(0,5):
            pdf.cell(190, 10, txt = "",ln = 1, align = 'C')
        pdf.image('C:/Users/Admin/Downloads/signature.png',x = 150, w = 50)

        # save the pdf with name .pdf
        pdf.output("prescription.pdf")
        os.startfile('prescription.pdf', 'open')
        #subprocess.call(['open', 'prescription.pdf'])

        mailPrescription()
        messages.success(request, "Email sent to the patient successfully!")
    return render(request, 'dashboard.html')

def submit_patient(request):
    if request.method == 'POST':
        globals()['patient_name'] = request.POST['patient_name']
        globals()['patient_email'] = request.POST['patient_email']
    print("NAME :" +globals()['patient_name'])
    return render(request, 'new-patient.html')