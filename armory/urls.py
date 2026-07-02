from django.urls import path

from . import views

app_name = "armory"

urlpatterns = [
    path("", views.WeaponListView.as_view(), name="weapon_list"),
    path("new/", views.WeaponCreateView.as_view(), name="weapon_create"),
    path("<int:pk>/", views.WeaponDetailView.as_view(), name="weapon_detail"),
    path("<int:pk>/edit/", views.WeaponUpdateView.as_view(), name="weapon_update"),
    path("<int:pk>/delete/", views.WeaponDeleteView.as_view(), name="weapon_delete"),
    path(
        "<int:weapon_pk>/link/",
        views.WeaponLinkCreateView.as_view(),
        name="weapon_link_create",
    ),
    path(
        "<int:weapon_pk>/link/<int:pk>/delete/",
        views.WeaponLinkDeleteView.as_view(),
        name="weapon_link_delete",
    ),
    path(
        "<int:weapon_pk>/profile/new/",
        views.WeaponProfileCreateView.as_view(),
        name="weaponprofile_create",
    ),
    path(
        "<int:weapon_pk>/profile/<int:pk>/edit/",
        views.WeaponProfileUpdateView.as_view(),
        name="weaponprofile_update",
    ),
    path(
        "<int:weapon_pk>/profile/<int:pk>/delete/",
        views.WeaponProfileDeleteView.as_view(),
        name="weaponprofile_delete",
    ),
    path("games/", views.GameListView.as_view(), name="game_list"),
    path("games/new/", views.GameCreateView.as_view(), name="game_create"),
    path("games/<int:pk>/", views.GameDetailView.as_view(), name="game_detail"),
    path("games/<int:pk>/edit/", views.GameUpdateView.as_view(), name="game_update"),
    path("games/<int:pk>/delete/", views.GameDeleteView.as_view(), name="game_delete"),
    path("types/", views.WeaponTypeListView.as_view(), name="weapontype_list"),
    path("types/new/", views.WeaponTypeCreateView.as_view(), name="weapontype_create"),
    path(
        "types/<int:pk>/edit/",
        views.WeaponTypeUpdateView.as_view(),
        name="weapontype_update",
    ),
    path(
        "types/<int:pk>/delete/",
        views.WeaponTypeDeleteView.as_view(),
        name="weapontype_delete",
    ),
    path("rules/", views.SpecialRuleListView.as_view(), name="specialrule_list"),
    path("rules/new/", views.SpecialRuleCreateView.as_view(), name="specialrule_create"),
    path(
        "rules/<int:pk>/",
        views.SpecialRuleDetailView.as_view(),
        name="specialrule_detail",
    ),
    path(
        "rules/<int:pk>/edit/",
        views.SpecialRuleUpdateView.as_view(),
        name="specialrule_update",
    ),
    path(
        "rules/<int:pk>/delete/",
        views.SpecialRuleDeleteView.as_view(),
        name="specialrule_delete",
    ),
    path("factions/", views.FactionListView.as_view(), name="faction_list"),
    path("factions/new/", views.FactionCreateView.as_view(), name="faction_create"),
    path(
        "factions/<int:pk>/edit/",
        views.FactionUpdateView.as_view(),
        name="faction_update",
    ),
    path(
        "factions/<int:pk>/delete/",
        views.FactionDeleteView.as_view(),
        name="faction_delete",
    ),
    path("characters/", views.CharacterListView.as_view(), name="character_list"),
    path("characters/new/", views.CharacterCreateView.as_view(), name="character_create"),
    path(
        "characters/<int:pk>/",
        views.CharacterDetailView.as_view(),
        name="character_detail",
    ),
    path(
        "characters/<int:pk>/edit/",
        views.CharacterUpdateView.as_view(),
        name="character_update",
    ),
    path(
        "characters/<int:pk>/delete/",
        views.CharacterDeleteView.as_view(),
        name="character_delete",
    ),
]
