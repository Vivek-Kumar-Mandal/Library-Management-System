from django.db import models


class User(models.Model):
    user_id = models.CharField(max_length=50, unique=True, primary_key=True)
    password_hash = models.CharField(max_length=255)
    name = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user_id} - {self.name}"


class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=150)
    genre = models.CharField(max_length=80)
    isbn = models.CharField(max_length=20, unique=True)
    total_copies = models.PositiveIntegerField(default=1)
    available_copies = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.title} ({self.isbn})"


class IssuedBook(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="issued_records")
    user_id = models.CharField(max_length=50)
    issue_date = models.DateField()
    return_date = models.DateField()
    returned = models.BooleanField(default=False)
    fine_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.user_id} - {self.book.title}"