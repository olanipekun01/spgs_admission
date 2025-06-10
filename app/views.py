from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.urls import reverse
# from .forms import UserSignupForm, StudentSignupForm, InstructorSignupForm
from .models import *
from django.db.models import Max, Q, F
import uuid
import random
import string
import json

import os

import fpdf
from fpdf import FPDF, HTMLMixin

from django.http import HttpResponse
from django.template.loader import render_to_string

# from weasyprint import HTML

# from io import BytesIO
# from django.template.loader import get_template
# from xhtml2pdf import pisa

from django.contrib.auth.models import User, auth
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin


from django.shortcuts import render, redirect
from django.contrib.auth.models import User, auth
from django.contrib.auth.tokens import default_token_generator
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm
from django.contrib.auth import get_user_model
from django.forms.models import model_to_dict


from django.contrib import messages

# Create your views here.
def Signup(request):
    if request.method == "POST":
        email = request.POST["email"]
        password = request.POST["password"]
        firstName = request.POST["firstName"]
        lastName = request.POST["lastName"]
        confirmPassword = request.POST["confirmPassword"]

        if len(password) < 8:
            messages.info(request, "Password too short!")
            redirect('/accounts/signup')

        if password != confirmPassword:
            messages.info(request, "Password doesn't match!")
            redirect('/accounts/signup')

        # Validate form fields (you can add more complex validation if needed)
        if not (firstName and lastName and email):
            messages.error(request, "Please fill out all required fields.")
            return redirect("/accounts/signup")  # Replace 'signup' with your signup view's URL name

        # Check for duplicate email
        if Application.objects.filter(applicant__username=email).exists():
            messages.error(request, "Email is already registered.")
            return redirect("/accounts/signup")
        
        
        user = CustomUser.objects.create(username=email, password=password, user_type="student")
        user.save()
        return redirect("/accounts/login")

    return render(request, "./authentication/signup.html")

def Login(request):
    if request.user.is_authenticated:
        user = request.user
        return redirect("/apply/start")
    if request.method == "POST":
        email = request.POST["email"]
        password = request.POST["password"]

        try:
            # user = auth.authenticate(username=email, password=password)
            user = authenticate(request, username=email, password=password)
            # user = User.objects.get(email=email)
            # if user.check_password(password):
            #     # Log the user in (assuming you're using Django's session framework)
            # login(request, user)
            #     return redirect('/')  # Redirect to the dashboard or homepage
            # else:
            #     error_message = "Invalid password."
            print('user', user)
            if user is not None:
                auth.login(request, user)
                return redirect("/apply/start")
                # 
                # if user.user_type == "student":
                #     return redirect("/")
                # elif user.user_type == "instructor":
                #     return redirect("/instructor/dashboard")
                # else:
                #     # Redirect user to a 404 page
                #     return redirect("/404")
            # elif user is not None and user.user_type == 'student':

            else:
                messages.error(request, "Invalid credentials!")
                return redirect('/accounts/login')
                # return render(request, "./authentication/login.html", {"error": error_message})
        except User.DoesNotExist:
            messages.error(request, "Invalid credentials!")
            return redirect('/accounts/login')
            # return render(request, "./authentication/login.html", {"error": error_message})

    return render(request, "./authentication/login.html")

@login_required
def logout(request):
    auth.logout(request)
    return redirect("/accounts/login")