from django.db import models


class Game(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class WeaponType(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Faction(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Weapon(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    weapon_type = models.ForeignKey(
        WeaponType, on_delete=models.SET_NULL, null=True, blank=True, related_name="weapons"
    )

    faction = models.ForeignKey(
        Faction, on_delete=models.SET_NULL, null=True, blank=True, related_name="weapons"
    )

    close_combat = models.BooleanField(default=False)
    template = models.BooleanField(default=False)

    games = models.ManyToManyField(Game, through="WeaponGame", related_name="weapons")
    special_rules = models.ManyToManyField("SpecialRule", blank=True, related_name="weapons")

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    def _range_display(self):
        if self.template and self.close_combat:
            return "template or close combat"
        if self.template:
            return "template"
        if self.close_combat:
            return "close combat"
        return None

    @property
    def primary_profile(self):
        return self.profiles.first()

    @property
    def short_range(self):
        r = self._range_display()
        if r:
            return r
        profile = self.primary_profile
        if profile:
            return profile.short_range
        return "—"

    @property
    def long_range(self):
        r = self._range_display()
        if r:
            return r
        profile = self.primary_profile
        if profile:
            return profile.long_range
        return "—"

    @property
    def to_hit_short_display(self):
        profile = self.primary_profile
        if profile:
            return profile.to_hit_short_display
        return "—"

    @property
    def to_hit_long_display(self):
        profile = self.primary_profile
        if profile:
            return profile.to_hit_long_display
        return "—"

    @property
    def strength(self):
        profile = self.primary_profile
        return profile.strength if profile else "—"

    @property
    def damage(self):
        profile = self.primary_profile
        return profile.damage if profile else "—"

    @property
    def save_modifier(self):
        profile = self.primary_profile
        return profile.save_modifier if profile else 0

    @property
    def ammo_roll(self):
        profile = self.primary_profile
        return profile.ammo_roll if profile else "—"


class WeaponProfile(models.Model):
    weapon = models.ForeignKey(Weapon, on_delete=models.CASCADE, related_name="profiles")
    name = models.CharField(max_length=100, blank=True)

    short_range_min = models.PositiveIntegerField()
    short_range_max = models.PositiveIntegerField()

    long_range_min = models.PositiveIntegerField()
    long_range_max = models.PositiveIntegerField()

    to_hit_short = models.IntegerField()
    to_hit_long = models.IntegerField()

    strength = models.CharField(max_length=10)
    damage = models.CharField(max_length=10)

    save_modifier = models.IntegerField()

    ammo_roll = models.CharField(max_length=10)

    description = models.TextField(blank=True)

    cost = models.IntegerField(null=True, blank=True)
    per_shot = models.BooleanField(default=False)

    class Meta:
        ordering = ["weapon", "id"]

    def __str__(self):
        label = f"{self.weapon.name}"
        if self.name:
            label += f" ({self.name})"
        return label

    @property
    def short_range(self):
        return f"{self.short_range_min}-{self.short_range_max}"

    @property
    def long_range(self):
        return f"{self.long_range_min}-{self.long_range_max}"

    @property
    def to_hit_short_display(self):
        return self._format_to_hit(self.to_hit_short)

    @property
    def to_hit_long_display(self):
        return self._format_to_hit(self.to_hit_long)

    @staticmethod
    def _format_to_hit(value):
        if value == 0:
            return "-"
        if value > 0:
            return f"+{value}"
        return str(value)

    @property
    def suggested_cost(self):
        """Calculate expected Necromunda credit cost from the rubric."""
        w = self.weapon
        rules = set(w.special_rules.values_list("name", flat=True))
        wtype = w.weapon_type.name if w.weapon_type else "Basic"
        is_power_cc = w.close_combat and not self._is_user_strength and self.strength_val >= 4

        # ---- base cost ----
        if wtype == "Pistol":
            base = 10
        elif wtype == "Close combat" and is_power_cc:
            base = 20
        elif wtype == "Close combat":
            base = 5
        elif wtype == "Basic":
            base = 20
        elif wtype == "Grenade":
            base = 20
        elif wtype == "Special":
            base = 20
        elif wtype == "Heavy":
            base = 40 if w.close_combat else 120  # eviscerator/flamer = 40, stubber/bolter = 120
        else:
            base = 20

        # ---- strength ----
        if self._is_user_strength:
            s_mod = self._user_bonus * 5
        elif is_power_cc:
            sv = self.strength_val
            s_mod = {4: 0, 5: 5, 6: 15, 8: 40}.get(sv, sv * 5)
        else:
            sv = self.strength_val
            s_mod = {3: 0, 4: 5, 5: 10, 6: 20, 7: 30, 8: 50}.get(sv, sv * 5)

        # ---- save modifier ----
        abs_sv = abs(self.save_modifier) if self.save_modifier < 0 else 0
        if wtype == "Heavy":
            sv_mod = abs_sv * 5
        elif abs_sv >= 4:
            sv_mod = 18 + (abs_sv - 4) * 7
        else:
            sv_mod = {0: 0, 1: 5, 2: 8, 3: 12}.get(abs_sv, abs_sv * 5)

        # ---- special rules ----
        rule_costs = {
            "Close Combat": 2,
            "Parry": 5,
            "Two-Handed": 0,
            "Sustained Fire 1": 40,
            "Sustained Fire 2": 60,
            "Sustained Fire 3": 80,
            "Move or Fire": 0,
            "Rapid Fire": 3,
            "Slow Reload": -5,
            "Single Shot": -15,
            "Flamer Template": 5,
            "Catch Fire": 2,
            "Plasma": 5,
            "Plasma Overheat": -5,
            "Toxin": 15,
            "Web": 10,
            "Knockout": 0,
            'Blast 2"': 5,
            'Blast 3"': 10,
            "Smoke": 0,
            "Gas Cloud": 5,
            "Choke": 5,
            "Hallucinogen": 5,
            "Blind": 5,
            "Armour Piercing": 5,
            "Indirect Fire": 5,
            "Burster": 0,
            "Rending Claws": 5,
            "Fear": 3,
            "Terror": 5,
            "Variable Strength": 5,
            "Stealth": 5,
            "1 or 2 Handed": 0,
            "Explodes on Death": -5,
        }
        rule_mod = sum(rule_costs.get(r, 0) for r in rules)

        return base + s_mod + sv_mod + rule_mod

    @property
    def _is_user_strength(self):
        return "User" in self.strength

    @property
    def _user_bonus(self):
        if not self._is_user_strength:
            return 0
        import re

        m = re.search(r"User\s*\+\s*(\d+)", self.strength)
        return int(m.group(1)) if m else 0

    @property
    def strength_val(self):
        try:
            return int(self.strength)
        except (ValueError, TypeError):
            return 0


class WeaponGame(models.Model):
    weapon = models.ForeignKey(Weapon, on_delete=models.CASCADE, related_name="weapon_games")
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name="weapon_games")
    cost = models.IntegerField(null=True, blank=True)

    class Meta:
        unique_together = ["weapon", "game"]
        ordering = ["game__name"]

    def __str__(self):
        return f"{self.weapon.name} in {self.game.name}"


class SpecialRule(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Character(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    faction = models.ForeignKey(
        Faction, on_delete=models.SET_NULL, null=True, blank=True, related_name="characters"
    )

    movement = models.PositiveIntegerField()
    weapon_skill = models.PositiveIntegerField()
    ballistic_skill = models.PositiveIntegerField()
    strength = models.PositiveIntegerField()
    toughness = models.PositiveIntegerField()
    wounds = models.PositiveIntegerField()
    initiative = models.PositiveIntegerField()
    attacks = models.PositiveIntegerField()
    leadership = models.PositiveIntegerField()

    weapon_types = models.ManyToManyField(WeaponType, blank=True, related_name="characters")
    games = models.ManyToManyField(Game, through="CharacterGameCost", related_name="characters")

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    @property
    def statline(self):
        return f"M{self.movement} WS{self.weapon_skill} BS{self.ballistic_skill} S{self.strength} T{self.toughness} W{self.wounds} I{self.initiative} A{self.attacks} Ld{self.leadership}"


class CharacterGameCost(models.Model):
    character = models.ForeignKey(
        Character, on_delete=models.CASCADE, related_name="character_games"
    )
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name="character_games")
    cost = models.IntegerField(null=True, blank=True)

    class Meta:
        unique_together = ["character", "game"]

    def __str__(self):
        return f"{self.character.name} in {self.game.name}"


class Warband(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name="warbands")
    faction = models.ForeignKey(
        Faction, on_delete=models.SET_NULL, null=True, blank=True, related_name="warbands"
    )

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    @property
    def total_cost(self):
        return sum(member.total_cost for member in self.members.all())


class WarbandMember(models.Model):
    warband = models.ForeignKey(Warband, on_delete=models.CASCADE, related_name="members")
    character = models.ForeignKey(
        Character, on_delete=models.CASCADE, related_name="warband_memberships"
    )
    name = models.CharField(max_length=255, blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "character__name"]

    def __str__(self):
        return f"{self.display_name} in {self.warband.name}"

    @property
    def display_name(self):
        return self.name or self.character.name

    @property
    def total_cost(self):
        weapon_cost = sum(w.weapon_game.cost or 0 for w in self.weapons.all() if w.weapon_game)
        return weapon_cost


class WarbandMemberWeapon(models.Model):
    member = models.ForeignKey(WarbandMember, on_delete=models.CASCADE, related_name="weapons")
    weapon_game = models.ForeignKey(
        WeaponGame,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="warband_assignments",
    )

    class Meta:
        ordering = ["weapon_game__weapon__name"]

    def __str__(self):
        weapon_name = self.weapon_game.weapon.name if self.weapon_game else "(no weapon)"
        return f"{weapon_name} for {self.member}"
