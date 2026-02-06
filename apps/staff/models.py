from django.db import models
from django.utils.translation import gettext_lazy as _


class EmailSettings(models.Model):
    """Singleton model for SMTP settings"""
    
    EMAIL_BACKENDS = [
        ('django.core.mail.backends.smtp.EmailBackend', 'SMTP'),
        ('django.core.mail.backends.console.EmailBackend', 'Console (debug)'),
    ]
    
    TLS_CHOICES = [
        ('none', _('None')),
        ('tls', _('TLS')),
        ('ssl', _('SSL')),
    ]
    
    enabled = models.BooleanField(_('Enable email'), default=False)
    backend = models.CharField(
        _('Email backend'),
        max_length=100,
        choices=EMAIL_BACKENDS,
        default='django.core.mail.backends.smtp.EmailBackend'
    )
    host = models.CharField(_('SMTP Host'), max_length=255, default='localhost')
    port = models.PositiveIntegerField(_('SMTP Port'), default=587)
    username = models.CharField(_('Username'), max_length=255, blank=True)
    password = models.CharField(_('Password'), max_length=255, blank=True)
    security = models.CharField(
        _('Security'),
        max_length=10,
        choices=TLS_CHOICES,
        default='tls'
    )
    from_email = models.EmailField(_('From email'), default='noreply@example.com')
    timeout = models.PositiveIntegerField(_('Timeout (seconds)'), default=30)
    
    class Meta:
        verbose_name = _('Email Settings')
        verbose_name_plural = _('Email Settings')
    
    def __str__(self):
        return f"Email Settings ({self.host}:{self.port})"
    
    def save(self, *args, **kwargs):
        # Ensure only one instance exists (singleton)
        self.pk = 1
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs):
        pass  # Prevent deletion
    
    @classmethod
    def get_settings(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj
    
    @property
    def use_tls(self):
        return self.security == 'tls'
    
    @property
    def use_ssl(self):
        return self.security == 'ssl'
