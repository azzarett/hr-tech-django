from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),

    # Users API
    path("v1/users", include("modules.users.urls")),

    # Invitations API
    path("v1/", include("modules.invitations.urls")),

    # Teams API
    path("v1/teams", include("modules.teams.urls")),

]