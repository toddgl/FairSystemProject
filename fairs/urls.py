# fairs/urls.py


from django.urls import path

from fairs.views import (
    FairListView,
    FairCreateView,
    FairDetailUpdateView,
    EventCreateView,
    EventListView,
    EventDetailUpdateView,
)

app_name = 'fair' # This is the namespace so you can reverse urls with fair:*

urlpatterns = [

    path('fair/', FairListView.as_view(), name='fair-list'),
    path('fair/<int:pk>', FairDetailUpdateView.as_view(), name='fair-detail'),
    path('event/', EventListView.as_view(), name='event-list'),
    path('event/<int:pk>', EventDetailUpdateView.as_view(), name='event-detail'),
    path('fair/actionUrl/', FairCreateView.as_view(), name='actionUrl'),
    path('event/actionUrl/', EventCreateView.as_view(), name='actionUrl'),
]
