from django.db import migrations, models


def migrate_book_data(apps, schema_editor):
    Book = apps.get_model("LibManager", "Book")
    for idx, book in enumerate(Book.objects.all().order_by("id"), start=1):
        copies = getattr(book, "copies", 1) or 1
        book.total_copies = copies
        book.available_copies = copies
        book.isbn = f"LIB{idx:03d}"
        book.save(update_fields=["total_copies", "available_copies", "isbn"])


class Migration(migrations.Migration):
    dependencies = [
        ("LibManager", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="book",
            name="isbn",
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AddField(
            model_name="book",
            name="total_copies",
            field=models.PositiveIntegerField(default=1),
        ),
        migrations.AddField(
            model_name="book",
            name="available_copies",
            field=models.PositiveIntegerField(default=1),
        ),
        migrations.AlterField(
            model_name="book",
            name="title",
            field=models.CharField(max_length=200),
        ),
        migrations.AlterField(
            model_name="book",
            name="author",
            field=models.CharField(max_length=150),
        ),
        migrations.AlterField(
            model_name="book",
            name="genre",
            field=models.CharField(max_length=80),
        ),
        migrations.RunPython(migrate_book_data, migrations.RunPython.noop),
        migrations.RemoveField(
            model_name="book",
            name="copies",
        ),
        migrations.AlterField(
            model_name="book",
            name="isbn",
            field=models.CharField(max_length=20, unique=True),
        ),
        migrations.CreateModel(
            name="IssuedBook",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("user_id", models.CharField(max_length=50)),
                ("issue_date", models.DateField()),
                ("return_date", models.DateField()),
                ("returned", models.BooleanField(default=False)),
                ("fine_amount", models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                (
                    "book",
                    models.ForeignKey(on_delete=models.deletion.CASCADE, related_name="issued_records", to="LibManager.book"),
                ),
            ],
        ),
    ]
