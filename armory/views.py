from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView
from django.views.generic.edit import BaseDeleteView

from .forms import (
    CharacterForm,
    FactionForm,
    GameForm,
    SpecialRuleForm,
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
    Weapon,
    WeaponGame,
    WeaponProfile,
    WeaponType,
)


class WeaponListView(ListView):
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


class WeaponDetailView(DetailView):
    model = Weapon
    context_object_name = "weapon"
    queryset = Weapon.objects.prefetch_related("profiles")


class WeaponCreateView(CreateView):
    model = Weapon
    form_class = WeaponForm
    success_url = reverse_lazy("armory:weapon_list")


class WeaponUpdateView(UpdateView):
    model = Weapon
    form_class = WeaponForm
    success_url = reverse_lazy("armory:weapon_list")


class WeaponDeleteView(DeleteView):
    model = Weapon
    success_url = reverse_lazy("armory:weapon_list")


class WeaponLinkCreateView(CreateView):
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


class WeaponLinkDeleteView(BaseDeleteView):
    model = WeaponGame
    template_name = "armory/weapongame_confirm_delete.html"

    def get_success_url(self):
        return reverse("armory:weapon_detail", kwargs={"pk": self.kwargs["weapon_pk"]})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["weapon"] = get_object_or_404(Weapon, pk=self.kwargs["weapon_pk"])
        return context


class WeaponProfileCreateView(CreateView):
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


class WeaponProfileUpdateView(UpdateView):
    model = WeaponProfile
    form_class = WeaponProfileForm
    template_name = "armory/weaponprofile_form.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["weapon"] = get_object_or_404(Weapon, pk=self.kwargs["weapon_pk"])
        return context

    def get_success_url(self):
        return reverse("armory:weapon_detail", kwargs={"pk": self.kwargs["weapon_pk"]})


class WeaponProfileDeleteView(DeleteView):
    model = WeaponProfile
    template_name = "armory/weaponprofile_confirm_delete.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["weapon"] = get_object_or_404(Weapon, pk=self.kwargs["weapon_pk"])
        return context

    def get_success_url(self):
        return reverse("armory:weapon_detail", kwargs={"pk": self.kwargs["weapon_pk"]})


class GameListView(ListView):
    model = Game
    context_object_name = "games"


class GameDetailView(DetailView):
    model = Game
    context_object_name = "game"


class GameCreateView(CreateView):
    model = Game
    form_class = GameForm
    success_url = reverse_lazy("armory:game_list")


class GameUpdateView(UpdateView):
    model = Game
    form_class = GameForm
    success_url = reverse_lazy("armory:game_list")


class GameDeleteView(DeleteView):
    model = Game
    success_url = reverse_lazy("armory:game_list")


class WeaponTypeListView(ListView):
    model = WeaponType
    context_object_name = "weapon_types"


class WeaponTypeCreateView(CreateView):
    model = WeaponType
    form_class = WeaponTypeForm
    success_url = reverse_lazy("armory:weapontype_list")


class WeaponTypeUpdateView(UpdateView):
    model = WeaponType
    form_class = WeaponTypeForm
    success_url = reverse_lazy("armory:weapontype_list")


class WeaponTypeDeleteView(DeleteView):
    model = WeaponType
    success_url = reverse_lazy("armory:weapontype_list")


class SpecialRuleListView(ListView):
    model = SpecialRule
    context_object_name = "special_rules"


class SpecialRuleDetailView(DetailView):
    model = SpecialRule
    context_object_name = "special_rule"


class SpecialRuleCreateView(CreateView):
    model = SpecialRule
    form_class = SpecialRuleForm
    success_url = reverse_lazy("armory:specialrule_list")


class SpecialRuleUpdateView(UpdateView):
    model = SpecialRule
    form_class = SpecialRuleForm
    success_url = reverse_lazy("armory:specialrule_list")


class SpecialRuleDeleteView(DeleteView):
    model = SpecialRule
    success_url = reverse_lazy("armory:specialrule_list")


class FactionListView(ListView):
    model = Faction
    context_object_name = "factions"


class FactionCreateView(CreateView):
    model = Faction
    form_class = FactionForm
    success_url = reverse_lazy("armory:faction_list")


class FactionUpdateView(UpdateView):
    model = Faction
    form_class = FactionForm
    success_url = reverse_lazy("armory:faction_list")


class FactionDeleteView(DeleteView):
    model = Faction
    success_url = reverse_lazy("armory:faction_list")


class CharacterListView(ListView):
    model = Character
    context_object_name = "characters"


class CharacterDetailView(DetailView):
    model = Character
    context_object_name = "character"


class CharacterCreateView(CreateView):
    model = Character
    form_class = CharacterForm
    success_url = reverse_lazy("armory:character_list")


class CharacterUpdateView(UpdateView):
    model = Character
    form_class = CharacterForm
    success_url = reverse_lazy("armory:character_list")


class CharacterDeleteView(DeleteView):
    model = Character
    success_url = reverse_lazy("armory:character_list")
