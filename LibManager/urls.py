from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("books/", views.home, name="home"),
    path("login/", views.login_view, name="login"),
    path("admin-login/", views.admin_login, name="admin_login"),
    path("user-login/", views.user_login, name="user_login"),
    path("logout/", views.logout_view, name="logout"),
    path("dashboard/", views.user_dashboard, name="user_dashboard"),
    path("add-book/", views.add_book, name="add_book"),
    path("delete-book/<int:book_id>/", views.delete_book, name="delete_book"),
    path("issue-book/", views.issue_book, name="issue_book"),
    path("return-book/", views.return_book, name="return_book"),
    path("issued-books/", views.issued_books, name="issued_books"),
]
