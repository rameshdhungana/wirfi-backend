from django.urls import path
from wirfi_app.views import IndustryTypeDetailView, IndustryTypeListView, LocationTypeDetailView, LocationTypeListView


urlpatterns = [
    path('industry-type/', IndustryTypeListView.as_view(), name="industry-type"),
    path('industry-type/<int:id>/', IndustryTypeDetailView.as_view(), name="industry-type-detail"),

    path('location-type/', LocationTypeListView.as_view(), name="location-type"),
    path('location-type/<int:id>/', LocationTypeDetailView.as_view(), name="location-type-detail")
]
