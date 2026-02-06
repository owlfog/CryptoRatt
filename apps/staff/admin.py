from django.contrib import admin
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import path, reverse
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from django.core.mail import send_mail, EmailMessage
from django.core.mail.backends.smtp import EmailBackend

from .models import EmailSettings


@admin.register(EmailSettings)
class EmailSettingsAdmin(admin.ModelAdmin):
    list_display = ['host', 'port', 'enabled', 'security', 'test_email_button']
    change_form_template = 'admin/staff/emailsettings/change_form.html'
    fieldsets = (
        (None, {
            'fields': ('enabled', 'backend')
        }),
        (_('SMTP Server'), {
            'fields': ('host', 'port', 'security', 'timeout')
        }),
        (_('Authentication'), {
            'fields': ('username', 'password'),
            'classes': ('collapse',),
        }),
        (_('Sender'), {
            'fields': ('from_email',)
        }),
    )
    
    def has_add_permission(self, request):
        # Only allow one instance
        try:
            return not EmailSettings.objects.exists()
        except Exception:
            return True
    
    def has_delete_permission(self, request, obj=None):
        return False
    
    def test_email_button(self, obj):
        url = reverse('admin:staff_emailsettings_test_email')
        return format_html(
            '<a class="button" href="{}">Test Email</a>',
            url
        )
    test_email_button.short_description = _('Test')
    test_email_button.allow_tags = True
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                'test-email/',
                self.admin_site.admin_view(self.test_email_view),
                name='staff_emailsettings_test_email',
            ),
        ]
        return custom_urls + urls
    
    def test_email_view(self, request):
        settings = EmailSettings.get_settings()
        
        if not settings.enabled:
            messages.error(request, _('Email is disabled. Enable it first.'))
            return redirect('admin:staff_emailsettings_changelist')
        
        try:
            # Create custom backend with current settings
            backend = EmailBackend(
                host=settings.host,
                port=settings.port,
                username=settings.username,
                password=settings.password,
                use_tls=settings.use_tls,
                use_ssl=settings.use_ssl,
                timeout=settings.timeout,
            )
            
            email = EmailMessage(
                subject='CryptoRatt - Test Email',
                body='This is a test email from CryptoRatt. If you received this, your SMTP settings are working correctly.',
                from_email=settings.from_email,
                to=[request.user.email or settings.from_email],
                connection=backend,
            )
            email.send(fail_silently=False)
            
            messages.success(
                request,
                _('Test email sent successfully to %(email)s') % {'email': request.user.email or settings.from_email}
            )
        except Exception as e:
            messages.error(request, _('Failed to send email: %(error)s') % {'error': str(e)})
        
        return redirect('admin:staff_emailsettings_changelist')
    
    def changelist_view(self, request, extra_context=None):
        # Redirect to change view if settings exist
        if EmailSettings.objects.exists():
            obj = EmailSettings.get_settings()
            return redirect('admin:staff_emailsettings_change', obj.pk)
        return super().changelist_view(request, extra_context)
