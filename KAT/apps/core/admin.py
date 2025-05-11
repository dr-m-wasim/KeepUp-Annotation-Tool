from django.contrib import admin

# Register your models here.
from .models import Events, Comments, PostFeatures, UserFeatures

# Register your models here
admin.site.register(Events)
admin.site.register(Comments)
admin.site.register(PostFeatures)
admin.site.register(UserFeatures)