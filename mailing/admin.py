from django.contrib import admin
from .models import Client, Mailing, Message, Attempt


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email', 'comment')
    search_fields = ('full_name', 'email')


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('subject', 'body')
    search_fields = ('subject',)


@admin.register(Mailing)
class MailingAdmin(admin.ModelAdmin):
    list_display = ('title', 'start_time', 'periodicity', 'status', 'message')
    list_filter = ('status', 'periodicity')
    search_fields = ('title', 'message__subject')


@admin.register(Attempt)
class AttemptAdmin(admin.ModelAdmin):
    list_display = ('mailing', 'sent_at', 'status', 'server_response')
    list_filter = ('status', 'mailing')
    search_fields = ('mailing__title', 'server_response')
    readonly_fields = ('mailing', 'sent_at', 'status', 'server_response')
