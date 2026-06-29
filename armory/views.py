from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from .models import Weapon
from .forms import WeaponForm


class WeaponListView(ListView):
    model = Weapon
    context_object_name = "weapons"


class WeaponDetailView(DetailView):
    model = Weapon
    context_object_name = "weapon"


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
