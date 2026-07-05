from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Max, Prefetch
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView
from django.views.generic.edit import BaseDeleteView

from .forms import (
    CharacterForm,
    FactionForm,
    GameForm,
    SpecialRuleForm,
    WarbandForm,
    WarbandMemberForm,
    WarbandMemberWeaponForm,
    WeaponForm,
    WeaponGameForm,
    WeaponProfileForm,
    WeaponTypeForm,
)
from .models import (
    Character,
    Faction,
    Game,
    SpecialRule,
    Warband,
    WarbandMember,
    WarbandMemberWeapon,
    Weapon,
    WeaponGame,
    WeaponProfile,
    WeaponType,
)


class WeaponListView(LoginRequiredMixin, ListView):
    model = Weapon
    context_object_name = "weapons"
    paginate_by = 50

    def get_queryset(self):
        qs = Weapon.objects.prefetch_related("profiles", "weapon_games__game", "special_rules")
        qs = qs.select_related("weapon_type", "faction")

        # Filter by weapon type
        type_id = self.request.GET.get("type")
        if type_id:
            qs = qs.filter(weapon_type_id=type_id)

        # Filter by faction
        faction_id = self.request.GET.get("faction")
        if faction_id:
            qs = qs.filter(faction_id=faction_id)

        # Filter by game
        game_id = self.request.GET.get("game")
        if game_id:
            qs = qs.filter(weapon_games__game_id=game_id)

        # Filter by close combat vs ranged
        cc = self.request.GET.get("cc")
        if cc == "1":
            qs = qs.filter(close_combat=True)
        elif cc == "0":
            qs = qs.filter(close_combat=False, template=False)

        # Filter by template
        if self.request.GET.get("template") == "1":
            qs = qs.filter(template=True)

        # Search by name
        search = self.request.GET.get("search", "").strip()
        if search:
            qs = qs.filter(name__icontains=search)

        return qs.distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["weapon_types"] = WeaponType.objects.all()
        context["factions"] = Faction.objects.all()
        context["games"] = Game.objects.all()
        context["current_filters"] = self.request.GET.dict()
        return context


class WeaponDetailView(LoginRequiredMixin, DetailView):
    model = Weapon
    context_object_name = "weapon"

    def get_queryset(self):
        return Weapon.objects.prefetch_related(
            "profiles", "weapon_games__game", "special_rules"
        ).select_related("weapon_type", "faction")


class WeaponCreateView(LoginRequiredMixin, CreateView):
    model = Weapon
    form_class = WeaponForm
    success_url = reverse_lazy("armory:weapon_list")


class WeaponUpdateView(LoginRequiredMixin, UpdateView):
    model = Weapon
    form_class = WeaponForm
    success_url = reverse_lazy("armory:weapon_list")


class WeaponDeleteView(LoginRequiredMixin, DeleteView):
    model = Weapon
    success_url = reverse_lazy("armory:weapon_list")


class WeaponLinkCreateView(LoginRequiredMixin, CreateView):
    model = WeaponGame
    form_class = WeaponGameForm
    template_name = "armory/weapongame_form.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["weapon"] = get_object_or_404(Weapon, pk=self.kwargs["weapon_pk"])
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["weapon"] = get_object_or_404(Weapon, pk=self.kwargs["weapon_pk"])
        context["existing_links"] = context["weapon"].weapon_games.select_related("game").all()
        return context

    def get_success_url(self):
        return reverse("armory:weapon_detail", kwargs={"pk": self.kwargs["weapon_pk"]})


class WeaponLinkDeleteView(LoginRequiredMixin, BaseDeleteView):
    model = WeaponGame
    template_name = "armory/weapongame_confirm_delete.html"

    def get_success_url(self):
        return reverse("armory:weapon_detail", kwargs={"pk": self.kwargs["weapon_pk"]})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["weapon"] = get_object_or_404(Weapon, pk=self.kwargs["weapon_pk"])
        return context


class WeaponProfileCreateView(LoginRequiredMixin, CreateView):
    model = WeaponProfile
    form_class = WeaponProfileForm
    template_name = "armory/weaponprofile_form.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        self.weapon = get_object_or_404(Weapon, pk=self.kwargs["weapon_pk"])
        return kwargs

    def form_valid(self, form):
        form.instance.weapon = self.weapon
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["weapon"] = self.weapon
        return context

    def get_success_url(self):
        return reverse("armory:weapon_detail", kwargs={"pk": self.kwargs["weapon_pk"]})


class WeaponProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = WeaponProfile
    form_class = WeaponProfileForm
    template_name = "armory/weaponprofile_form.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["weapon"] = get_object_or_404(Weapon, pk=self.kwargs["weapon_pk"])
        return context

    def get_success_url(self):
        return reverse("armory:weapon_detail", kwargs={"pk": self.kwargs["weapon_pk"]})


class WeaponProfileDeleteView(LoginRequiredMixin, DeleteView):
    model = WeaponProfile
    template_name = "armory/weaponprofile_confirm_delete.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["weapon"] = get_object_or_404(Weapon, pk=self.kwargs["weapon_pk"])
        return context

    def get_success_url(self):
        return reverse("armory:weapon_detail", kwargs={"pk": self.kwargs["weapon_pk"]})


class GameListView(LoginRequiredMixin, ListView):
    model = Game
    context_object_name = "games"


class GameDetailView(LoginRequiredMixin, DetailView):
    model = Game
    context_object_name = "game"

    def get_queryset(self):
        return Game.objects.prefetch_related(
            Prefetch(
                "weapon_games",
                queryset=WeaponGame.objects.select_related("weapon__weapon_type", "weapon__faction")
                .prefetch_related("weapon__profiles", "weapon__special_rules")
                .order_by("weapon__name"),
            )
        )


class GameCreateView(LoginRequiredMixin, CreateView):
    model = Game
    form_class = GameForm
    success_url = reverse_lazy("armory:game_list")


class GameUpdateView(LoginRequiredMixin, UpdateView):
    model = Game
    form_class = GameForm
    success_url = reverse_lazy("armory:game_list")


class GameDeleteView(LoginRequiredMixin, DeleteView):
    model = Game
    success_url = reverse_lazy("armory:game_list")


class WeaponTypeListView(LoginRequiredMixin, ListView):
    model = WeaponType
    context_object_name = "weapon_types"


class WeaponTypeCreateView(LoginRequiredMixin, CreateView):
    model = WeaponType
    form_class = WeaponTypeForm
    success_url = reverse_lazy("armory:weapontype_list")


class WeaponTypeUpdateView(LoginRequiredMixin, UpdateView):
    model = WeaponType
    form_class = WeaponTypeForm
    success_url = reverse_lazy("armory:weapontype_list")


class WeaponTypeDeleteView(LoginRequiredMixin, DeleteView):
    model = WeaponType
    success_url = reverse_lazy("armory:weapontype_list")


class SpecialRuleListView(LoginRequiredMixin, ListView):
    model = SpecialRule
    context_object_name = "special_rules"


class SpecialRuleDetailView(LoginRequiredMixin, DetailView):
    model = SpecialRule
    context_object_name = "special_rule"


class SpecialRuleCreateView(LoginRequiredMixin, CreateView):
    model = SpecialRule
    form_class = SpecialRuleForm
    success_url = reverse_lazy("armory:specialrule_list")


class SpecialRuleUpdateView(LoginRequiredMixin, UpdateView):
    model = SpecialRule
    form_class = SpecialRuleForm
    success_url = reverse_lazy("armory:specialrule_list")


class SpecialRuleDeleteView(LoginRequiredMixin, DeleteView):
    model = SpecialRule
    success_url = reverse_lazy("armory:specialrule_list")


class FactionListView(LoginRequiredMixin, ListView):
    model = Faction
    context_object_name = "factions"


class FactionCreateView(LoginRequiredMixin, CreateView):
    model = Faction
    form_class = FactionForm
    success_url = reverse_lazy("armory:faction_list")


class FactionUpdateView(LoginRequiredMixin, UpdateView):
    model = Faction
    form_class = FactionForm
    success_url = reverse_lazy("armory:faction_list")


class FactionDeleteView(LoginRequiredMixin, DeleteView):
    model = Faction
    success_url = reverse_lazy("armory:faction_list")


class CharacterListView(LoginRequiredMixin, ListView):
    model = Character
    context_object_name = "characters"

    def get_queryset(self):
        return Character.objects.prefetch_related(
            "character_games__game", "faction", "weapon_types"
        )


class CharacterDetailView(LoginRequiredMixin, DetailView):
    model = Character
    context_object_name = "character"

    def get_queryset(self):
        return Character.objects.prefetch_related(
            "character_games__game", "weapon_types", "faction"
        )


class CharacterCreateView(LoginRequiredMixin, CreateView):
    model = Character
    form_class = CharacterForm
    success_url = reverse_lazy("armory:character_list")


class CharacterUpdateView(LoginRequiredMixin, UpdateView):
    model = Character
    form_class = CharacterForm
    success_url = reverse_lazy("armory:character_list")


class CharacterDeleteView(LoginRequiredMixin, DeleteView):
    model = Character
    success_url = reverse_lazy("armory:character_list")


class WarbandListView(LoginRequiredMixin, ListView):
    model = Warband
    context_object_name = "warbands"

    def get_queryset(self):
        members_qs = WarbandMember.objects.order_by("order", "character__name")
        return (
            Warband.objects.filter(user=self.request.user)
            .annotate(member_count=Count("members"))
            .prefetch_related(
                Prefetch("members", queryset=members_qs.select_related("character")),
                "game",
                "faction",
            )
        )


class WarbandDetailView(LoginRequiredMixin, DetailView):
    model = Warband
    context_object_name = "warband"

    def get_queryset(self):
        members_qs = WarbandMember.objects.order_by("order", "character__name")
        return Warband.objects.filter(user=self.request.user).prefetch_related(
            Prefetch(
                "members",
                queryset=members_qs.prefetch_related(
                    "character",
                    Prefetch(
                        "weapons",
                        queryset=WarbandMemberWeapon.objects.select_related(
                            "weapon_game__weapon", "weapon_game__game"
                        ),
                    ),
                ),
            ),
            "game",
            "faction",
        )


class WarbandBuilderView(LoginRequiredMixin, DetailView):
    model = Warband
    context_object_name = "warband"
    template_name = "armory/warband_builder.html"

    def get_queryset(self):
        members_qs = WarbandMember.objects.order_by("order", "character__name")
        return Warband.objects.filter(user=self.request.user).prefetch_related(
            Prefetch(
                "members",
                queryset=members_qs.prefetch_related(
                    "character",
                    Prefetch(
                        "weapons",
                        queryset=WarbandMemberWeapon.objects.select_related(
                            "weapon_game__weapon", "weapon_game__game"
                        ),
                    ),
                ),
            ),
            "game",
            "faction",
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        warband = self.object

        # Get available characters (all characters for the warband's game)
        context["available_characters"] = (
            Character.objects.filter(character_games__game=warband.game)
            .select_related("faction")
            .distinct()
            .order_by("name")
        )

        # Get available weapons (all weapon games for the warband's game)
        context["available_weapons"] = (
            WeaponGame.objects.filter(game=warband.game)
            .select_related("weapon", "weapon__weapon_type", "weapon__faction")
            .order_by("weapon__name")
        )

        return context


class WarbandAddMemberAPI(LoginRequiredMixin, View):
    def post(self, request, pk):
        warband = get_object_or_404(Warband, pk=pk, user=request.user)

        import json

        try:
            data = json.loads(request.body)
            character_id = data.get("character_id")
        except (json.JSONDecodeError, ValueError):
            character_id = request.POST.get("character_id")

        if not character_id:
            return JsonResponse({"success": False, "error": "Character ID required"}, status=400)

        character = get_object_or_404(Character, pk=character_id)

        # Check if character already in warband
        if WarbandMember.objects.filter(warband=warband, character=character).exists():
            return JsonResponse(
                {"success": False, "error": "Character already in warband"}, status=400
            )

        # Get max order
        max_order = (
            WarbandMember.objects.filter(warband=warband).aggregate(max_order=Max("order"))[
                "max_order"
            ]
            or 0
        )

        member = WarbandMember.objects.create(
            warband=warband, character=character, order=max_order + 1
        )

        return JsonResponse(
            {"success": True, "member_id": member.pk, "member_name": member.display_name}
        )


class WarbandAddWeaponAPI(LoginRequiredMixin, View):
    def post(self, request, pk, member_pk):
        warband = get_object_or_404(Warband, pk=pk, user=request.user)
        member = get_object_or_404(WarbandMember, pk=member_pk, warband=warband)

        import json

        try:
            data = json.loads(request.body)
            weapon_game_id = data.get("weapon_game_id")
        except (json.JSONDecodeError, ValueError):
            weapon_game_id = request.POST.get("weapon_game_id")

        if not weapon_game_id:
            return JsonResponse({"success": False, "error": "Weapon game ID required"}, status=400)

        weapon_game = get_object_or_404(WeaponGame, pk=weapon_game_id, game=warband.game)

        # Check if weapon already assigned
        if WarbandMemberWeapon.objects.filter(member=member, weapon_game=weapon_game).exists():
            return JsonResponse({"success": False, "error": "Weapon already assigned"}, status=400)

        WarbandMemberWeapon.objects.create(member=member, weapon_game=weapon_game)

        return JsonResponse({"success": True, "weapon_name": weapon_game.weapon.name})


class WarbandCreateView(LoginRequiredMixin, CreateView):
    model = Warband
    form_class = WarbandForm
    success_url = reverse_lazy("warbands:warband_list")

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class WarbandUpdateView(LoginRequiredMixin, UpdateView):
    model = Warband
    form_class = WarbandForm
    success_url = reverse_lazy("warbands:warband_list")

    def get_queryset(self):
        return Warband.objects.filter(user=self.request.user)


class WarbandDeleteView(LoginRequiredMixin, DeleteView):
    model = Warband
    success_url = reverse_lazy("warbands:warband_list")

    def get_queryset(self):
        return Warband.objects.filter(user=self.request.user)


class WarbandMemberCreateView(LoginRequiredMixin, CreateView):
    model = WarbandMember
    form_class = WarbandMemberForm
    template_name = "armory/warbandmember_form.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        self.warband = get_object_or_404(
            Warband, pk=self.kwargs["warband_pk"], user=self.request.user
        )
        kwargs["warband"] = self.warband
        return kwargs

    def form_valid(self, form):
        form.instance.warband = self.warband
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["warband"] = self.warband
        return context

    def get_success_url(self):
        return reverse("warbands:warband_detail", kwargs={"pk": self.kwargs["warband_pk"]})


class WarbandMemberUpdateView(LoginRequiredMixin, UpdateView):
    model = WarbandMember
    form_class = WarbandMemberForm
    template_name = "armory/warbandmember_form.html"

    def get_queryset(self):
        return WarbandMember.objects.filter(warband__user=self.request.user)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["warband"] = self.object.warband
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["warband"] = self.object.warband
        context["member"] = self.object
        return context

    def get_success_url(self):
        return reverse("warbands:warband_detail", kwargs={"pk": self.object.warband_id})


class WarbandMemberDeleteView(LoginRequiredMixin, DeleteView):
    model = WarbandMember
    template_name = "armory/warbandmember_confirm_delete.html"

    def get_queryset(self):
        return WarbandMember.objects.filter(warband__user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["warband"] = self.object.warband
        return context

    def get_success_url(self):
        return reverse("warbands:warband_detail", kwargs={"pk": self.object.warband_id})


class WarbandMemberWeaponCreateView(LoginRequiredMixin, CreateView):
    model = WarbandMemberWeapon
    form_class = WarbandMemberWeaponForm
    template_name = "armory/warbandmemberweapon_form.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        self.member = get_object_or_404(
            WarbandMember.objects.filter(warband__user=self.request.user).select_related(
                "warband__game"
            ),
            pk=self.kwargs["member_pk"],
        )
        kwargs["warband"] = self.member.warband
        kwargs["member"] = self.member
        return kwargs

    def form_valid(self, form):
        form.instance.member = self.member
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["member"] = self.member
        context["warband"] = self.member.warband
        return context

    def get_success_url(self):
        return reverse("warbands:warband_detail", kwargs={"pk": self.member.warband_id})


class WarbandMemberWeaponDeleteView(LoginRequiredMixin, DeleteView):
    model = WarbandMemberWeapon
    template_name = "armory/warbandmemberweapon_confirm_delete.html"

    def get_queryset(self):
        return WarbandMemberWeapon.objects.filter(member__warband__user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        obj = self.get_object()
        context["warband"] = obj.member.warband
        context["member"] = obj.member
        return context

    def get_success_url(self):
        obj = self.get_object()
        return reverse("warbands:warband_detail", kwargs={"pk": obj.member.warband_id})
