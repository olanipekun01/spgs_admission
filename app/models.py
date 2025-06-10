from django.db import models
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import AbstractUser
import uuid
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.timezone import now

# Create your models here.
class CustomUser(AbstractUser):
    USER_TYPE_CHOICES = (
        ('student', 'Student'),
        ('instructor', 'Instructor'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # date_joined = models.DateTimeField(auto_now_add=True)
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES)

    def __str__(self):
        return self.username
        
    def set_password(self, raw_password):
        """Hash and set the password."""
        self.password = make_password(raw_password)
        self.save()
        
    def check_password(self, raw_password):
        """Check the password against the stored hashed password."""
        return check_password(raw_password, self.password)
    
class Session(models.Model):
    year = models.CharField(max_length=500)  # e.g., '2023/2024'
    is_current = models.BooleanField(default=False)  # Marks current active session

    def save(self, *args, **kwargs):
        if self.is_current:
            # Uncheck `is_current` for all other Semester objects
            Session.objects.filter(is_current=True).exclude(id=self.id).update(is_current=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.year
    
    

class College(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(blank=True, null=True, max_length=500)

    def __str__(self):
        return self.name
    
class Department(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(blank=True, null=True, max_length=500)
    college = models.ForeignKey(College, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

class Programme(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(blank=True, null=True, max_length=500)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    duration = models.IntegerField(blank=True, null=True)
    degree = models.CharField(blank=True, null=True, max_length=50)

class Application(models.Model):
    applicant = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='application')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    has_paid = models.BooleanField(default=False)
    payment_reference = models.CharField(max_length=100, null=True, blank=True)
    current_step = models.CharField(max_length=50, default="start")
    status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('approved', 'Approved')], default='pending')
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

class PersonalDetails(models.Model):
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
    ]

    DENOMINATION_CHOICES = [
        ('christian', 'Christian'),
        ('muslim', 'Muslim'),
        ('traditional', 'Traditional'),
    ]

    PROGRAM_CHOICES = [
        ('electricalElectronicsEngineering', 'B.Eng. Electrical & Electronics Engineering'),
        ('computerEngineering', 'B.Eng. Computer Engineering'),
        ('mechatronicsEngineering', 'B.Eng. Mechatronics Engineering'),
        ('mechanicalEngineering', 'B.Eng. Mechanical Engineering'),
        ('biomedicalEngineering', 'B.Eng. Biomedical Engineering'),
        ('civilEnvironmentalEngineering', 'B.Eng. Civil and Environmental Engineering'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    applicant = models.OneToOneField(Application, on_delete=models.CASCADE, related_name='personal_details', default=None)
    first_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    place_of_birth = models.CharField(max_length=150, blank=True, null=True)
    state_of_origin = models.CharField(max_length=100, blank=True, null=True)
    nationality = models.CharField(max_length=100,blank=True, null=True)
    local_government_area = models.CharField(max_length=100, blank=True, null=True)
    denomination = models.CharField(max_length=15, choices=DENOMINATION_CHOICES, blank=True, null=True)
    address = models.TextField( blank=True, null=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True, null=True)
    desired_program = models.ForeignKey(Programme, on_delete=models.CASCADE, null=True, default=None)
    session = models.ForeignKey(Session, on_delete=models.CASCADE, null=True, default=None)

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.email}"


class PersonalInfo(models.Model):

    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
    ]

    DENOMINATION_CHOICES = [
        ('christian', 'Christian'),
        ('muslim', 'Muslim'),
        ('traditional', 'Traditional'),
    ]

    PROGRAM_CHOICES = [
        ('electricalElectronicsEngineering', 'B.Eng. Electrical & Electronics Engineering'),
        ('computerEngineering', 'B.Eng. Computer Engineering'),
        ('mechatronicsEngineering', 'B.Eng. Mechatronics Engineering'),
        ('mechanicalEngineering', 'B.Eng. Mechanical Engineering'),
        ('biomedicalEngineering', 'B.Eng. Biomedical Engineering'),
        ('civilEnvironmentalEngineering', 'B.Eng. Civil and Environmental Engineering'),
    ]


    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    applicant = models.OneToOneField(Application, on_delete=models.CASCADE, related_name='personal_details', default=None)
    title = models.CharField(max_length=100, blank=True, null=True)
    first_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100, blank=True, null=True)
    middle_name = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    place_of_birth = models.CharField(max_length=150, blank=True, null=True)
    state_of_origin = models.CharField(max_length=100, blank=True, null=True)
    nationality = models.CharField(max_length=100,blank=True, null=True)
    local_government_area = models.CharField(max_length=100, blank=True, null=True)
    religiousAffiliation = models.CharField(max_length=15, choices=DENOMINATION_CHOICES, blank=True, null=True)
    address = models.TextField( blank=True, null=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True, null=True)
    maritalStatus = models.CharField(max_length=100, choices=GENDER_CHOICES, blank=True, null=True)
    session = models.ForeignKey(Session, on_delete=models.CASCADE, null=True, default=None)

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.email}"

class NextOfKin(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    applicant = models.OneToOneField(Application, on_delete=models.CASCADE, related_name='personal_details', default=None)
    title = models.CharField(max_length=100, blank=True, null=True)
    first_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100, blank=True, null=True)
    middle_name = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    address = models.TextField( blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    session = models.ForeignKey(Session, on_delete=models.CASCADE, null=True, default=None)
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.applicant.applicant.username}"

class EducationHistory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    applicant = models.OneToOneField(Application, on_delete=models.CASCADE, related_name='personal_details', default=None)
    session = models.ForeignKey(Session, on_delete=models.CASCADE, null=True, default=None)
    institution = models.CharField(max_length=255)
    fromDate = models.DateField(blank=True, null=True)
    toDate = models.DateField(blank=True, null=True)
    degree = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.email}"

    # multiple entries allowed

class WorkExperience(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    applicant = models.OneToOneField(Application, on_delete=models.CASCADE, related_name='personal_details', default=None)
    session = models.ForeignKey(Session, on_delete=models.CASCADE, null=True, default=None)
    post = models.CharField(max_length=255)
    employer = models.CharField(max_length=255)
    date = models.DateField(blank=True, null=True)
    # ...

class AdditionalInformation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    applicant = models.OneToOneField(Application, on_delete=models.CASCADE, related_name='personal_details', default=None)
    session = models.ForeignKey(Session, on_delete=models.CASCADE, null=True, default=None)
    info = models.TextField(blank=True, null=True)

class OtherInformation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    applicant = models.OneToOneField(Application, on_delete=models.CASCADE, related_name='personal_details', default=None)
    session = models.ForeignKey(Session, on_delete=models.CASCADE, null=True, default=None)
    info = models.TextField(blank=True, null=True)

class StatementOfPurpose(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    applicant = models.OneToOneField(Application, on_delete=models.CASCADE, related_name='personal_details', default=None)
    session = models.ForeignKey(Session, on_delete=models.CASCADE, null=True, default=None)
    sop_file = models.FileField(upload_to='sop/')

class Referral(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    applicant = models.OneToOneField(Application, on_delete=models.CASCADE, related_name='personal_details', default=None)
    session = models.ForeignKey(Session, on_delete=models.CASCADE, null=True, default=None)
    application = models.ForeignKey(Application, on_delete=models.CASCADE)
    email = models.EmailField()
    token = models.UUIDField(default=uuid.uuid4, editable=False)
    submitted = models.BooleanField(default=False)
    recommendation_text = models.TextField(null=True, blank=True)
    recommendation = models.FileField(upload_to='recommendation/')