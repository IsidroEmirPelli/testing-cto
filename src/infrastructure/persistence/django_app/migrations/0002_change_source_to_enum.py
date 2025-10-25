from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("persistence", "0001_initial"),
    ]

    operations = [
        migrations.RemoveIndex(
            model_name="sourcemodel",
            name="sources_dominio_065a06_idx",
        ),
        migrations.RemoveField(
            model_name="sourcemodel",
            name="dominio",
        ),
        migrations.RemoveField(
            model_name="sourcemodel",
            name="nombre",
        ),
        migrations.RemoveField(
            model_name="sourcemodel",
            name="pais",
        ),
        migrations.AddField(
            model_name="sourcemodel",
            name="source_type",
            field=models.IntegerField(
                choices=[
                    (1, "Clarín"),
                    (2, "La Nación"),
                    (3, "Página 12"),
                    (4, "Infobae"),
                ],
                unique=True,
                db_index=True,
            ),
        ),
        migrations.AddIndex(
            model_name="sourcemodel",
            index=models.Index(
                fields=["source_type"], name="sources_source__3a2e8f_idx"
            ),
        ),
    ]
