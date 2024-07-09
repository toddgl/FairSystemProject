# pages/views.py

from django.views.generic import TemplateView
from notices.models import(
    Notice
)


# Create your views here.
# class HomePageView(TemplateView):
#    template_name = 'home.html'

class NoticePageView(TemplateView):
    template_name = 'notice_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["notice_list"] = Notice.activenoticemgr.all()
        return context

class FaqPageView(TemplateView):
    template_name = 'faq.html'
