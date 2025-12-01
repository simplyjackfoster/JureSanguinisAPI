from django.urls import path

from .views import EvaluateLineageView

urlpatterns = [
    path("evaluate/", EvaluateLineageView.as_view(), name="evaluate-lineage"),
]
