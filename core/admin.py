from django.contrib import admin
from .models import Profile, Room, Topic, Message
# Register your models here.

admin.site.register(Profile)
admin.site.register(Room)
admin.site.register(Topic)
admin.site.register(Message)