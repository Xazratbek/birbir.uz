from django.views.generic import TemplateView


class PaymentsPlaceholderView(TemplateView):
    template_name = "placeholders/payments.html"
