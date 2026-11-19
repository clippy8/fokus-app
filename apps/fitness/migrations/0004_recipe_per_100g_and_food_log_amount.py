from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("fitness", "0003_exercise_equipment_setting_exercise_image")]

    operations = [
        migrations.RenameField(model_name="recipe", old_name="calories_kcal", new_name="calories_kcal_per_100g"),
        migrations.RenameField(model_name="recipe", old_name="protein_g", new_name="protein_g_per_100g"),
        migrations.AlterField(
            model_name="recipe",
            name="calories_kcal_per_100g",
            field=models.PositiveIntegerField(blank=True, null=True, verbose_name="Kalorien pro 100 g (kcal)"),
        ),
        migrations.AlterField(
            model_name="recipe",
            name="protein_g_per_100g",
            field=models.DecimalField(
                blank=True, decimal_places=1, max_digits=6, null=True, verbose_name="Protein pro 100 g (g)"
            ),
        ),
        migrations.AddField(
            model_name="foodlogentry",
            name="amount_g",
            field=models.PositiveIntegerField(blank=True, null=True, verbose_name="Menge (g)"),
        ),
    ]
