from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(Application)
admin.site.register(Payment)
admin.site.register(Instructor)
admin.site.register(PersonalInfo)
admin.site.register(EducationalRecord)
admin.site.register(TranscriptInstructions)

admin.site.register(ApplicationWorkExperience)
admin.site.register(WorkExperienceRecord)

admin.site.register(ProfessionalCredential)

admin.site.register(NextOfKin)
admin.site.register(Reference)

admin.site.register(AdditionalInformation)
admin.site.register(Honor)


# admin.site.register(NextOfKin)
# admin.site.register(EducationHistory)
# admin.site.register(WorkExperience)
# admin.site.register(AdditionalInformation)
# admin.site.register(OtherInformation)
# admin.site.register(StatementOfPurpose)
# admin.site.register(Referral)
# admin.site.register(PersonalInfo)