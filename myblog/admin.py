from django.contrib import admin
from .models import signupModel
from .models import profileModel
from .models import postcreateModel

# Register your models here.
admin.site.register(signupModel)
admin.site.register(profileModel)
admin.site.register(postcreateModel)
