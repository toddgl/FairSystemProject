# faq/views.py

from django.urls import reverse_lazy
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.views.generic import (
    CreateView,
    ListView,
    UpdateView,
)

from faq.models import (
    FAQ,
)
from fairs.models import(
    InventoryItemFair
)
from .forms import(
    FaqCreateForm,
    FaqUpdateForm,
)


# Create your views here.
class FaqCreateView(PermissionRequiredMixin, CreateView):
    """
    Create a FAQ
    """
    permission_required = 'faq.add_faq'
    model = FAQ
    form_class = FaqCreateForm
    template_name = 'faq_create.html'
    success_url = reverse_lazy('faq:faq-list')


class FaqListView( ListView):
    """
    List all FAQ
    """
    model = FAQ
    template_name = 'faq_list.html'
    queryset = FAQ.objects.all().filter(is_active=True)

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        context["current_prices"] =  InventoryItemFair.currentinventoryitemfairmgr.all()
        return context



class FaqDetailUpdateView(PermissionRequiredMixin, UpdateView):
    """
    Display an editable form of Fair FAQ
    """
    permission_required = 'faq.change_faq'
    model = FAQ
    form_class = FaqUpdateForm
    template_name = 'faq_detail.html'
    success_url = reverse_lazy('faq:faq-list')


