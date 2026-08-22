from django.apps import AppConfig

class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounts'

    def ready(self):
        import accounts.signals  # ✅ this ensures signals run

class SchoolAdminConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'school_admin'

    def ready(self):
        import school_admin.models  # 👈 this ensures signal registration
