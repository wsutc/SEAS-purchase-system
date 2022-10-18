# Generated by Django 4.0.3 on 2022-09-21 20:53

from django.db import migrations, models


def set_product_rank(apps, schema_editor):
    PurchaseRequest = apps.get_model("purchases", "purchaserequest")
    SimpleProduct = apps.get_model("purchases", "simpleproduct")
    requests = PurchaseRequest.objects.all()

    qsa = SimpleProduct.objects.none()

    for r in requests:
        qs = SimpleProduct.objects.filter(purchase_request=r).order_by("pk")
        count = len(qs)
        if count == 0:
            continue

        for c, p in enumerate(qs, 1):
            p.rank = c
            p.save()

    #     qsa = qsa | qs

    # SimpleProduct.objects.bulk_update(qsa, ["rank"])


class Migration(migrations.Migration):

    dependencies = [
        ("purchases", "0088_remove_trackeritem_simple_product_and_more"),
    ]

    operations = [
        # migrations.RunSQL( "ALTER TABLE `seas_purchasing`.`purchases_simpleproduct`
        #     DROP COLUMN `rank`;" ),
        migrations.AddField(
            model_name="simpleproduct",
            name="rank",
            field=models.SmallIntegerField(
                editable=False, null=True, verbose_name="in pr ordering"
            ),
        ),
        # migrations.RunPython(set_product_rank),
        # migrations.AlterField(
        #     model_name="simpleproduct",
        #     name="rank",
        #     field=models.SmallIntegerField(
        #         editable=False, null=False, verbose_name="in pr ordering"
        #     ),
        # ),
    ]
