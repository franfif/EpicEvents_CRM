from django.contrib import admin
from django.urls import path, include

import clients.views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api-auth/", include("rest_framework.urls")),
    path(
        "api/clients/",
        clients.views.ClientListCreateAPIView.as_view(),
        name="client-list",
    ),
    path(
        "api/clients/<int:id>/",
        clients.views.ClientDetailAPIView.as_view(),
        name="client-detail",
    ),
]
