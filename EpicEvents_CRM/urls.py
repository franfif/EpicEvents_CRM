from django.contrib import admin
from django.urls import path, include

from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

import clients.views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api-auth/", include("rest_framework.urls")),
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
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
