from django import forms

from .models import Weapon


class WeaponForm(forms.ModelForm):
    class Meta:
        model = Weapon
        fields = [
            "name",
            "description",
            "short_range_min",
            "short_range_max",
            "long_range_min",
            "long_range_max",
            "to_hit_short",
            "to_hit_long",
            "strength",
            "damage",
            "save_modifier",
            "ammo_roll",
        ]
        labels = {
            "short_range_min": "Short range (min)",
            "short_range_max": "Short range (max)",
            "long_range_min": "Long range (min)",
            "long_range_max": "Long range (max)",
            "to_hit_short": "To Hit (short)",
            "to_hit_long": "To Hit (long)",
            "save_modifier": "Save modifier",
            "ammo_roll": "Ammo roll",
        }
