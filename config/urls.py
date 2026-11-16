
from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views

from leagues.views import (
    dashboard_page,
    clubs_page,
    teams_page,
    matchs_page,
    table_page,
    view_page,
    home_page
)

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    
    path("", home_page, name="home"),
        
    path("competitions", view_page, name="view"),

    path(
        "admin-login/",
        auth_views.LoginView.as_view(
            template_name="leagues/login.html"
        ),
        name="login"
    ),

    path(
        "admin-logout/",
        auth_views.LogoutView.as_view(),
        name="logout"
    ),

    path("view/", dashboard_page, name="dashboard"),
    path("clubs/", clubs_page, name="clubs"),
    path("teams/", teams_page, name="teams"),
    path("matchs/", matchs_page, name="matchs"),
    path("table/", table_page, name="table"),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )
