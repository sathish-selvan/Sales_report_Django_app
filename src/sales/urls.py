from django.urls import path
from .views import home_view, SaleListView, SaleDetailView, UploadTemplateView, csv_upload

app_name = "sales"

urlpatterns = [
    path('', home_view, name="home"),
    path("sales/", SaleListView.as_view(), name="list"),
    path("upload/", UploadTemplateView.as_view(), name="upload"),
    path("from_file/", csv_upload, name="from-file"),
    path("sales/<pk>/", SaleDetailView.as_view(), name="detail"),
]
