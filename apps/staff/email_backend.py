import logging
from django.core.mail.backends.smtp import EmailBackend as SMTPBackend
from django.core.mail.backends.console import EmailBackend as ConsoleBackend

logger = logging.getLogger(__name__)


class DatabaseEmailBackend(SMTPBackend):
    """
    Email backend that loads settings from database.
    Falls back to console backend if email is disabled.
    """
    
    def __init__(self, **kwargs):
        # Import here to avoid circular imports
        from .models import EmailSettings
        
        try:
            settings = EmailSettings.get_settings()
            
            if not settings.enabled:
                # Use console backend if disabled
                self._use_console = True
                super().__init__(**kwargs)
                return
            
            self._use_console = False
            
            # Override with database settings
            kwargs['host'] = settings.host
            kwargs['port'] = settings.port
            kwargs['username'] = settings.username
            kwargs['password'] = settings.password
            kwargs['use_tls'] = settings.use_tls
            kwargs['use_ssl'] = settings.use_ssl
            kwargs['timeout'] = settings.timeout
            
        except Exception:
            # If database not ready, use defaults
            self._use_console = True
        
        super().__init__(**kwargs)
    
    def send_messages(self, email_messages):
        logger.info(f"DatabaseEmailBackend.send_messages called with {len(email_messages)} messages")
        logger.info(f"_use_console = {getattr(self, '_use_console', False)}")
        
        if getattr(self, '_use_console', False):
            # Print to console instead
            logger.info("Using console backend (email disabled)")
            backend = ConsoleBackend()
            return backend.send_messages(email_messages)
        
        # Override from_email with database setting
        from .models import EmailSettings
        try:
            settings = EmailSettings.get_settings()
            for message in email_messages:
                logger.info(f"Sending email to: {message.to}, subject: {message.subject}")
                if message.from_email == 'noreply@example.com' or not message.from_email:
                    message.from_email = settings.from_email
        except Exception as e:
            logger.error(f"Error getting email settings: {e}")
        
        try:
            result = super().send_messages(email_messages)
            logger.info(f"Email sent successfully, result: {result}")
            return result
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            raise


def get_from_email():
    """Get FROM email from database settings"""
    from .models import EmailSettings
    try:
        settings = EmailSettings.get_settings()
        return settings.from_email
    except Exception:
        return 'noreply@example.com'
