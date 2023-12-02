import enum


class Messages(enum.Enum):
    EMAIL_ACTIVATED = 'Your email has been activated!'
    PHONE_ACTIVATED = 'Your phone number has been activated!'
    EMAIL_ACTIVATION_RESEND = 'Email activation resend!'
    PHONE_ACTIVATION_RESEND = 'phone activation resend!'
    EMAIL_SENT = 'Email sent!'
    PASSWORD_CHANGED = 'Password changed!'