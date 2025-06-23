from django.shortcuts import render, HttpResponse, redirect
from django.core.mail import send_mail
from django.core.mail import EmailMessage
from .models import Test, AccessTokendb as ATT
from django.contrib import messages

import requests
import datetime
import time
import csv
import os

# Create your views here.

# generate csv file function.
def generatecsv(ACCESS_TOKEN):
    # Google Fit endpoint for aggregated data (steps, distance, etc.)
    URL = "https://www.googleapis.com/fitness/v1/users/me/dataset:aggregate"


    end_time_millis = int(time.time() * 1000)
    start_time_millis = end_time_millis - (15 * 24 * 60 * 60 * 1000)

    # Request payload for step count data
    payload = {
        "aggregateBy": [{
            "dataTypeName": "com.google.step_count.delta",
            "dataSourceId": "derived:com.google.step_count.delta:com.google.android.gms:estimated_steps"
        }
        ],
        "bucketByTime": { "durationMillis": 86400000 },  # daily bucket
        "startTimeMillis": start_time_millis,
        "endTimeMillis": end_time_millis
    }

    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }

    response = requests.post(URL, json=payload, headers=headers)

    if response.status_code == 200:
        data = response.json()
        rows = []
        print("Google Fit Step Count (Last 24h):")
        for bucket in data["bucket"]:
            start = int(bucket["startTimeMillis"])
            end = int(bucket["endTimeMillis"])
            date_str = time.strftime('%Y-%m-%d', time.localtime(start / 1000))
            for dataset in bucket["dataset"]:
                for point in dataset["point"]:
                    steps = point["value"][0]["intVal"]
                    rows.append([date_str, steps])
                    print(f"Steps: {steps}")
        filename = "google_fit_steps.csv"
        with open(filename, mode="w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["Date", "Steps"])  # Header
            writer.writerows(rows)

        print("✅ Step data saved to google_fit_steps.csv")
        full_path = os.path.abspath(filename)
        print(f"✅ Step data saved to: {full_path}")
        return True
    else:
        print(f"Error: {response.status_code}")
        return False


def send_mail_csv(mail,file_mail):
    subject = 'CSV Report Attached'
    body = 'Please find the attached CSV file.'
    from_email = 'praveenkumarreddy1202@example.com'
    to_email = mail

    email = EmailMessage(subject, body, from_email, to_email)

    csv_path = os.path.join(os.getcwd(), 'google_fit_steps.csv')
    
    file_mail = file_mail
    file_name = str(file_mail).split('@')[0]
    # Attach the CSV file
    with open(csv_path, 'rb') as f:
        email.attach(file_name, f.read(), 'text/csv')

    # Send the email
    email.send()

def signin(request):
    return render(request,'signin.html')

def done(request):
    try :
        token = request.GET.get('accessToken')
        mail = []
        # mail.append("siddesh.bijavara@gmail.com")
        mail.append(request.GET.get('email'))

        generatecsv(token)
        obj = ATT.objects.update_or_create(
        email=request.GET.get('email'),
    defaults={
        'firstName': 'testuser',
        'token': token
    }
        )
        # obj.save()
        
        # send_mail_csv(mail)
    except Exception as e :
        print("Error :- \n\n ",e)
        messages.error(request,f"An Error occured : - email = {mail} {str(e)}")
            
        return redirect('home')
    
    print("Done")
    return render(request,'done.html')

def generateCsv_db():
    tokens = ATT.objects.values_list('token',flat=True)
    mail = ATT.objects.values_list('email',flat=True)
    # tst = Test.objects.values_list('token',flat=True)
    for token,mail in zip(tokens,mail) :
        print(mail)
        generate = generatecsv(token)

        if generate :
            print("email is sending...")
            send_mail_csv(["siddesh.bijavara@gmail.com","jobcracking907@gmail.com"],mail)
        
    return tokens

def generateCsvtoAll(request):
    tk = generateCsv_db()

    return HttpResponse(tk)

def privacy(request):
    return render(request,"privacy.html")

def terms(request):
    return render(request,"terms.html")


