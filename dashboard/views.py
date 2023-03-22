from django.urls import reverse, reverse_lazy
import two_factor.views
import oscar.apps.dashboard.views
from two_factor.views.mixins import OTPRequiredMixin


class LoginView(two_factor.views.LoginView):
    template_name = "oscar/dashboard/login.html"


class IndexView(OTPRequiredMixin, oscar.apps.dashboard.views.IndexView):
    verification_url = "customer:security-denied"
