# fairs/view.py

from django.urls import reverse_lazy
from .forms import FairDetailForm

from django.views.generic import (
    ListView,
    DetailView,
    UpdateView,
)
from fairs.models import (
    Fair,
    Event,
)


# Create your views here.
class FairListView(ListView):
    """
    List all fairs in the system by created date
    """
    template_name = 'fairs/fair_list.html'
    queryset = Fair.objects.all().order_by("-date_created")


class FairDetailUpdateView(UpdateView):
    """
    Display an editable form of the details of a fair
    """
    model = Fair
    form_class = FairDetailForm
    template_name = 'fairs/fair_detail.html'
    # success_url = reverse_lazy('fair:fair-list')
    success_url = '/'

    def get_context_data(self, **kwargs):
        context = super(FairDetailUpdateView, self).get_context_data(**kwargs)
        # Refresh the object from the database in case the form validation changed it
        object = self.get_object()
        context['object'] = context['fair'] = object
        return context


class EventListView(ListView):
    """
    List all events in the system by created date
    """
    model = Event
    template_name = 'events/event_list.html'
    queryset = Event.objects.all().order_by("-date_created")


class EventDetailView(DetailView):
    """
    Display an editable form of the details of an event
    """
    model = Event
    template_name = 'events/event_detail.html'
