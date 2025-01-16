from django.contrib import admin
from .models import Client, Mailing, Message, Attempt


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email', 'comment', 'owner')
    search_fields = ('full_name', 'email')
    list_filter = ('owner',)


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('subject', 'body', 'owner')
    search_fields = ('subject',)
    list_filter = ('owner',)


@admin.register(Mailing)
class MailingAdmin(admin.ModelAdmin):
    list_display = ('title', 'start_time', 'periodicity', 'status', 'message', 'owner')
    list_filter = ('status', 'periodicity', 'owner')
    search_fields = ('title', 'message__subject')


@admin.register(Attempt)
class AttemptAdmin(admin.ModelAdmin):
    list_display = ('mailing', 'sent_at', 'status', 'server_response')
    list_filter = ('status', 'mailing')
    search_fields = ('mailing__title', 'server_response')
    readonly_fields = ('mailing', 'sent_at', 'status', 'server_response')
