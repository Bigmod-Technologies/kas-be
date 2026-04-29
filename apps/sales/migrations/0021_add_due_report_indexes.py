from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("sales", "0020_remove_orderitem_shift"),
    ]

    operations = [
        migrations.AddIndex(
            model_name="duesell",
            index=models.Index(
                fields=["customer", "-sale_date", "-created_at"],
                name="sales_duesel_custome_286da7_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="duecollection",
            index=models.Index(
                fields=["customer", "-collection_date", "-created_at"],
                name="sales_dueco_custome_0395f4_idx",
            ),
        ),
    ]
