from django.urls import path
from wirfi_app.views import PresetFilterView, PresetFilterDeleteView


urlpatterns = [
    path('preset-filter/', PresetFilterView.as_view()),
    path('preset-filter/<int:id>/', PresetFilterDeleteView.as_view())
]