from django import forms

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


class FactionForm(forms.ModelForm):
    class Meta:
        model = Faction
        fields = ["name"]


class GameForm(forms.ModelForm):
    class Meta:
        model = Game
        fields = ["name", "description"]


class WeaponTypeForm(forms.ModelForm):
    class Meta:
        model = WeaponType
        fields = ["name"]


class WeaponForm(forms.ModelForm):
    class Meta:
        model = Weapon
        fields = [
            "name",
            "description",
            "weapon_type",
            "faction",
            "close_combat",
            "template",
            "special_rules",
        ]
        labels = {
            "weapon_type": "Type",
            "faction": "Faction",
            "close_combat": "Close combat weapon",
            "template": "Template weapon",
            "special_rules": "Special rules",
        }
        widgets = {
            "special_rules": forms.CheckboxSelectMultiple,
        }


class WeaponProfileForm(forms.ModelForm):
    class Meta:
        model = WeaponProfile
        fields = [
            "name",
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
            "description",
            "cost",
            "per_shot",
        ]
        labels = {
            "name": "Profile name",
            "short_range_min": "Short range (min)",
            "short_range_max": "Short range (max)",
            "long_range_min": "Long range (min)",
            "long_range_max": "Long range (max)",
            "to_hit_short": "To Hit (short)",
            "to_hit_long": "To Hit (long)",
            "save_modifier": "Save modifier",
            "ammo_roll": "Ammo roll",
            "description": "Description",
            "cost": "Cost (credits)",
            "per_shot": "Cost is per shot",
        }


class WeaponGameForm(forms.ModelForm):
    class Meta:
        model = WeaponGame
        fields = ["game", "cost"]
        labels = {
            "game": "Game system",
            "cost": "Cost (points)",
        }

    def __init__(self, *args, weapon=None, **kwargs):
        super().__init__(*args, **kwargs)
        if weapon:
            linked_game_ids = weapon.weapon_games.values_list("game_id", flat=True)
            self.fields["game"].queryset = Game.objects.exclude(id__in=linked_game_ids)
            self.instance.weapon = weapon


class SpecialRuleForm(forms.ModelForm):
    class Meta:
        model = SpecialRule
        fields = ["name", "description"]


class CharacterForm(forms.ModelForm):
    class Meta:
        model = Character
        fields = [
            "name",
            "description",
            "faction",
            "movement",
            "weapon_skill",
            "ballistic_skill",
            "strength",
            "toughness",
            "wounds",
            "initiative",
            "attacks",
            "leadership",
            "weapon_types",
        ]
        labels = {
            "movement": "M",
            "weapon_skill": "WS",
            "ballistic_skill": "BS",
            "strength": "S",
            "toughness": "T",
            "wounds": "W",
            "initiative": "I",
            "attacks": "A",
            "leadership": "Ld",
            "weapon_types": "Can use weapon types",
        }
        widgets = {
            "weapon_types": forms.CheckboxSelectMultiple,
        }


class WarbandForm(forms.ModelForm):
    class Meta:
        model = Warband
        fields = ["name", "description", "game", "faction"]
        labels = {
            "game": "Game system",
            "faction": "Faction",
        }


class WarbandMemberForm(forms.ModelForm):
    class Meta:
        model = WarbandMember
        fields = ["character", "name", "order"]
        labels = {
            "character": "Character",
            "name": "Custom name (optional)",
            "order": "Sort order",
        }

    def __init__(self, *args, warband=None, **kwargs):
        super().__init__(*args, **kwargs)
        if warband:
            self.instance.warband = warband


class WarbandMemberWeaponForm(forms.ModelForm):
    class Meta:
        model = WarbandMemberWeapon
        fields = ["weapon_game"]
        labels = {
            "weapon_game": "Weapon",
        }

    def __init__(self, *args, warband=None, member=None, **kwargs):
        super().__init__(*args, **kwargs)
        if warband:
            self.fields["weapon_game"].queryset = WeaponGame.objects.filter(
                game=warband.game
            ).select_related("weapon")
        if member:
            self.instance.member = member
