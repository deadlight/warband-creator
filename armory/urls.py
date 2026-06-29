from django.urls import path

from . import views

app_name = "armory"

urlpatterns = [
    path("", views.WeaponListView.as_view(), name="weapon_list"),
    path("new/", views.WeaponCreateView.as_view(), name="weapon_create"),
    path("<int:pk>/", views.WeaponDetailView.as_view(), name="weapon_detail"),
    path("<int:pk>/edit/", views.WeaponUpdateView.as_view(), name="weapon_update"),
    path("<int:pk>/delete/", views.WeaponDeleteView.as_view(), name="weapon_delete"),
]
