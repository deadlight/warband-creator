import django.db.models.deletion
from django.db import migrations, models


def copy_weapon_stats_to_profiles(apps, schema_editor):
    Weapon = apps.get_model("armory", "Weapon")
    WeaponProfile = apps.get_model("armory", "WeaponProfile")

    for weapon in Weapon.objects.all():
        WeaponProfile.objects.create(
            weapon=weapon,
            short_range_min=weapon.short_range_min,
            short_range_max=weapon.short_range_max,
            long_range_min=weapon.long_range_min,
            long_range_max=weapon.long_range_max,
            to_hit_short=weapon.to_hit_short,
            to_hit_long=weapon.to_hit_long,
            strength=str(weapon.strength),
            damage=str(weapon.damage),
            save_modifier=weapon.save_modifier,
            ammo_roll=weapon.ammo_roll,
        )


class Migration(migrations.Migration):

    dependencies = [
        ("armory", "0008_specialrule_weapon_special_rules"),
    ]

    operations = [
        migrations.CreateModel(
            name="WeaponProfile",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("name", models.CharField(blank=True, max_length=100)),
                ("short_range_min", models.PositiveIntegerField()),
                ("short_range_max", models.PositiveIntegerField()),
                ("long_range_min", models.PositiveIntegerField()),
                ("long_range_max", models.PositiveIntegerField()),
                ("to_hit_short", models.IntegerField()),
                ("to_hit_long", models.IntegerField()),
                ("strength", models.CharField(max_length=10)),
                ("damage", models.CharField(max_length=10)),
                ("save_modifier", models.IntegerField()),
                ("ammo_roll", models.CharField(max_length=3)),
                (
                    "weapon",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="profiles",
                        to="armory.weapon",
                    ),
                ),
            ],
            options={
                "ordering": ["weapon", "id"],
            },
        ),
        migrations.RunPython(copy_weapon_stats_to_profiles, reverse_code=migrations.RunPython.noop),
        migrations.RemoveField(model_name="weapon", name="ammo_roll"),
        migrations.RemoveField(model_name="weapon", name="damage"),
        migrations.RemoveField(model_name="weapon", name="long_range_max"),
        migrations.RemoveField(model_name="weapon", name="long_range_min"),
        migrations.RemoveField(model_name="weapon", name="save_modifier"),
        migrations.RemoveField(model_name="weapon", name="short_range_max"),
        migrations.RemoveField(model_name="weapon", name="short_range_min"),
        migrations.RemoveField(model_name="weapon", name="strength"),
        migrations.RemoveField(model_name="weapon", name="to_hit_long"),
        migrations.RemoveField(model_name="weapon", name="to_hit_short"),
    ]
