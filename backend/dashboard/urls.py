from django.urls import path
from .views import (
    DashboardListCreateView,
    DashboardRetrieveUpdateDestroyView,
    BlockListCreateView,
    BlockRetrieveUpdateDestroyView,
    FileUploadView,
    CodeExecutionView,
    CodeGenerateView
)

urlpatterns = [
    path('', DashboardListCreateView.as_view(), name='dashboard-list-create'),
    path('<int:pk>/', DashboardRetrieveUpdateDestroyView.as_view(), name='dashboard-detail'),
    path('<int:dashboard_id>/blocks/', BlockListCreateView.as_view(), name='block-list-create'),
    path('blocks/<int:pk>/', BlockRetrieveUpdateDestroyView.as_view(), name='block-detail'),
    path('<int:dashboard_id>/upload/', FileUploadView.as_view(), name='file-upload'),
    path('blocks/<int:block_id>/run/', CodeExecutionView.as_view(), name='block-run'),
    path('blocks/<int:block_id>/generate_code/', CodeGenerateView.as_view(), name='block-generate-code'),


]
