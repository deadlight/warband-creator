from django.db import models


class Weapon(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    short_range_min = models.PositiveIntegerField()
    short_range_max = models.PositiveIntegerField()

    long_range_min = models.PositiveIntegerField()
    long_range_max = models.PositiveIntegerField()

    to_hit_short = models.IntegerField()
    to_hit_long = models.IntegerField()

    strength = models.PositiveIntegerField()
    damage = models.PositiveIntegerField()

    save_modifier = models.IntegerField()

    ammo_roll = models.CharField(max_length=3)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    @property
    def short_range(self):
        return f"{self.short_range_min}-{self.short_range_max}"

    @property
    def long_range(self):
        return f"{self.long_range_min}-{self.long_range_max}"
