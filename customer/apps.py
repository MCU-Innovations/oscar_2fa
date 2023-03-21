from django.contrib.auth.decorators import login_required
from django.urls import path
import oscar.apps.customer.apps as apps
from oscar.core.loading import get_class


class CustomerConfig(apps.CustomerConfig):
    name = "oscar_2fa.customer"

    def ready(self):
        super().ready()
        self.security_view = get_class("customer.views", "SecurityView")
        self.security_backup_token_view = get_class(
            "customer.views", "SecurityBackupTokenView"
        )
        self.security_disable_view = get_class("customer.views", "SecurityDisableView")
        self.security_setup_view = get_class("customer.views", "SecuritySetupView")
        self.security_setup_complete_view = get_class(
            "customer.views", "SecuritySetupCompleteView"
        )
        self.security_qr = get_class("customer.views", "SecurityQR")

    def get_urls(self):
        urls = super().get_urls()
        urls += [
            path(
                "security/",
                login_required(self.security_view.as_view()),
                name="security-view",
            ),
            path(
                "security/backup_tokens/",
                login_required(self.security_backup_token_view.as_view()),
                name="security-backup-tokens",
            ),
            path(
                "security/disable/",
                login_required(self.security_disable_view.as_view()),
                name="security-disable",
            ),
            path(
                "security/setup/",
                login_required(self.security_setup_view.as_view()),
                name="security-setup",
            ),
            path(
                "security/qr/",
                login_required(self.security_qr.as_view()),
                name="security-qr",
            ),
            path(
                "security/complete/",
                login_required(self.security_setup_complete_view.as_view()),
                name="security-setup-complete-view",
            ),
        ]
        return urls
