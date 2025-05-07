from django.contrib import admin

# Register your models here.
from .models import Events, AuthGroup, Comments, PostFeatures, UserFeatures  # Import your models

# Register your models here
admin.site.register(Events)
admin.site.register(AuthGroup)
admin.site.register(Comments)
admin.site.register(PostFeatures)
admin.site.register(UserFeatures)