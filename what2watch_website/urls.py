"""what2watch_website URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.views.i18n import JavaScriptCatalog
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import views as auth_views

from what2watch.views import *

# Django admin pannel
urlpatterns = [
    path("admin/", admin.site.urls),
    path("", IndexView.as_view(), name="index"),
]

# Website views
urlpatterns += i18n_patterns(
    path("jsi18n/", JavaScriptCatalog.as_view(), name="javascript-catalog"),
    path(_("search/"), SearchView.as_view(), name="search"),
    path(_("search/query"), SearchQuery.as_view(), name="search_query"),
    path(_("search/") + "<str:s>", SearchView.as_view(), name="search_results"),
    path(_("shows/"), ShowsView.as_view(), name="shows"),
    path(_("shows/") + "<int:pk>", ShowDetailView.as_view(), name="shows_detail"),
    path(_("actors/"), ActorsView.as_view(), name="actors"),
    path(_("actors/") + "<int:pk>", ActorDetailView.as_view(), name="actors_detail"),
    path(_("profile/") + "<int:pk>", ProfileView.as_view(), name="profile"),
    path(
        _("profile/edit/") + "<int:pk>", ProfileEditView.as_view(), name="profile_edit"
    ),
    path(_("about/"), AboutView.as_view(), name="about"),
    path(_("signup/"), SignupView.as_view(), name="signup"),
    path(_("login/"), auth_views.LoginView.as_view(), name="login"),
    path(_("logout/"), auth_views.LogoutView.as_view(), name="logout"),
    path(
        _("password_change/"),
        auth_views.PasswordChangeView.as_view(),
        name="password_change",
    ),
    path(
        _("password_change_done/"),
        auth_views.PasswordChangeDoneView.as_view(),
        name="password_change_done",
    ),
    path(
        _("password_reset/"),
        auth_views.PasswordResetView.as_view(),
        name="password_reset",
    ),
    path(
        _("password_reset_done/"),
        auth_views.PasswordResetDoneView.as_view(),
        name="password_reset_done",
    ),
    path(
        _("password_reset_confirm/"),
        auth_views.PasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    path(
        _("password_reset_complete/"),
        auth_views.PasswordResetCompleteView.as_view(),
        name="password_reset_complete",
    ),
)

# Upload path
urlpatterns += static(settings.IMAGES_PATH, document_root=settings.IMAGES_ROOT)
