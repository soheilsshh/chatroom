from django.contrib import admin
from .models import Profile, Forum, Message

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at')
    search_fields = ('user__username', 'bio')
    list_filter = ('created_at',)

@admin.register(Forum)
class ForumAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_by', 'is_private', 'created_at')
    search_fields = ('name', 'description')
    list_filter = ('is_private', 'created_at')
    filter_horizontal = ('members',)

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'forum', 'is_private', 'created_at')
    search_fields = ('content', 'sender__username')
    list_filter = ('is_private', 'created_at', 'forum')
    readonly_fields = ('created_at', 'updated_at')
