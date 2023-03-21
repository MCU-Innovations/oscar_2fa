import qrcode
from django.utils.translation import gettext_lazy as _
from oscar.core.loading import get_classes
from django.shortcuts import redirect
from django.conf import settings
from django.contrib import messages
from django.http import HttpResponse
from django.utils.module_loading import import_string
import two_factor.views
from two_factor.utils import get_otpauth_url, totp_digits

PageTitleMixin, RegisterUserMixin = get_classes(
    "customer.mixins", ["PageTitleMixin", "RegisterUserMixin"]
)

EmailUserCreationForm = get_classes("customer.forms", ["EmailUserCreationForm"])[0]


class SecurityView(PageTitleMixin, two_factor.views.ProfileView):
    template_name = "oscar/customer/security/security.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = _("Account Security")
        context["active_tab"] = "security"
        return context


class SecurityDisableView(PageTitleMixin, two_factor.views.DisableView):
    template_name = "oscar/customer/security/security_disable.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = _("Disable Two-factor Authentication")
        context["active_tab"] = "security"
        return context


class SecuritySetupView(PageTitleMixin, two_factor.views.SetupView):
    template_name = "oscar/customer/security/security_setup.html"
    success_url = "customer:security-setup-complete-view"
    qrcode_url = "customer:security-qr"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = _("Enable Two-Factor Authentication")
        context["active_tab"] = "security"
        return context


class SecuritySetupCompleteView(PageTitleMixin, two_factor.views.SetupCompleteView):
    template_name = "oscar/customer/security/security_setup_complete.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = _("Enable Two-Factor Authentication")
        context["active_tab"] = "security"
        return context


class SecurityBackupTokenView(PageTitleMixin, two_factor.views.BackupTokensView):
    template_name = "oscar/customer/security/security_backup_tokens.html"
    success_url = "customer:security-backup-tokens"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = _("Backup Tokens")
        context["active_tab"] = "security"
        return context


class SecurityQR(two_factor.views.QRGeneratorView):
    def get_username(self):
        return self.request.user.email


class AccountAuthView(RegisterUserMixin, two_factor.views.LoginView):
    template_name = "oscar/customer/login_registration.html"
    redirect_field_name = "next"
    login_prefix, registration_prefix = "login", "registration"
    registration_form_class = EmailUserCreationForm

    def post(self, request, *args, **kwargs):
        if "registration_submit" in request.POST:
            return self.validate_registration_form()
        return super().post(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect(settings.LOGIN_REDIRECT_URL)
        return super().get(request, *args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        ctx = super().get_context_data(*args, **kwargs)
        if "registration_form" not in kwargs:
            ctx["registration_form"] = self.get_registration_form()
        else:
            print(kwargs)
        return ctx

    def get_registration_form(self, bind_data=False):
        return self.registration_form_class(
            **self.get_registration_form_kwargs(bind_data)
        )

    def get_registration_form_kwargs(self, bind_data=False):
        kwargs = {}
        kwargs["host"] = self.request.get_host()
        kwargs["prefix"] = self.registration_prefix
        kwargs["initial"] = {
            "redirect_url": self.request.GET.get(self.redirect_field_name, ""),
        }
        if bind_data and self.request.method in ("POST", "PUT"):
            kwargs.update(
                {
                    "data": self.request.POST,
                    "files": self.request.FILES,
                }
            )
        return kwargs

    def validate_registration_form(self):
        form = self.get_registration_form(bind_data=True)
        if form.is_valid():
            self.register_user(form)

            msg = self.get_registration_success_message(form)
            messages.success(self.request, msg)

            return redirect(self.get_registration_success_url(form))

        ctx = self.get_context_data(self.get_form(), registration_form=form)
        return self.render_to_response(ctx)

    def get_registration_success_message(self, form):
        return _("Thanks for registering!")

    def get_registration_success_url(self, form):
        redirect_url = form.cleaned_data["redirect_url"]
        if redirect_url:
            return redirect_url

        return settings.LOGIN_REDIRECT_URL
