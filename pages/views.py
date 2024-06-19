# pages/views.py

from django.views.generic import TemplateView


# Create your views here.
# class HomePageView(TemplateView):
#    template_name = 'home.html'

class NoticePageView(TemplateView):
    template_name = 'notice.html'

class FaqPageView(TemplateView):
    template_name = 'faq.html'
