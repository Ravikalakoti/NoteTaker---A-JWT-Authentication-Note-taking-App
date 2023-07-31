from django.contrib import admin
from.models import Note, Category, NoteSharingInvitation, UserRelationship

# Register your models here.
admin.site.register(Note)
admin.site.register(Category)
admin.site.register(NoteSharingInvitation)
admin.site.register(UserRelationship)

