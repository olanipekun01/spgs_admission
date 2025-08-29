from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.urls import reverse
# from .forms import UserSignupForm, StudentSignupForm, InstructorSignupForm
from .models import *
from common.models import *
from django.db.models import Max, Q, F
import uuid
import random
import string
import json

import re

import os

import fpdf
from fpdf import FPDF, HTMLMixin

from django.http import HttpResponse
from django.template.loader import render_to_string

from django.core.exceptions import ValidationError

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
from django.views.decorators.csrf import csrf_exempt


from django.contrib import messages

from datetime import datetime
from django.utils import timezone


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
        
        current_session = Session.objects.filter(is_current=True).first()
        if not current_session:
            messages.error(request, "No current session is available.")
            return redirect("/accounts/signup")
            
        
        user = CustomUser.objects.create(username=email, first_name=firstName, last_name=lastName, email=email, user_type="student")
        user.set_password(password)
        user.save()
        messages.error(request, "Account Successfully created login now!")
        return redirect("/accounts/login")

    return render(request, "./application/signup.html")


def Login(request):
    if request.user.is_authenticated:
        user = request.user
        return redirect("/apply/start")
    if request.method == "POST":
        email = request.POST["email"]
        password = request.POST["password"]
        print('we go here')
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
                return redirect("/apply/dashboard")
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

    return render(request, "./application/login.html")

@login_required
def logout(request):
    auth.logout(request)
    return redirect("/accounts/login")


@login_required
def dashboard(request):
    if request.user.is_authenticated:
        user = request.user
     # Fetch the current session (assuming Session has an 'is_current' field)
    current_session = Session.objects.filter(is_current=True).first()
    if not current_session:
        messages.error(request, "No current session available!")
        context = {
            "sess": current_session,
        }
    else:
        if request.method == "POST":  # Ensure the new application is only created on form submission
                new_application = Application.objects.create(applicant=user, session=current_session)
                messages.error(request, "Application Started! Proceed to make payment")
                return redirect('/apply/dashboard')
    
        # Check if the user already has an application for the current session
        application = Application.objects.filter(applicant=user, session=current_session).first()

        context = {
            "sess": current_session,
            "applicant": application
        }
    return render(request, "./application/dashboard.html", context)

@login_required
# @user_passes_test(is_student, login_url="/404")
def ApplyPayment(request):
    if request.user.is_authenticated:
        user = request.user
        applicant = get_object_or_404(Application, applicant=user)
    # programmes = Programme.objects.all()
    current_session = Session.objects.filter(is_current=True).first()

    

    if current_session:

        application = Application.objects.filter(applicant=user, session=current_session).first()
        if not application:
            # If PersonalDetails is not completed, redirect to /apply/1
            messages.info(request, "Please start an application!.")
            return redirect('/apply/dashboard')
        
        try:
        # your logic here
            payment = Payment.objects.filter(applicant=applicant, session=current_session).first()
        except Exception as e:
            print("Error:", e)  # Or use logging
        
        
        if payment:
            messages.info(request, "Continue application!.")
            return redirect('/apply/dashboard')

    # Fetch all available programmes for the form
    programmes = Programme.objects.all()
    

    return render(request, "./application/payment.html", {'current_session': current_session, 'user': user})

@csrf_exempt  # Remove this if you're using a form with CSRF token
@login_required
def ApplyPaymentConfirm(request):
    if request.method == 'POST':
        transaction_ref = request.POST.get("transactionRef")
        payment_ref = request.POST.get("paymentRef")

        if not transaction_ref and not paymemt_ref:
            messages.error(request, "Transaction Ref or Payment Ref missing.")
            return redirect('/apply/payment')

        user = request.user
        current_session = Session.objects.filter(is_current=True).first()

        try:
            applicant = Application.objects.get(applicant=user, session=current_session)
        except Application.DoesNotExist:
            messages.error(request, "Application not found.")
            return redirect('/apply/dashboard')

        # Placeholder: Verify payment with Monnify API
        #     # In production, use Monnify's API to verify transaction_ref
        #     print(f"Payment Confirmation: TransactionRef={transaction_ref}, PaymentRef={payment_ref}")
            
        payment, created = Payment.objects.get_or_create(
            applicant=applicant,
            session=current_session,
            defaults={'hasPayed': True, 'transRef': transaction_ref, 'payRef': payment_ref}
        )

        if not created:
            payment.hasPayed = True
            payment.transRef = transaction_ref
            payment.save()

        applicant.has_paid = True
        applicant.payment_reference = payment_ref
        applicant.save()

        messages.success(request, "Payment confirmed successfully. Continue Application")
        return redirect('/apply/dashboard')  # Redirect to the next step
    else:
        return redirect('/apply/payment')

@login_required
# @user_passes_test(is_student, login_url="/404")
def ApplyOne(request):
    if request.user.is_authenticated:
        user = request.user
        applicant = get_object_or_404(Application, applicant=user)
    # programmes = Programme.objects.all()
    current_session = Session.objects.filter(is_current=True).first()
    context = {}
    if current_session:

        application = Application.objects.filter(applicant=user, session=current_session).first()
        if not application:
            # If PersonalDetails is not completed, redirect to /apply/1
            messages.info(request, "Please start here first.")
            return redirect('/apply/dashboard')


        personal_details = PersonalInfo.objects.filter(applicant=applicant, session=current_session).first()
        
        if personal_details:
        #     return redirect('/apply/2')
            print("details1", personal_details.surname)
            context["personal"] = personal_details
            context["applicant"] = application

    # Fetch all available programmes for the form
    programmes = Programme.objects.all()
    departments = Department.objects.all()
    colleges = College.objects.all()
    context['programme'] = programmes
    context['college'] = colleges
    context['department'] = departments

    if request.method == "POST":
        # Retrieve data from the POST request
        department = request.POST.get('department', "")
        college = request.POST.get('faculty', "")
        programme = request.POST.get('programme', "")
        area_of_specialization = request.POST.get('areaOfSpecialization', "")
        title = request.POST.get("title", "")
        first_name = request.POST.get("firstName", "")
        middle_name = request.POST.get("middleName", "")
        surname = request.POST.get("surname", "")
        mailing_address = request.POST.get("mailingAddress", "")
        email = request.POST.get("email", "")
        mobile_phone = request.POST.get("mobilePhone", "")
        date_of_birth = request.POST.get("dateOfBirth", None)
        place_of_birth = request.POST.get("placeOfBirth", "")
        state_of_origin = request.POST.get("stateOfOrigin", "")
        nationality = request.POST.get("nationality", "")
        gender = request.POST.get("gender", "")
        marital_status = request.POST.get("maritalStatus", "")
        religious_affiliation = request.POST.get("religiousAffiliation", "")
        other_religion = request.POST.get("otherReligion", "")
        
        try:
            # Update or create PersonalInfo record
            if personal_details:
                # Update existing record
                personal_details.title = title
                personal_details.first_name = first_name
                personal_details.middle_name = middle_name
                personal_details.surname = surname
                personal_details.mailing_address = mailing_address
                personal_details.mobile_phone = mobile_phone
                personal_details.email = email
                personal_details.date_of_birth = date_of_birth
                personal_details.place_of_birth = place_of_birth
                personal_details.state_of_origin = state_of_origin
                personal_details.nationality = nationality
                personal_details.gender = gender
                personal_details.marital_status = marital_status
                personal_details.religious_affiliation = religious_affiliation
                personal_details.other_religion = other_religion
                personal_details.save()
            else:
                # Create new record
                personal_info = PersonalInfo.objects.create(
                    applicant=application,
                    title=title,
                    first_name=first_name,
                    middle_name=middle_name,
                    surname=surname,
                    mailing_address=mailing_address,
                    mobile_phone=mobile_phone,
                    email=email,
                    date_of_birth=date_of_birth,
                    place_of_birth=place_of_birth,
                    state_of_origin=state_of_origin,
                    nationality=nationality,
                    gender=gender,
                    marital_status=marital_status,
                    religious_affiliation=religious_affiliation,
                    other_religion=other_religion,
                    session=current_session
                )

            # Update Application model
            application.programme = programme
            application.area_of_specialization = area_of_specialization
            application.college = college
            application.department = department
            application.save()

            messages.success(request, "Personal Info Saved!")
            return redirect('/apply/2')
        except Programme.DoesNotExist:
            messages.info(request, "Programme doesn't exist!")
            return redirect('/apply/1')
        except Session.DoesNotExist:
            messages.info(request, "Session doesn't exist!")
            return redirect('/apply/1')
        except Exception as e:
            messages.info(request, "Invalid request!")
            return redirect('/apply/1')


    return render(request, "./application/applyone.html", context)

@login_required
def ApplyTwo(request):
    if request.user.is_authenticated:
        user = request.user
        applicant = get_object_or_404(Application, applicant=user)
        # applicant = application.applicant
        current_session = Session.objects.filter(is_current=True).first()
        context = {}

        months = [
            "January", "February", "March", "April", "May", "June",
            "July", "August", "September", "October", "November", "December"
        ]
        
        current_year = datetime.now().year
        years = [str(current_year - i) for i in range(50)]
        degreeTypes = [
            "Bachelor of Science (B.Sc.)",
            "Bachelor of Arts (B.A.)",
            "Bachelor of Engineering (B.Eng.)",
            "Bachelor of Technology (B.Tech.)",
            "Higher National Diploma (HND)",
            "National Diploma (ND)",
            "Master of Science (M.Sc.)",
            "Master of Arts (M.A.)",
            "Master of Engineering (M.Eng.)",
            "Master of Business Administration (MBA)",
            "Doctor of Philosophy (Ph.D.)",
            "Other (Please specify in institution field)"
        ]

        # Fetch existing educational records and transcript instructions
        educational_records = EducationalRecord.objects.filter(applicant=applicant, session=current_session)
        transcript_instructions = TranscriptInstructions.objects.filter(applicant=applicant, session=current_session).first()
        
        context['educational_records'] = educational_records
        context['transcript_instructions'] = transcript_instructions.instructions if transcript_instructions else "The Dean of Postgraduate Studies, Achievers University, Km 1, Idasen-Ute Road, Owo, Ondo State, Nigeria."
        # context['application_id'] = application_id
        context['degree_types'] = degreeTypes
        context['months'] = months
        context['years'] = years

        if request.method == "POST":
            # Retrieve data from POST
            records = []
            i = 0
            while f'records[{i}][institution]' in request.POST:
                records.append({
                    'id': request.POST.get(f'records[{i}][id]', ''),
                    'institution': request.POST.get(f'records[{i}][institution]', ''),
                    'diploma_degree': request.POST.get(f'records[{i}][diplomaDegree]', ''),
                    'from_month': request.POST.get(f'records[{i}][fromMonth]', ''),
                    'from_year': request.POST.get(f'records[{i}][fromYear]', ''),
                    'to_month': request.POST.get(f'records[{i}][toMonth]', ''),
                    'to_year': request.POST.get(f'records[{i}][toYear]', ''),
                    'currently_enrolled': request.POST.get(f'records[{i}][currentlyEnrolled]', '') == 'on',
                })
                i += 1
            transcript_instructions_text = request.POST.get('transcriptInstructions', '')

            try:
                # Validate records
                for record in records:
                    if not record['institution'] or not record['diploma_degree'] or not record['from_month'] or not record['from_year']:
                        messages.error(request, "All required fields must be filled for each educational record.")
                        return redirect('/apply/2/')
                    if not record['currently_enrolled'] and (not record['to_month'] or not record['to_year']):
                        messages.error(request, "End date is required unless currently enrolled.")
                        return redirect('/apply/2/')

                # Update or create educational records
                existing_record_ids = set(EducationalRecord.objects.filter(applicant=applicant, session=current_session).values_list('applicant__id', flat=True))
                submitted_record_ids = set(record['id'] for record in records if record['id'])

                # Delete removed records
                for record_id in existing_record_ids - submitted_record_ids:
                    EducationalRecord.objects.filter(id=record_id, applicant=applicant, session=current_session).delete()

                # Create or update records
                for record in records:
                    if record['id']:
                        # Update existing record
                        edu_record = EducationalRecord.objects.get(id=record['id'], applicant=applicant, session=current_session)
                        edu_record.institution = record['institution']
                        edu_record.diploma_degree = record['diploma_degree']
                        edu_record.from_month = record['from_month']
                        edu_record.from_year = record['from_year']
                        edu_record.to_month = record['to_month']
                        edu_record.to_year = record['to_year']
                        edu_record.currently_enrolled = record['currently_enrolled']
                        edu_record.save()
                    else:
                        # Create new record
                        EducationalRecord.objects.create(
                            applicant=applicant,
                            session=current_session,
                            institution=record['institution'],
                            diploma_degree=record['diploma_degree'],
                            from_month=record['from_month'],
                            from_year=record['from_year'],
                            to_month=record['to_month'],
                            to_year=record['to_year'],
                            currently_enrolled=record['currently_enrolled']
                        )

                # Update or create transcript instructions
                if transcript_instructions:
                    transcript_instructions.instructions = transcript_instructions_text
                    transcript_instructions.save()
                else:
                    TranscriptInstructions.objects.create(
                        applicant=applicant,
                        session=current_session,
                        instructions=transcript_instructions_text
                    )

                messages.success(request, "Educational history saved successfully!")
                return redirect('/apply/3/')  # Adjust to your next step
            except Exception as e:
                messages.error(request, f"Error saving educational history: {str(e)}")
                return redirect('/apply/2/')

        return render(request, "./application/applytwo.html", context)

    
def ApplyThree(request):
    if request.user.is_authenticated:
        user = request.user
        applicant = get_object_or_404(Application, applicant=user)
        # applicant = application.applicant
        current_session = Session.objects.filter(is_current=True).first()
        context = {}

        # Fetch existing work experience data
        work_experience = ApplicationWorkExperience.objects.filter(applicant=applicant, session=current_session).first()
        work_records = WorkExperienceRecord.objects.filter(applicant=applicant, session=current_session).order_by('-current_position', '-to_year', '-to_month')

        context['work_experience'] = work_experience
        context['work_records'] = work_records
        context['has_no_experience'] = work_experience.has_no_experience if work_experience else False
        # context['application_id'] = application_id

        # Add months, years, and current year
        context['months'] = [
            "January", "February", "March", "April", "May", "June",
            "July", "August", "September", "October", "November", "December"
        ]
        current_year = datetime.now().year
        context['years'] = [str(current_year - i) for i in range(10)]  # Past 10 years
        context['current_year'] = current_year

        if request.method == "POST":
            try:
                has_no_experience = 'no-experience' in request.POST and request.POST['no-experience'] == 'on'
                records = []
                i = 0
                while f'records[{i}][position]' in request.POST:
                    records.append({
                        'id': request.POST.get(f'records[{i}][id]', ''),
                        'position': request.POST.get(f'records[{i}][position]', ''),
                        'employer': request.POST.get(f'records[{i}][employer]', ''),
                        'from_month': request.POST.get(f'records[{i}][fromMonth]', ''),
                        'from_year': request.POST.get(f'records[{i}][fromYear]', ''),
                        'to_month': request.POST.get(f'records[{i}][toMonth]', ''),
                        'to_year': request.POST.get(f'records[{i}][toYear]', ''),
                        'current_position': request.POST.get(f'records[{i}][currentPosition]', '') == 'on',
                        'responsibilities': request.POST.get(f'records[{i}][responsibilities]', ''),
                    })
                    i += 1

                # Validate records if not no experience
                if not has_no_experience:
                    for record in records:
                        if not record['position'] or not record['employer'] or not record['from_month'] or not record['from_year'] or not record['responsibilities']:
                            messages.error(request, "All required fields must be filled for each work experience record.")
                            return redirect('/apply/3/')
                        if not record['current_position'] and (not record['to_month'] or not record['to_year']):
                            messages.error(request, "End date is required unless current position.")
                            return redirect('/apply/3/')
                        from_year = int(record['from_year']) if record['from_year'] else 0
                        if from_year < (current_year - 5):
                            messages.error(request, f"Work experience must be from the past 5 years ({current_year - 5} onwards).")
                            return redirect('/apply/3/')

                # Update or create work experience flag
                if work_experience:
                    work_experience.has_no_experience = has_no_experience
                    work_experience.save()
                else:
                    work_experience = ApplicationWorkExperience.objects.create(
                        applicant=applicant,
                        session=current_session,
                        has_no_experience=has_no_experience
                    )

                # Handle records
                if has_no_experience:
                    WorkExperienceRecord.objects.filter(applicant=applicant, session=current_session).delete()
                else:
                    existing_record_ids = set(WorkExperienceRecord.objects.filter(applicant=applicant, session=current_session).values_list('id', flat=True))
                    submitted_record_ids = set(record['id'] for record in records if record['id'])

                    # Delete removed records
                    for record_id in existing_record_ids - submitted_record_ids:
                        WorkExperienceRecord.objects.filter(id=record_id, applicant=applicant, session=current_session).delete()

                    # Create or update records
                    for record in records:
                        if record['id']:
                            work_record = WorkExperienceRecord.objects.get(id=record['id'], applicant=applicant, session=current_session)
                            work_record.position = record['position']
                            work_record.employer = record['employer']
                            work_record.from_month = record['from_month']
                            work_record.from_year = record['from_year']
                            work_record.to_month = record['to_month']
                            work_record.to_year = record['to_year']
                            work_record.current_position = record['current_position']
                            work_record.responsibilities = record['responsibilities']
                            work_record.save()
                        else:
                            WorkExperienceRecord.objects.create(
                                applicant=applicant,
                                session=current_session,
                                position=record['position'],
                                employer=record['employer'],
                                from_month=record['from_month'],
                                from_year=record['from_year'],
                                to_month=record['to_month'],
                                to_year=record['to_year'],
                                current_position=record['current_position'],
                                responsibilities=record['responsibilities']
                            )

                messages.success(request, "Work experience saved successfully!")
                return redirect('/apply/4/')  # Adjust to your next step
            except Exception as e:
                messages.error(request, f"Error saving work experience: {str(e)}")
                return redirect('/apply/3/')

        return render(request, "./application/applythree.html", context)

from django.forms import inlineformset_factory
from .forms import ProfessionalCredentialForm

ProfessionalCredentialFormSet = inlineformset_factory(
    ApplicationWorkExperience,
    ProfessionalCredential,
    form=ProfessionalCredentialForm,
    extra=5,  # Provide up to 5 empty forms initially
    max_num=5,  # Limit to 5 credentials
    can_delete=True,
)

def ApplyFour(request):
    if not request.user.is_authenticated:
        return redirect('/')

    user = request.user
    applicant = get_object_or_404(Application, applicant=user)
    current_year = timezone.now().year
    current_session = Session.objects.filter(is_current=True).first()

    # Get or create ApplicationWorkExperience instance
    application_work_experience, created = ApplicationWorkExperience.objects.get_or_create(
        applicant=applicant,
        session=current_session,
        defaults={'has_no_credentials': False}
    )

    credentials = ProfessionalCredential.objects.filter(application_work_experience=application_work_experience)

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'next':
            messages.success(request, "Credentials saved. Proceeding to next step.")
            return redirect('/apply/5/')
        
        elif action == 'save':
            credential_name = request.POST.get(f'credential_name')
            issuing_organization = request.POST.get(f'issuing_organization')
            issue_date = request.POST.get(f'issue_date')
            expiry_date = request.POST.get(f'expiry_date')
            credential_number = request.POST.get(f'credential_number')

            if credential_name and issuing_organization and issue_date:  # Required fields
                try:
                    issue_date = timezone.datetime.strptime(issue_date, '%Y-%m-%d').date()
                    expiry_date = timezone.datetime.strptime(expiry_date, '%Y-%m-%d').date() if expiry_date else None

                    # Validate dates
                    if expiry_date and issue_date and expiry_date <= issue_date:
                        raise ValidationError("Expiry date must be after issue date.")
                    if issue_date > timezone.now().date():
                        raise ValidationError("Issue date cannot be in the future.")

                    # Create or update credential
                    credential = ProfessionalCredential.objects.create(
                        application_work_experience=application_work_experience,
                        session= current_session,
                        credential_name=credential_name,
                        issuing_organization= issuing_organization,
                        issue_date=issue_date,
                        expiry_date=expiry_date,
                        credential_number=credential_number
                    )
                except ValueError as e:
                    messages.error(request, f"Invalid date format for Credential: {str(e)}")
                except ValidationError as e:
                    messages.error(request, f"Validation error for Credential: {str(e)}")

            # Remove any excess credentials beyond 3
            # existing_credentials = ProfessionalCredential.objects.filter(application_work_experience=application_work_experience).count()
            # if existing_credentials > 3:
            #     excess_credentials = ProfessionalCredential.objects.filter(application_work_experience=application_work_experience)[3:]
            #     excess_credentials.delete()

                messages.success(request, "Credentials saved successfully.")
                return redirect('/apply/4/')
        
    context = {
        'credentials': credentials,
        'has_no_credentials': application_work_experience.has_no_credentials,
        'current_year': current_year,
    }
    return render(request, './application/applyfour.html', context)



def CredDelete(request, id):
    if request.user.is_authenticated:
        user = request.user
        cred = get_object_or_404(ProfessionalCredential, id=id)
        cred.delete()
        
        messages.success(request, "Credentials deleted!")
        return redirect('/apply/4/')


def CredUpdate(request):
    if request.user.is_authenticated:
        user = request.user

        if request.method == 'POST':
            cred_name = request.POST.get("cred_name", "")
            issuing_organization = request.POST.get("issuing_organization", "")
            issue_date = request.POST.get("issue_date", "")
            expiry_date = request.POST.get("expiry_date", "")
            cred_number = request.POST.get("cred_number", "")
            cred_id = request.POST.get("cred_id", "")
            print(cred_id)
            try:
                credential = get_object_or_404(ProfessionalCredential, id=cred_id)

                credential.credential_name = cred_name
                credential.issuing_organization = issuing_organization
                credential.issue_date = issue_date
                credential.expiry_date = expiry_date
                credential.credential_number = cred_number

                credential.save()
                messages.success(request, "Credentials Updated!")
                return redirect('/apply/4/')
            except ValueError as e:
                messages.error(request, f"Invalid Credential!: {str(e)}")
                return redirect('/apply/4/')
            except ValidationError as e:
                messages.error(request, f"Invalid Credential!: {str(e)}")
                return redirect('/apply/4/')

            

def ApplyFive(request):
    if request.user.is_authenticated:
        user = request.user
        applicant = get_object_or_404(Application, applicant=user)
        current_session = Session.objects.filter(is_current=True).first()
        context = {}

        # Handle GET request to display existing data
        next_of_kin = NextOfKin.objects.filter(applicant=applicant, session=current_session).first()
        nok = ['parent', 'spouse', 'sibling', 'child', 'guardian', 'grandparent', 'uncle_aunt', 'cousin', 'friend', 'other']
        if request.method == 'GET':
            context = {
                'nok': nok,
                'next_of_kin': next_of_kin,
                'current_year': timezone.now().year,
            }
            return render(request, './application/applyfive.html', context)

        # Handle POST request to save or update data
        if request.method == 'POST':
            action = request.POST.get('action')
            if next_of_kin:
                # Update existing record
                next_of_kin.surname = request.POST.get('surname', '')
                next_of_kin.first_name = request.POST.get('first_name', '')
                next_of_kin.middle_name = request.POST.get('middle_name', '')
                next_of_kin.relationship = request.POST.get('relationship', '').lower()
                next_of_kin.address = request.POST.get('address', '')
                next_of_kin.phone_number = request.POST.get('phone_number', '')
                next_of_kin.alternate_phone_number = request.POST.get('alternate_phone_number', '')
                next_of_kin.email = request.POST.get('email', '')
                next_of_kin.occupation = request.POST.get('occupation', '')
                next_of_kin.work_address = request.POST.get('work_address', '')
                next_of_kin.session = current_session
            else:
                # Create new record
                next_of_kin = NextOfKin(
                    applicant=applicant,
                    session=current_session,
                    surname=request.POST.get('surname', ''),
                    first_name=request.POST.get('first_name', ''),
                    middle_name=request.POST.get('middle_name', ''),
                    relationship=request.POST.get('relationship', '').lower(),
                    address=request.POST.get('address', ''),
                    phone_number=request.POST.get('phone_number', ''),
                    alternate_phone_number=request.POST.get('alternate_phone_number', ''),
                    email=request.POST.get('email', ''),
                    occupation=request.POST.get('occupation', ''),
                    work_address=request.POST.get('work_address', ''),
                )

            try:
                next_of_kin.full_clean()
                next_of_kin.save()
                if action == 'save':
                    messages.success(request, "Next of kin information saved as draft.")
                    return redirect('/apply/5/')
                elif action == 'next':
                    messages.success(request, "Next of kin information saved. Proceeding to review.")
                    return redirect('/apply/6/')  # Adjust to your review URL
            except ValidationError as e:
                for field, errors in e.message_dict.items():
                    for error in errors:
                        messages.error(request, f"{field.replace('_', ' ').capitalize()}: {error}")

        return render(request, './application/applyfive.html', context)

def ApplySix(request):
    if request.user.is_authenticated:
        user = request.user
        applicant = get_object_or_404(Application, applicant=user)
        current_session = Session.objects.filter(is_current=True).first()
        context = {}

        # Handle GET request to display existing data
        # references = Reference.objects.filter(applicant=applicant, session=current_session).order_by('id')
        references = Reference.objects.filter(applicant=applicant, session=current_session)
        # if len(references) < 3:
        #     # Pad with unsaved Reference objects to ensure 3 forms
        #     additional_refs = [Reference(applicant=applicant, session=current_session) for _ in range(3 - len(references))]
        #     references.extend(additional_refs)
        context = {
            'references': references,
            'current_year': timezone.now().year,
        }
        if request.method == 'GET':
            return render(request, './application/applysix.html', context)

        # Handle POST request to save or update data
        if request.method == 'POST':
            action = request.POST.get('action')
            # Delete existing references if starting fresh (optional logic based on your needs)
            if action == 'save' and not messages.get_messages(request):
                messages.success(request, "References saved!")
                return redirect('/apply/6/')
            
                # Process submitted references
                
                name = request.POST.get(f'references[name]', '')
                position_rank = request.POST.get(f'references[position_rank]', '')
                address = request.POST.get(f'references[address]', '')
                phone_number = request.POST.get(f'references[phone_number]', '')
                email = request.POST.get(f'references[email]', '')
                relationship_type = request.POST.get(f'references[relationship_type]', '')
                institution_organization = request.POST.get(f'references[institution_organization]', '')
                years_known = request.POST.get(f'references[years_known]', '')

                if Reference.objects.filter(applicant=applicant, session=current_session, email=email).exists():
                    messages.success(request, "References already exists!")
                    return redirect('/apply/6/')
                else:
                    try:
                        reference = Reference.objects.create(applicant=applicant, session=current_session, name=name,
                                                        position_rank=position_rank, address=address,
                                                        phone_number=phone_number, email=email, relationship=relationship_type,
                                                        institution_organization=institution_organization, years_known=years_known)

                        reference.save()
                    except ValidationError as e:
                        messages.error(request, f"Invalid Request!")

            elif action == 'next' and not messages.get_messages(request):
                messages.success(request, "References saved. Proceeding to next step.")
                return redirect('/apply/7/')  # Adjust to your next URL
            # Adjust to your next URL

        context['references'] = references
        return render(request, './application/applysix.html', context)

def RefDelete(request, id):
    if request.user.is_authenticated:
        user = request.user
        cred = get_object_or_404(Reference, id=id)
        cred.delete()
        
        messages.success(request, "Credentials deleted!")
        return redirect('/apply/6/')


def RefUpdate(request):
    if request.user.is_authenticated:
        user = request.user

        if request.method == 'POST':
            ref_name = request.POST.get("ref_name", "")
            position = request.POST.get("position", "")
            relationship = request.POST.get("relationship", "")
            institution = request.POST.get("institution", "")
            years_known = request.POST.get("years_known", "")
            complete_address = request.POST.get("complete_address", "")
            phone_number = request.POST.get("phone_number", "")
            email_address = request.POST.get("email_address", "")
            ref_id = request.POST.get("ref_id", "")
            
            try:
                reference = get_object_or_404(Reference, id=ref_id)

                reference.name = ref_name
                reference.position_rank = position
                reference.address = complete_address
                reference.phone_number = phone_number
                reference.institution_organization = institution
                reference.email = email_address
                reference.relationship = relationship
                reference.years_known = years_known

                reference.save()
                messages.success(request, "Referee Updated!")
                return redirect('/apply/6/')
            except ValueError as e:
                messages.error(request, f"Invalid Information of Referee!: {str(e)}")
                return redirect('/apply/6/')
            except ValidationError as e:
                messages.error(request, f"Invalid Information of Referee!: {str(e)}")
                return redirect('/apply/6/')

from .models import Application, AdditionalInformation, Honor, Session
from django import forms

class HonorForm(forms.ModelForm):
    class Meta:
        model = Honor
        fields = ['title', 'organization', 'year', 'description']

class AdditionalInfoForm(forms.ModelForm):
    class Meta:
        model = AdditionalInformation
        fields = ['additional_info']

def ApplySeven(request):
    if request.user.is_authenticated:
        user = request.user
        applicant = get_object_or_404(Application, applicant=user)
        current_session = Session.objects.filter(is_current=True).first()
        context = {}

        # Handle GET request to display existing data
        additional_info, created = AdditionalInformation.objects.get_or_create(
            applicant=applicant,
            session=current_session,
            defaults={'additional_info': ''}
        )
        honors = Honor.objects.filter(additional_info=additional_info).order_by('id')
        context = {
            'additional_info': additional_info,
            'honors': honors,
            'current_year': timezone.now().year,
        }
        if request.method == 'GET':
            return render(request, './application/applyseven.html', context)

        # Handle POST request to save or update data
        if request.method == 'POST':
            action = request.POST.get('action')
            if action == 'save' and not messages.get_messages(request):
                title = request.POST.get(f'title', '').strip()
                organization = request.POST.get(f'organization', '').strip()
                year = request.POST.get(f'year', '').strip()
                description = request.POST.get(f'description', '').strip()
                additional_info_form = AdditionalInfoForm(request.POST, instance=additional_info)
                honor_form = HonorForm(request.POST)
                if additional_info_form.is_valid() and honor_form.is_valid():
                    honor = Honor.objects.create(additional_info=additional_info, title=title, organization=organization, year=year, description=description)
                    honor.save()

                    messages.success(request, "Additional information saved.")
                    return redirect('/apply/7/')
                
                # if additional_info_form.is_valid():
                #     additional_info = additional_info_form.save()
                    
                    # Process honors
                    # for i in range(3):  # Allow up to 3 honors
                    # title = request.POST.get(f'title', '').strip()
                    # organization = request.POST.get(f'organization', '').strip()
                    # year = request.POST.get(f'year', '').strip()
                    # description = request.POST.get(f'description', '').strip()

                    # Honor.objects.filter(additional_info=additional_info).delete()
                    # for data in honors_data:
                    #     honor_form = HonorForm(data)
                    #     if honor_form.is_valid():
                    #         honor_form.save()
                    #     else:
                    #         for field, errors in honor_form.errors.items():
                    #             messages.error(request, f"{field.replace('_', ' ').capitalize()} error: {errors[0]}")

                messages.success(request, "Invalid Submission!")
                return redirect('/apply/7/')
            elif action == 'next' and not messages.get_messages(request):
                messages.success(request, "Proceeding to upload document.")
                return redirect('/apply/8/')

        return render(request, './application/applyseven.html', context)

    return redirect('/')  # Redirect if not authenticated


def AwardDelete(request, id):
    if request.user.is_authenticated:
        user = request.user
        honor = get_object_or_404(Honor, id=id)
        honor.delete()
        
        messages.success(request, "Additional Info deleted!")
        return redirect('/apply/7/') 

class UploadedFileForm(forms.ModelForm):
    class Meta:
        model = UploadedFile
        fields = ['name', 'file', 'size', 'status']

class DocumentUploadView(forms.Form):
    file = forms.FileField()

def ApplyEight(request):
    if request.user.is_authenticated:
        user = request.user
        applicant = get_object_or_404(Application, applicant=user)
        current_session = Session.objects.filter(is_current=True).first()
        context = {}


        docs = UploadedFile.objects.filter(applicant=applicant, session=current_session)
        uploaded_docs = 0 if not docs.exists() else docs.count()
        total_required = 5
        missing_required = total_required - uploaded_docs

        if request.method == 'POST':
            title = request.POST.get('title', 'Untitled')  # Default to 'Untitled' if not provided

            
            
            action = request.POST.get('action')

            if action == 'save':
                if title.strip() == "":
                    messages.error(request, f"Add title to file!")
                    return redirect('/apply/8/')
            
                if request.FILES.get('file'):
                    file = request.FILES['file']
                    file_extension = file.name.split('.').pop().lower()
                    if file_extension not in ['pdf', 'jpg', 'png']:
                        messages.error(request, f"Invalid file type for {title}. Accepted formats: {', '.join(['pdf', 'jpg', 'png'])}")
                        return redirect('/apply/8/')

                    file_size_mb = file.size / (1024 * 1024)
                    if file_size_mb > 5:
                        messages.error(request, f"File too large for {title}. Maximum size: 5MB")
                        return redirect('/apply/8/')

                    if UploadedFile.objects.filter(applicant=applicant, session=current_session).count() >= 5:
                        messages.error(request, f"Maximum {7} files allowed for upload.")
                        return redirect('/apply/8/')

                    uploaded_file = UploadedFile(
                        applicant=applicant,
                        session=current_session,
                        title=title,
                        name=file.name,
                        file=file,
                        size=file.size,
                        status='completed'
                    )
                    uploaded_file.save()
                    messages.success(request, "Document saved successfully.")
                else:
                    messages.success(request, "No file attached. Please upload a document.")
                return redirect('/apply/8/')

            elif action == 'next':
                if not messages.get_messages(request):
                    if uploaded_docs >= total_required:
                        messages.success(request, "Documents saved. Proceeding to review.")
                        return redirect('/apply/review/')
                    else:
                        messages.error(request, f"Please upload all {total_required} required documents before proceeding. Uploaded: {uploaded_docs}")
                return redirect('/apply/8/')

        context = {
            'uploadedDocs': docs,
            'uploaded_docs': uploaded_docs,
            'total_required': total_required,
        }
        return render(request, './application/applyeight.html', context)

def DocDelete(request, id):
    if request.user.is_authenticated:
        user = request.user
        file = get_object_or_404(UploadedFile, id=id)
        file.delete()
        
        messages.success(request, "Uploaded file deleted!")
        return redirect('/apply/8/') 
    

@csrf_exempt
def delete_file(request, file_id):
    if request.method == 'POST':
        file = get_object_or_404(UploadedFile, id=file_id)
        if file.document_category.applicant.applicant == request.user:
            file.file.delete(save=False)  # Remove file from storage
            file.delete()
            return JsonResponse({'status': 'success'})
        return JsonResponse({'status': 'error', 'message': 'Unauthorized'}, status=403)
    return JsonResponse({'status': 'error', 'message': 'Invalid method'}, status=405)


@login_required
def application_review(request):
    if request.method == 'POST':
        # Simulate submission logic
        return HttpResponseRedirect(reverse('dashboard'))  # Replace with actual URL

    user = request.user
    applicant = Application.objects.get(applicant=user)

    context = {
        'user': user,
        'personal_info': {
            'programme': 'Master of Science (M.Sc.)',
            'area_of_specialization': 'Computer Science',
            'title': 'Mr.',
            'first_name': 'John',
            'middle_name': 'A.',
            'surname': 'Doe',
            'mailing_address': '123 University Road, Cityville, State, 12345',
            'mobile_phone': '+2348012345678',
            'email': 'john.doe@example.com',
            'date_of_birth': '1995-05-10',
            'place_of_birth': 'Lagos',
            'state_of_origin': 'Lagos',
            'nationality': 'Nigerian',
            'gender': 'M',
            'marital_status': 'single',
            'religious_affiliation': 'christian',
            'other_religion': '',
        },
        'educational_history': {
            'records': [
                {
                    'institution': 'University of Lagos',
                    'diploma_degree': 'Bachelor of Science (B.Sc.)',
                    'from_month': 'September',
                    'from_year': '2013',
                    'to_month': 'July',
                    'to_year': '2017',
                    'currently_enrolled': False,
                },
                {
                    'institution': 'Lagos State Polytechnic',
                    'diploma_degree': 'National Diploma (ND)',
                    'from_month': 'September',
                    'from_year': '2010',
                    'to_month': 'July',
                    'to_year': '2012',
                    'currently_enrolled': False,
                },
            ],
            'transcript_instructions': 'The Dean of Postgraduate Studies, Achievers University, Km 1, Idasen-Ute Road, Owo, Ondo State, Nigeria.',
        },
        'work_experience': {
            'has_no_experience': False,
            'records': [
                {
                    'position': 'Software Engineer',
                    'employer': 'Tech Solutions Ltd.',
                    'from_month': 'August',
                    'from_year': '2020',
                    'to_month': '',
                    'to_year': '',
                    'current_position': True,
                    'responsibilities': 'Developed and maintained web applications using React and Node.js...',
                },
                {
                    'position': 'Junior Developer',
                    'employer': 'Innovate Corp.',
                    'from_month': 'September',
                    'from_year': '2017',
                    'to_month': 'July',
                    'to_year': '2020',
                    'current_position': False,
                    'responsibilities': 'Assisted senior developers in building and testing software components...',
                },
            ],
        },
        'professional_credentials': {
            'has_no_credentials': False,
            'credentials': [
                {
                    'credential_name': 'Project Management Professional (PMP)',
                    'issuing_organization': 'Project Management Institute',
                    'issue_date': '2022-03-15',
                    'expiry_date': '2025-03-15',
                    'credential_number': 'PMP123456',
                    'file_name': 'PMP_Certificate.pdf',
                    'upload_status': 'success',
                },
                {
                    'credential_name': 'Certified ScrumMaster (CSM)',
                    'issuing_organization': 'Scrum Alliance',
                    'issue_date': '2021-08-01',
                    'expiry_date': '',
                    'credential_number': 'CSM789012',
                    'file_name': 'CSM_Certificate.pdf',
                    'upload_status': 'success',
                },
            ],
        },
        'next_of_kin': {
            'first_name': 'Jane',
            'middle_name': '',
            'surname': 'Smith',
            'relationship': 'spouse',
            'address': '456 Family Lane, Townsville, State, 67890',
            'phone_number': '+2349012345678',
            'alternate_phone_number': '',
            'email': 'jane.smith@example.com',
            'occupation': 'Doctor',
            'work_address': 'City Hospital, Main Street, Townsville',
        },
        'references': {
            'references': [
                {
                    'name': 'Prof. Adaobi Nnamdi',
                    'position_rank': 'Professor',
                    'address': 'Department of Computer Science, University of Lagos, Akoka, Lagos',
                    'phone_number': '+2348031234567',
                    'email': 'adaobi.nnamdi@unilag.edu.ng',
                    'is_undergraduate_teacher': True,
                    'relationship_type': 'Undergraduate Professor/Lecturer',
                    'institution_organization': 'University of Lagos',
                    'years_known': '4',
                },
                {
                    'name': 'Dr. Emeka Okoro',
                    'position_rank': 'Senior Manager',
                    'address': 'Tech Solutions Ltd., 789 Business Park, Cityville',
                    'phone_number': '+2347045678901',
                    'email': 'emeka.okoro@techsolutions.com',
                    'is_undergraduate_teacher': False,
                    'relationship_type': 'Employer/Manager',
                    'institution_organization': 'Tech Solutions Ltd.',
                    'years_known': '3',
                },
                {
                    'name': 'Mr. David Jones',
                    'position_rank': 'Lecturer',
                    'address': 'Department of Mathematics, University of Ibadan, Ibadan',
                    'phone_number': '+2348123456789',
                    'email': 'david.jones@ui.edu.ng',
                    'is_undergraduate_teacher': False,
                    'relationship_type': 'Academic Supervisor',
                    'institution_organization': 'University of Ibadan',
                    'years_known': '2',
                },
            ],
        },
        'additional_information': {
            'additional_info': 'My passion for artificial intelligence stems from my undergraduate research project on natural language processing...',
            'honors': [
                {
                    'title': "Dean's List",
                    'organization': 'University of Lagos',
                    'year': '2016',
                    'description': 'Recognized for outstanding academic performance (top 5% of class)',
                },
                {
                    'title': 'Best Final Year Project Award',
                    'organization': 'University of Lagos, Department of Computer Science',
                    'year': '2017',
                    'description': 'Awarded for innovative sentiment analysis model',
                },
            ],
        },
        'document_categories': [
            {
                'title': 'Academic Transcripts',
                'required': True,
                'files': [{'name': 'Unilag_Transcript.pdf', 'size': 1200000, 'status': 'completed', 'url': '/placeholder.svg'}],
            },
            {
                'title': 'Degree Certificates',
                'required': True,
                'files': [{'name': 'BSc_Certificate.pdf', 'size': 800000, 'status': 'completed', 'url': '/placeholder.svg'}],
            },
            {
                'title': 'Identification Document',
                'required': True,
                'files': [{'name': 'Passport_Bio_Page.jpg', 'size': 1500000, 'status': 'completed', 'url': '/placeholder.svg'}],
            },
            {
                'title': 'Passport Photograph',
                'required': True,
                'files': [{'name': 'Passport_Photo.png', 'size': 500000, 'status': 'completed', 'url': '/placeholder.svg'}],
            },
            {
                'title': 'Professional Certificates',
                'required': False,
                'files': [{'name': 'PMP_Cert.pdf', 'size': 2000000, 'status': 'completed', 'url': '/placeholder.svg'}],
            },
            {
                'title': 'Employment Documents',
                'required': False,
                'files': [{'name': 'Employment_Letter_TechSolutions.pdf', 'size': 1800000, 'status': 'completed', 'url': '/placeholder.svg'}],
            },
            {
                'title': 'Research & Publications',
                'required': False,
                'files': [{'name': 'Sentiment_Analysis_Thesis.pdf', 'size': 4500000, 'status': 'completed', 'url': '/placeholder.svg'}],
            },
            {
                'title': 'Supporting Documents',
                'required': False,
                'files': [{'name': 'Award_Certificate.jpg', 'size': 900000, 'status': 'completed', 'url': '/placeholder.svg'}],
            },
        ],
        'is_submitting': False,  # This would be dynamic in a real app
    }
    return render(request, 'application/applyreview.html', context)