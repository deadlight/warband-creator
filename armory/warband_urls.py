from django.urls import path

from . import views

app_name = "warbands"

urlpatterns = [
    path("", views.WarbandListView.as_view(), name="warband_list"),
    path("new/", views.WarbandCreateView.as_view(), name="warband_create"),
    path("<int:pk>/", views.WarbandDetailView.as_view(), name="warband_detail"),
    path("<int:pk>/builder/", views.WarbandBuilderView.as_view(), name="warband_builder"),
    path(
        "<int:pk>/api/add-member/",
        views.WarbandAddMemberAPI.as_view(),
        name="warband_add_member_api",
    ),
    path("<int:pk>/edit/", views.WarbandUpdateView.as_view(), name="warband_update"),
    path("<int:pk>/delete/", views.WarbandDeleteView.as_view(), name="warband_delete"),
    path(
        "<int:warband_pk>/member/new/",
        views.WarbandMemberCreateView.as_view(),
        name="warbandmember_create",
    ),
    path(
        "<int:warband_pk>/member/<int:pk>/edit/",
        views.WarbandMemberUpdateView.as_view(),
        name="warbandmember_update",
    ),
    path(
        "<int:warband_pk>/member/<int:pk>/delete/",
        views.WarbandMemberDeleteView.as_view(),
        name="warbandmember_delete",
    ),
    path(
        "<int:warband_pk>/member/<int:member_pk>/weapon/new/",
        views.WarbandMemberWeaponCreateView.as_view(),
        name="warbandmemberweapon_create",
    ),
    path(
        "<int:warband_pk>/member/<int:member_pk>/weapon/<int:pk>/delete/",
        views.WarbandMemberWeaponDeleteView.as_view(),
        name="warbandmemberweapon_delete",
    ),
    path(
        "<int:warband_pk>/member/<int:member_pk>/api/add-weapon/",
        views.WarbandAddWeaponAPI.as_view(),
        name="warband_add_weapon_api",
    ),
]
