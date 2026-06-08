from datetime import timedelta
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.hashers import check_password, make_password
from django.conf import settings
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .models import Book, IssuedBook, User

SESSION_ADMIN_KEY = "is_admin"
SESSION_USER_KEY = "user_id"
OVERDUE_FINE_PER_DAY = Decimal("50.00")


def is_admin(request):
    return bool(request.session.get(SESSION_ADMIN_KEY))


def is_user(request):
    return bool(request.session.get(SESSION_USER_KEY))


def get_user_id(request):
    return request.session.get(SESSION_USER_KEY)


def require_admin(request):
    if not is_admin(request):
        messages.error(request, "Please login as admin to access this page.")
        return False
    return True


def require_user(request):
    if not is_user(request):
        messages.error(request, "Please login to access this page.")
        return False
    return True


def index(request):
    """Home page with dual login sections"""
    if is_admin(request):
        return redirect("home")
    if is_user(request):
        return redirect("home")
    return render(request, "index.html")


def home(request):
    """Books listing - requires login (user or admin)"""
    if not is_admin(request) and not is_user(request):
        messages.error(request, "Please login to view books.")
        return redirect("index")
    
    books = Book.objects.order_by("title")
    context = {
        "books": books,
        "is_admin": is_admin(request),
        "is_user": is_user(request),
        "user_id": get_user_id(request),
    }
    return render(request, "books.html", context)


def admin_login(request):
    """Admin login view"""
    if is_admin(request):
        return redirect("home")
    if is_user(request):
        messages.error(request, "Please logout from user account first.")
        return redirect("home")
    
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        if username == settings.ADMIN_USERNAME and check_password(password, settings.ADMIN_PASSWORD_HASH):
            request.session[SESSION_ADMIN_KEY] = True
            messages.success(request, "Logged in as admin.")
            return redirect("home")
        messages.error(request, "Invalid username or password.")
    return render(request, "admin_login.html")


def user_login(request):
    """User login view"""
    if is_user(request):
        return redirect("home")
    if is_admin(request):
        messages.error(request, "Please logout from admin account first.")
        return redirect("home")
    
    if request.method == "POST":
        user_id = request.POST.get("user_id", "").strip()
        password = request.POST.get("password", "")
        
        if not user_id or not password:
            messages.error(request, "User ID and password are required.")
            return render(request, "user_login.html")
        
        try:
            user = User.objects.get(user_id=user_id)
            if check_password(password, user.password_hash):
                request.session[SESSION_USER_KEY] = user_id
                messages.success(request, f"Welcome, {user.name or user_id}!")
                return redirect("home")
            else:
                messages.error(request, "Invalid user ID or password.")
        except User.DoesNotExist:
            messages.error(request, "Invalid user ID or password.")
    
    return render(request, "user_login.html")


def login_view(request):
    """Redirect to index for dual login"""
    return redirect("index")


def logout_view(request):
    request.session.pop(SESSION_ADMIN_KEY, None)
    request.session.pop(SESSION_USER_KEY, None)
    messages.success(request, "Logged out successfully.")
    return redirect("index")


def add_book(request):
    if not require_admin(request):
        return redirect("admin_login")
    if request.method == "POST":
        title = request.POST.get("title", "").strip()
        author = request.POST.get("author", "").strip()
        genre = request.POST.get("genre", "").strip()
        isbn = request.POST.get("isbn", "").strip().upper()
        total_copies_raw = request.POST.get("total_copies", "").strip()

        if not all([title, author, genre, isbn, total_copies_raw]):
            messages.error(request, "All fields are required.")
            return redirect("add_book")
        if not (isbn.startswith("LIB") and isbn[3:].isdigit()):
            messages.error(request, "ISBN must use format like LIB001.")
            return redirect("add_book")
        if Book.objects.filter(isbn=isbn).exists():
            messages.error(request, "A book with this ISBN already exists.")
            return redirect("add_book")
        try:
            total_copies = int(total_copies_raw)
            if total_copies < 1:
                raise ValueError
        except ValueError:
            messages.error(request, "Total copies must be a positive number.")
            return redirect("add_book")

        Book.objects.create(
            title=title,
            author=author,
            genre=genre,
            isbn=isbn,
            total_copies=total_copies,
            available_copies=total_copies,
        )
        messages.success(request, "Book added successfully.")
        return redirect("home")
    return render(request, "add_book.html", {"is_admin": is_admin(request)})


def delete_book(request, book_id):
    if request.method != "POST":
        return redirect("home")
    if not require_admin(request):
        return redirect("admin_login")
    book = get_object_or_404(Book, pk=book_id)
    if IssuedBook.objects.filter(book=book, returned=False).exists():
        messages.error(request, "Cannot delete a book that is currently issued.")
        return redirect("home")
    book.delete()
    messages.success(request, "Book deleted successfully.")
    return redirect("home")


def issue_book(request):
    if not require_admin(request):
        return redirect("admin_login")
    books = Book.objects.filter(available_copies__gt=0).order_by("title")
    selected_book = None
    selected_id = request.GET.get("book_id") or request.POST.get("book_id")
    if selected_id:
        selected_book = Book.objects.filter(id=selected_id).first()

    if request.method == "POST":
        user_id = request.POST.get("user_id", "").strip()
        days_raw = request.POST.get("duration_days", "").strip()
        if not selected_book:
            messages.error(request, "Please select a book to issue.")
            return redirect("issue_book")
        if not user_id:
            messages.error(request, "User ID is required.")
            return redirect(f"{request.path}?book_id={selected_book.id}")
        try:
            duration_days = int(days_raw)
            if duration_days < 1:
                raise ValueError
        except ValueError:
            messages.error(request, "Issue duration must be a positive number of days.")
            return redirect(f"{request.path}?book_id={selected_book.id}")

        with transaction.atomic():
            book = Book.objects.select_for_update().get(id=selected_book.id)
            if book.available_copies <= 0:
                messages.error(request, "This book is currently out of stock.")
                return redirect("issue_book")
            issue_date = timezone.localdate()
            return_date = issue_date + timedelta(days=duration_days)
            IssuedBook.objects.create(
                book=book,
                user_id=user_id,
                issue_date=issue_date,
                return_date=return_date,
                returned=False,
                fine_amount=Decimal("0.00"),
            )
            book.available_copies -= 1
            book.save(update_fields=["available_copies"])

        messages.success(request, f"Book issued successfully to {user_id}.")
        return redirect("home")

    return render(
        request,
        "issue_book.html",
        {"books": books, "selected_book": selected_book, "is_admin": is_admin(request)},
    )


def return_book(request):
    if not require_admin(request):
        return redirect("admin_login")
    user_id = request.GET.get("user_id", "").strip()
    records = []
    if user_id:
        records = IssuedBook.objects.select_related("book").filter(
            user_id__iexact=user_id,
            returned=False,
        )

    if request.method == "POST":
        record_id = request.POST.get("record_id", "").strip()
        record = get_object_or_404(IssuedBook.objects.select_related("book"), id=record_id, returned=False)
        today = timezone.localdate()
        overdue_days = max(0, (today - record.return_date).days)
        fine = (OVERDUE_FINE_PER_DAY * Decimal(overdue_days)).quantize(Decimal("0.00"))

        with transaction.atomic():
            locked_record = IssuedBook.objects.select_for_update().select_related("book").get(id=record.id)
            if locked_record.returned:
                messages.error(request, "This issue record is already returned.")
                return redirect("return_book")
            locked_record.returned = True
            locked_record.fine_amount = fine
            locked_record.save(update_fields=["returned", "fine_amount"])

            book = Book.objects.select_for_update().get(id=locked_record.book_id)
            book.available_copies = min(book.total_copies, book.available_copies + 1)
            book.save(update_fields=["available_copies"])

        if fine > 0:
            messages.success(request, f"Book returned. Overdue fine: ₹{fine}.")
        else:
            messages.success(request, "Book returned successfully with no fine.")
        return redirect(f"{request.path}?user_id={locked_record.user_id}")

    return render(
        request,
        "return_book.html",
        {"records": records, "user_id": user_id, "is_admin": is_admin(request)},
    )


def issued_books(request):
    if not require_admin(request):
        return redirect("admin_login")
    records = IssuedBook.objects.select_related("book").order_by("-issue_date", "-id")
    return render(request, "issued_books.html", {"records": records, "is_admin": is_admin(request)})


def user_dashboard(request):
    """User's dashboard to view their issued books"""
    if not require_user(request):
        return redirect("user_login")
    
    user_id = get_user_id(request)
    try:
        user = User.objects.get(user_id=user_id)
    except User.DoesNotExist:
        messages.error(request, "User not found.")
        return redirect("logout")
    
    # Get books issued to this user
    issued_records = IssuedBook.objects.select_related("book").filter(
        user_id=user_id,
        returned=False
    ).order_by("-issue_date")
    
    # Get returned books for this user
    returned_records = IssuedBook.objects.select_related("book").filter(
        user_id=user_id,
        returned=True
    ).order_by("-issue_date")
    
    context = {
        "user": user,
        "issued_records": issued_records,
        "returned_records": returned_records,
        "is_user": True,
        "user_id": user_id,
    }
    return render(request, "user_dashboard.html", context)



def add_book(request):
    if not require_admin(request):
        return redirect("login")
    if request.method == "POST":
        title = request.POST.get("title", "").strip()
        author = request.POST.get("author", "").strip()
        genre = request.POST.get("genre", "").strip()
        isbn = request.POST.get("isbn", "").strip().upper()
        total_copies_raw = request.POST.get("total_copies", "").strip()

        if not all([title, author, genre, isbn, total_copies_raw]):
            messages.error(request, "All fields are required.")
            return redirect("add_book")
        if not (isbn.startswith("LIB") and isbn[3:].isdigit()):
            messages.error(request, "ISBN must use format like LIB001.")
            return redirect("add_book")
        if Book.objects.filter(isbn=isbn).exists():
            messages.error(request, "A book with this ISBN already exists.")
            return redirect("add_book")
        try:
            total_copies = int(total_copies_raw)
            if total_copies < 1:
                raise ValueError
        except ValueError:
            messages.error(request, "Total copies must be a positive number.")
            return redirect("add_book")

        Book.objects.create(
            title=title,
            author=author,
            genre=genre,
            isbn=isbn,
            total_copies=total_copies,
            available_copies=total_copies,
        )
        messages.success(request, "Book added successfully.")
        return redirect("home")
    return render(request, "add_book.html", {"is_admin": is_admin(request)})


def delete_book(request, book_id):
    if request.method != "POST":
        return redirect("home")
    if not require_admin(request):
        return redirect("login")
    book = get_object_or_404(Book, pk=book_id)
    if IssuedBook.objects.filter(book=book, returned=False).exists():
        messages.error(request, "Cannot delete a book that is currently issued.")
        return redirect("home")
    book.delete()
    messages.success(request, "Book deleted successfully.")
    return redirect("home")


def issue_book(request):
    if not require_admin(request):
        return redirect("login")
    books = Book.objects.filter(available_copies__gt=0).order_by("title")
    selected_book = None
    selected_id = request.GET.get("book_id") or request.POST.get("book_id")
    if selected_id:
        selected_book = Book.objects.filter(id=selected_id).first()

    if request.method == "POST":
        user_id = request.POST.get("user_id", "").strip()
        days_raw = request.POST.get("duration_days", "").strip()
        if not selected_book:
            messages.error(request, "Please select a book to issue.")
            return redirect("issue_book")
        if not user_id:
            messages.error(request, "User ID is required.")
            return redirect(f"{request.path}?book_id={selected_book.id}")
        try:
            duration_days = int(days_raw)
            if duration_days < 1:
                raise ValueError
        except ValueError:
            messages.error(request, "Issue duration must be a positive number of days.")
            return redirect(f"{request.path}?book_id={selected_book.id}")

        with transaction.atomic():
            book = Book.objects.select_for_update().get(id=selected_book.id)
            if book.available_copies <= 0:
                messages.error(request, "This book is currently out of stock.")
                return redirect("issue_book")
            issue_date = timezone.localdate()
            return_date = issue_date + timedelta(days=duration_days)
            IssuedBook.objects.create(
                book=book,
                user_id=user_id,
                issue_date=issue_date,
                return_date=return_date,
                returned=False,
                fine_amount=Decimal("0.00"),
            )
            book.available_copies -= 1
            book.save(update_fields=["available_copies"])

        messages.success(request, f"Book issued successfully to {user_id}.")
        return redirect("home")

    return render(
        request,
        "issue_book.html",
        {"books": books, "selected_book": selected_book, "is_admin": is_admin(request)},
    )


def return_book(request):
    if not require_admin(request):
        return redirect("login")
    user_id = request.GET.get("user_id", "").strip()
    records = []
    if user_id:
        records = IssuedBook.objects.select_related("book").filter(
            user_id__iexact=user_id,
            returned=False,
        )

    if request.method == "POST":
        record_id = request.POST.get("record_id", "").strip()
        record = get_object_or_404(IssuedBook.objects.select_related("book"), id=record_id, returned=False)
        today = timezone.localdate()
        overdue_days = max(0, (today - record.return_date).days)
        fine = (OVERDUE_FINE_PER_DAY * Decimal(overdue_days)).quantize(Decimal("0.00"))

        with transaction.atomic():
            locked_record = IssuedBook.objects.select_for_update().select_related("book").get(id=record.id)
            if locked_record.returned:
                messages.error(request, "This issue record is already returned.")
                return redirect("return_book")
            locked_record.returned = True
            locked_record.fine_amount = fine
            locked_record.save(update_fields=["returned", "fine_amount"])

            book = Book.objects.select_for_update().get(id=locked_record.book_id)
            book.available_copies = min(book.total_copies, book.available_copies + 1)
            book.save(update_fields=["available_copies"])

        if fine > 0:
            messages.success(request, f"Book returned. Overdue fine: ₹{fine}.")
        else:
            messages.success(request, "Book returned successfully with no fine.")
        return redirect(f"{request.path}?user_id={locked_record.user_id}")

    return render(
        request,
        "return_book.html",
        {"records": records, "user_id": user_id, "is_admin": is_admin(request)},
    )


def issued_books(request):
    if not require_admin(request):
        return redirect("login")
    records = IssuedBook.objects.select_related("book").order_by("-issue_date", "-id")
    return render(request, "issued_books.html", {"records": records, "is_admin": is_admin(request)})

  