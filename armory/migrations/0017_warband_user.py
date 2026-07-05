from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


def assign_warbands_to_admin(apps, schema_editor):
    Warband = apps.get_model("armory", "Warband")
    User = apps.get_model("auth", "User")
    admin_user = User.objects.filter(is_superuser=True).first()
    if admin_user:
        Warband.objects.filter(user__isnull=True).update(user=admin_user)


class Migration(migrations.Migration):

    dependencies = [
        ("armory", "0016_alter_warbandmember_options_warbandmember_name_and_more"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="warband",
            name="user",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="warbands",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.RunPython(assign_warbands_to_admin),
        migrations.AlterField(
            model_name="warband",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="warbands",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
