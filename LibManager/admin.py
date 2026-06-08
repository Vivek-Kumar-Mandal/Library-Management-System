from django.contrib import admin
from .models import Book, IssuedBook


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ("isbn", "title", "author", "genre", "total_copies", "available_copies")
    search_fields = ("isbn", "title", "author", "genre")


@admin.register(IssuedBook)
class IssuedBookAdmin(admin.ModelAdmin):
    list_display = ("book", "user_id", "issue_date", "return_date", "returned", "fine_amount")
    list_filter = ("returned", "issue_date", "return_date")
    search_fields = ("user_id", "book__title", "book__isbn")
