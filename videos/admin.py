from django.contrib import admin
from .models import ContactMessage
from .models import Message

admin.site.register(ContactMessage)
admin.site.register(Message)

