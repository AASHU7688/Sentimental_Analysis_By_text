from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.views.decorators.csrf import csrf_exempt
import numpy as np
import joblib
import google.generativeai as genai
import re
import json
import pickle

from django.views.decorators.csrf import csrf_exempt
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences

# Load the saved LSTM model and tokenizer
model = load_model("static/sentiment_lstm.h5")
with open("static/tokenizer.pkl", "rb") as f:
    tokenizer = pickle.load(f)

# Maximum length used during training
MAXLEN = 200  

# Labels for prediction
labels = {0: "Negative", 1: "Neutral", 2: "Positive"}

@csrf_exempt
def prediction(request):
    output = None

    if request.method == 'POST':
        user_text = request.POST.get('text')

        try:
            # --- RULE BASED QUICK CLASSIFICATION ---
            keywords_positive = ["good", "great", "excellent", "amazing", "happy", "love", "awesome"]
            keywords_negative = ["bad", "worst", "awful", "sad", "angry", "hate", "terrible"]

            text_lower = user_text.lower()

            if any(word in text_lower for word in keywords_positive):
                output = {
                    'sentiment': 'Positive',
                    'score': 90,
                    'emotions': ['joy', 'satisfaction'],
                    'phrases': [w for w in keywords_positive if w in text_lower]
                }
            elif any(word in text_lower for word in keywords_negative):
                output = {
                    'sentiment': 'Negative',
                    'score': 90,
                    'emotions': ['anger', 'sadness'],
                    'phrases': [w for w in keywords_negative if w in text_lower]
                }
            else:
                # --- ML MODEL PREDICTION ---
                # Convert text → sequence
                seq = tokenizer.texts_to_sequences([user_text])
                padded = pad_sequences(seq, maxlen=100)

                prediction = model.predict(padded)[0][0]

                if prediction > 0.6:
                    sentiment = "Positive"
                elif prediction < 0.4:
                    sentiment = "Negative"
                else:
                    sentiment = "Neutral"

                output = {
                    'sentiment': sentiment,
                    'score': round(float(prediction) * 100, 2),
                    'emotions': [],
                    'phrases': []
                }

        except Exception as e:
            output = {
                'sentiment': 'Error',
                'score': 0,
                'emotions': [],
                'phrases': [f"Error: {str(e)}"]
            }

    return render(request, 'prediction.html', {'output': output})


# Create your views here.

def index(request):
    return render(request,'index.html')


def about(request):
    return render(request,'about.html')

def contact(request):
    return render(request,'contact.html')
def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)  # Use Django's login function
            return redirect('home')  # Redirect to home page or any desired page
        else:
            # Handle invalid login
            return render(request, 'login.html', {'error': 'Invalid credentials'})
    else:
        return render(request, 'login.html')
    

def signup(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')
        email = request.POST.get('email_or_phone')  # Adjusted field name to match the form
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        # Check if passwords match
        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return render(request, 'signup.html')

        # Check if username is already taken
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username is already taken.")
            return render(request, 'signup.html')

        # Check if username is alphanumeric and not purely numeric
        if not username.isalnum() or username.isnumeric():
            messages.error(request, "Username must contain both letters and numbers, and it can't be purely numeric.")
            return render(request, 'signup.html')

        # Create the user and set additional fields
        try:
            user = User.objects.create_user(username=username, email=email, password=password)
            user.first_name = first_name  # Set first name
            user.last_name = last_name  # Set last name
            user.save()

            messages.success(request, "Account created successfully.")
            return redirect('login')  # Redirect to login page after successful signup
        except ValidationError as e:
            messages.error(request, str(e))
            return render(request, 'signup.html')

    return render(request, 'signup.html')




def profile(request):
    if request.user.is_authenticated:
        return render(request, 'profile.html', {'user': request.user})
    else:
        return redirect('login')  # Redirect to login if not authenticated
