from django.db import models
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import AbstractUser
import uuid
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.timezone import now
from common.models import *
from django.core.exceptions import ValidationError
from datetime import datetime
from django.utils import timezone
import re
from django.core.validators import RegexValidator
from django.db import models
from django.contrib.auth.models import User
from django.core.serializers.json import DjangoJSONEncoder
import json
from django.core.validators import FileExtensionValidator


class Application(models.Model):
    applicant = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='application')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    has_paid = models.BooleanField(default=False)
    payment_reference = models.CharField(max_length=100, null=True, blank=True)
    current_step = models.CharField(max_length=50, default="start")
    status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('approved', 'Approved')], default='pending')
    programme = models.CharField(max_length=100, blank=True, null=True,)
    area_of_specialization = models.CharField(max_length=100, blank=True, null=True,)
    department = models.CharField(max_length=100, blank=True, null=True,)
    college = models.CharField(max_length=100, blank=True, null=True,)
    session = models.ForeignKey(Session, on_delete=models.CASCADE, null=True, default=None)
    
    def __str__(self):
        return f"Application - {self.applicant.username}"

class Payment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    applicant = models.OneToOneField(Application, on_delete=models.CASCADE, related_name='payment', default=None)
    session = models.ForeignKey(Session, on_delete=models.CASCADE, null=True, default=None)
    hasPayed = models.BooleanField(blank=True, null=True, default=False)
    transRef = models.CharField(blank=True, null=True, max_length=500)
    payRef = models.CharField(blank=True, null=True, max_length=500)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.applicant.applicant.username

class Instructor(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, primary_key=True)
    position = models.CharField(blank=True, null=True, max_length=500)
    departmental_email = models.CharField(blank=True, null=True, max_length=90)

    def __str__(self):
        return self.position

class PersonalInfo(models.Model):
    # PROGRAMME_CHOICES = [
    #     ('MSC', 'Master of Science (M.Sc.)'),
    #     ('MA', 'Master of Arts (M.A.)'),
    #     ('MBA', 'Master of Business Administration (MBA)'),
    #     ('MENG', 'Master of Engineering (M.Eng.)'),
    #     ('PHD', 'Doctor of Philosophy (Ph.D.)'),
    #     ('PROF_DOC', 'Professional Doctorate'),
    # ]

    TITLE_CHOICES = [
        ('Dr.', 'Dr.'),
        ('Mr.', 'Mr.'),
        ('Mrs.', 'Mrs.'),
        ('Ms.', 'Ms.'),
    ]

    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
    ]

    MARITAL_STATUS_CHOICES = [
        ('single', 'Single'),
        ('married', 'Married'),
        ('widowed', 'Widowed'),
        ('divorced', 'Divorced'),
    ]

    RELIGIOUS_AFFILIATION_CHOICES = [
        ('christian', 'Christian'),
        ('islam', 'Islam'),
        ('others', 'Others'),
    ]

    STATE_OF_ORIGIN_CHOICES = [
        ('Abia', 'Abia'),
        ('Adamawa', 'Adamawa'),
        ('Akwa Ibom', 'Akwa Ibom'),
        ('Anambra', 'Anambra'),
        ('Bauchi', 'Bauchi'),
        ('Bayelsa', 'Bayelsa'),
        ('Benue', 'Benue'),
        ('Borno', 'Borno'),
        ('Cross River', 'Cross River'),
        ('Delta', 'Delta'),
        ('Ebonyi', 'Ebonyi'),
        ('Edo', 'Edo'),
        ('Ekiti', 'Ekiti'),
        ('Enugu', 'Enugu'),
        ('FCT', 'FCT'),
        ('Gombe', 'Gombe'),
        ('Imo', 'Imo'),
        ('Jigawa', 'Jigawa'),
        ('Kaduna', 'Kaduna'),
        ('Kano', 'Kano'),
        ('Katsina', 'Katsina'),
        ('Kebbi', 'Kebbi'),
        ('Kogi', 'Kogi'),
        ('Kwara', 'Kwara'),
        ('Lagos', 'Lagos'),
        ('Nasarawa', 'Nasarawa'),
        ('Niger', 'Niger'),
        ('Ogun', 'Ogun'),
        ('Ondo', 'Ondo'),
        ('Osun', 'Osun'),
        ('Oyo', 'Oyo'),
        ('Plateau', 'Plateau'),
        ('Rivers', 'Rivers'),
        ('Sokoto', 'Sokoto'),
        ('Taraba', 'Taraba'),
        ('Yobe', 'Yobe'),
        ('Zamfara', 'Zamfara'),
    ]

    applicant = models.OneToOneField(Application, on_delete=models.CASCADE, related_name='personalinfo', default=None)
    title = models.CharField(max_length=5, choices=TITLE_CHOICES)
    surname = models.CharField(max_length=100)
    first_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True)
    mailing_address = models.TextField()
    mobile_phone = models.CharField(max_length=20)
    email = models.EmailField()
    date_of_birth = models.DateField()
    place_of_birth = models.CharField(max_length=100)
    state_of_origin = models.CharField(max_length=20, choices=STATE_OF_ORIGIN_CHOICES)
    nationality = models.CharField(max_length=100)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    marital_status = models.CharField(max_length=20, choices=MARITAL_STATUS_CHOICES)
    religious_affiliation = models.CharField(max_length=20, choices=RELIGIOUS_AFFILIATION_CHOICES)
    other_religion = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    session = models.ForeignKey(Session, on_delete=models.CASCADE, null=True, default=None)

    def __str__(self):
        return f"{self.title} {self.first_name} {self.surname}"

    class Meta:
        verbose_name = "Personal Information"
        verbose_name_plural = "Personal Information"

class EducationalRecord(models.Model):
    applicant = models.ForeignKey(Application, on_delete=models.CASCADE, related_name='educational_records')
    session = models.ForeignKey(Session, on_delete=models.CASCADE, null=True)
    institution = models.CharField(max_length=200)
    diploma_degree = models.CharField(max_length=100)
    from_month = models.CharField(max_length=20)
    from_year = models.CharField(max_length=4)
    to_month = models.CharField(max_length=20, blank=True)
    to_year = models.CharField(max_length=4, blank=True)
    currently_enrolled = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.institution} - {self.diploma_degree}"

    class Meta:
        verbose_name = "Educational Record"
        verbose_name_plural = "Educational Records"

class TranscriptInstructions(models.Model):
    applicant = models.ForeignKey(Application, on_delete=models.CASCADE, related_name='transcript_instructions')
    session = models.ForeignKey(Session, on_delete=models.CASCADE, null=True)
    instructions = models.TextField(default="The Dean of Postgraduate Studies, Achievers University, Km 1, Idasen-Ute Road, Owo, Ondo State, Nigeria.")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Transcript Instructions for {self.applicant}"

    class Meta:
        verbose_name = "Transcript Instruction"
        verbose_name_plural = "Transcript Instructions"

class WorkExperienceRecord(models.Model):
    applicant = models.ForeignKey(Application, on_delete=models.CASCADE, related_name='work_experience_records')
    session = models.ForeignKey(Session, on_delete=models.CASCADE, null=True)
    position = models.CharField(max_length=200)
    employer = models.CharField(max_length=200)
    from_month = models.CharField(max_length=20)
    from_year = models.CharField(max_length=4)
    to_month = models.CharField(max_length=20, blank=True)
    to_year = models.CharField(max_length=4, blank=True)
    current_position = models.BooleanField(default=False)
    responsibilities = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.position} at {self.employer}"

    class Meta:
        verbose_name = "Work Experience Record"
        verbose_name_plural = "Work Experience Records"

    def get_end_date_display(self):
        return f"{self.to_month} {self.to_year}" if not self.current_position else "Present"

class ApplicationWorkExperience(models.Model):
    applicant = models.OneToOneField(Application, on_delete=models.CASCADE, related_name='work_experience')
    session = models.ForeignKey(Session, on_delete=models.CASCADE, null=True)
    has_no_experience = models.BooleanField(default=False)
    has_no_credentials = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Work Experience for {self.applicant}"


from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import ApplicationWorkExperience

class ProfessionalCredential(models.Model):
    application_work_experience = models.ForeignKey(ApplicationWorkExperience, on_delete=models.CASCADE, blank=True, null=True, related_name='credentials')
    session = models.ForeignKey(Session, on_delete=models.CASCADE, null=True)
    credential_name = models.CharField(max_length=255, blank=False)
    issuing_organization = models.CharField(max_length=255, blank=False)
    issue_date = models.DateField(blank=False)
    expiry_date = models.DateField(null=True, blank=True)
    credential_number = models.CharField(max_length=100, blank=True)

    class Meta:
        verbose_name = "Professional Credential"
        verbose_name_plural = "Professional Credentials"
        ordering = ['-issue_date']

    def __str__(self):
        return f"{self.credential_name} - {self.issuing_organization}"

    def clean(self):
        if self.expiry_date and self.issue_date and self.expiry_date <= self.issue_date:
            raise ValidationError("Expiry date must be after issue date.")
        if self.issue_date and self.issue_date > timezone.now().date():
            raise ValidationError("Issue date cannot be in the future.")



class NextOfKin(models.Model):
    RELATIONSHIP_CHOICES = [ 
        ('parent', 'Parent'),
        ('spouse', 'Spouse'),
        ('sibling', 'Sibling'),
        ('child', 'Child'),
        ('guardian', 'Guardian'),
        ('grandparent', 'Grandparent'),
        ('uncle_aunt', 'Uncle/Aunt'),
        ('cousin', 'Cousin'),
        ('friend', 'Friend'),
        ('other', 'Other'),
    ]
    applicant = models.ForeignKey(Application, on_delete=models.CASCADE, related_name='next_of_kin')
    session = models.ForeignKey(Session, on_delete=models.CASCADE, null=True)
    surname = models.CharField(max_length=100, blank=False)
    first_name = models.CharField(max_length=100, blank=False)
    middle_name = models.CharField(max_length=100, blank=True, null=True)
    relationship = models.CharField(max_length=50, blank=False, choices=RELATIONSHIP_CHOICES)
    address = models.TextField(blank=False)
    phone_number = models.CharField(max_length=20, blank=False)
    alternate_phone_number = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    occupation = models.CharField(max_length=100, blank=True, null=True)
    work_address = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "Next of Kin"
        verbose_name_plural = "Next of Kin"
        ordering = ['-id']

    def __str__(self):
        return f"{self.first_name} {self.surname} - {self.relationship}"

    def clean(self):
        if not self.surname.strip() or len(self.surname.strip()) < 2:
            raise ValidationError("Surname must be at least 2 characters.")
        if not self.first_name.strip() or len(self.first_name.strip()) < 2:
            raise ValidationError("First name must be at least 2 characters.")
        if not self.relationship:
            raise ValidationError("Relationship is required.")
        if not self.address.strip() or len(self.address.strip()) < 10:
            raise ValidationError("Please provide a complete address.")
        if not self.phone_number.strip():
            raise ValidationError("Phone number is required.")
        else:
            phone_regex = r'^[0-9+\-\s()]+$'
            if not re.match(phone_regex, self.phone_number):
                raise ValidationError("Please enter a valid phone number.")
        if self.email and not re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', self.email):
            raise ValidationError("Please enter a valid email address.")
        if self.alternate_phone_number and not re.match(phone_regex, self.alternate_phone_number):
            raise ValidationError("Please enter a valid alternate phone number.")

class Reference(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    applicant = models.ForeignKey(Application, on_delete=models.CASCADE, related_name='references')
    session = models.ForeignKey(Session, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=200, blank=False)
    position_rank = models.CharField(max_length=100, blank=False)
    address = models.TextField(blank=False)
    phone_number = models.CharField(max_length=20, blank=False)
    email = models.EmailField(blank=False)
    relationship = models.CharField(max_length=100, blank=False, default="")
    institution_organization = models.CharField(max_length=200, blank=False)
    years_known = models.PositiveSmallIntegerField(blank=False)

    class Meta:
        verbose_name = "Reference"
        verbose_name_plural = "References"
        ordering = ['-id']

    def __str__(self):
        return f"{self.name} - {self.relationship}"

    def clean(self):
        if not self.name.strip() or len(self.name.strip()) < 3:
            raise ValidationError("Name must be at least 3 characters.")
        if not self.position_rank.strip():
            raise ValidationError("Position/Rank is required.")
        if not self.address.strip() or len(self.address.strip()) < 10:
            raise ValidationError("Please provide a complete address.")
        if not self.phone_number.strip():
            raise ValidationError("Phone number is required.")
        else:
            phone_regex = r'^[0-9+\-\s()]+$'
            if not re.match(phone_regex, self.phone_number):
                raise ValidationError("Please enter a valid phone number.")
        if not self.email.strip() or not re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', self.email):
            raise ValidationError("Please enter a valid email address.")
        if not self.institution_organization.strip():
            raise ValidationError("Institution/Organization is required.")
        if not self.years_known or self.years_known < 1 or self.years_known > 50:
            raise ValidationError("Please enter a valid number of years (1-50).")

class AdditionalInformation(models.Model):
    applicant = models.ForeignKey(Application, on_delete=models.CASCADE, related_name='additional_info')
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    additional_info = models.TextField(
        max_length=2000,
        blank=True,
        help_text="Additional information relevant to the application (max 2000 characters)"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Additional Info for {self.applicant.applicant.username}"

class Honor(models.Model):
    additional_info = models.ForeignKey(AdditionalInformation, on_delete=models.CASCADE, related_name='honors')
    title = models.CharField(max_length=255, help_text="Title or name of the honor/award")
    organization = models.CharField(max_length=255, help_text="Organization or institution granting the award")
    year = models.CharField(
        max_length=4,
        help_text="Year received (e.g., 2023)",
        validators=[RegexValidator(r'^\d{4}$', message='Please enter a valid 4-digit year')]
    )
    description = models.TextField(blank=True, help_text="Brief description or criteria (optional)")

    def __str__(self):
        return f"{self.title} - {self.organization} ({self.year})"

class DocumentCategory(models.Model):
    applicant = models.ForeignKey(Application, on_delete=models.CASCADE, related_name='document_categories')
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField()
    required = models.BooleanField(default=False)
    accepted_formats = models.CharField(
        max_length=100,  # Sufficient for a list like "PDF,JPG,PNG"
        default="PDF,JPG,PNG",
        help_text="Comma-separated list of accepted file formats (e.g., PDF,JPG,PNG)"
    )
    max_size_mb = models.PositiveIntegerField(default=5, help_text="Maximum file size in MB")
    max_files = models.PositiveIntegerField(default=1, help_text="Maximum number of files allowed")

    def get_accepted_formats(self):
        """Split the comma-separated string into a list."""
        return [f.strip() for f in self.accepted_formats.split(',') if f.strip()]

    def set_accepted_formats(self, value):
        """Join the list into a comma-separated string."""
        self.accepted_formats = ','.join(value) if value else ''

    def __str__(self):
        return self.title

class UploadedFile(models.Model):
    applicant = models.ForeignKey(Application, on_delete=models.CASCADE, related_name='uploaded_files', default=1)
    session = models.ForeignKey(Session, on_delete=models.CASCADE, default=1)
    title = models.CharField(max_length=255, default="text")
    # document_category = models.ForeignKey(DocumentCategory, on_delete=models.CASCADE, related_name='files')
    name = models.CharField(max_length=255)
    file = models.FileField(upload_to='uploads/%Y/%m/%d/')
    size = models.PositiveIntegerField(help_text="Size in bytes")
    upload_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20,
        choices=[('completed', 'Completed'), ('error', 'Error')],
        default='completed'
    )

    def __str__(self):
        return self.name