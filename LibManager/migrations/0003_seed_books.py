from django.db import migrations


BOOKS = [
    ("9780061120084", "To Kill a Mockingbird", "Harper Lee", "Classic Fiction", 6),
    ("9780451524935", "1984", "George Orwell", "Dystopian", 7),
    ("9780141439518", "Pride and Prejudice", "Jane Austen", "Classic Fiction", 5),
    ("9780743273565", "The Great Gatsby", "F. Scott Fitzgerald", "Classic Fiction", 5),
    ("9780316769174", "The Catcher in the Rye", "J. D. Salinger", "Classic Fiction", 4),
    ("9780060085246", "Brave New World", "Aldous Huxley", "Dystopian", 6),
    ("9780547928227", "The Hobbit", "J. R. R. Tolkien", "Fantasy", 8),
    ("9780544003415", "The Fellowship of the Ring", "J. R. R. Tolkien", "Fantasy", 6),
    ("9780439708180", "Harry Potter and the Sorcerer's Stone", "J. K. Rowling", "Fantasy", 9),
    ("9780439064873", "Harry Potter and the Chamber of Secrets", "J. K. Rowling", "Fantasy", 8),
    ("9780062315007", "The Alchemist", "Paulo Coelho", "Literary Fiction", 7),
    ("9780375831003", "The Book Thief", "Markus Zusak", "Historical Fiction", 6),
    ("9781594891549", "The Kite Runner", "Khaled Hosseini", "Literary Fiction", 6),
    ("9780061206993", "A Thousand Splendid Suns", "Khaled Hosseini", "Literary Fiction", 6),
    ("9780151008116", "Life of Pi", "Yann Martel", "Adventure", 5),
    ("9780439023481", "The Hunger Games", "Suzanne Collins", "Dystopian", 7),
    ("9780439023498", "Catching Fire", "Suzanne Collins", "Dystopian", 6),
    ("9780439023511", "Mockingjay", "Suzanne Collins", "Dystopian", 6),
    ("9780307474278", "The Da Vinci Code", "Dan Brown", "Thriller", 7),
    ("9780307474292", "Angels and Demons", "Dan Brown", "Thriller", 6),
    ("9780307269935", "The Girl with the Dragon Tattoo", "Stieg Larsson", "Crime", 5),
    ("9780393335681", "Gone Girl", "Gillian Flynn", "Thriller", 5),
    ("9780062661081", "The Silent Patient", "Alex Michaelides", "Thriller", 6),
    ("9780062316097", "Sapiens", "Yuval Noah Harari", "Non-Fiction", 8),
    ("9780062455710", "Homo Deus", "Yuval Noah Harari", "Non-Fiction", 7),
    ("9780735211292", "Atomic Habits", "James Clear", "Self-Help", 9),
    ("9780345540522", "Deep Work", "Cal Newport", "Self-Help", 7),
    ("9780812981605", "The Power of Habit", "Charles Duhigg", "Self-Help", 7),
    ("9780374533557", "Thinking, Fast and Slow", "Daniel Kahneman", "Psychology", 6),
    ("9780857197689", "The Psychology of Money", "Morgan Housel", "Finance", 8),
    ("9780887307288", "Rich Dad Poor Dad", "Robert T. Kiyosaki", "Finance", 8),
    ("9780132350884", "Clean Code", "Robert C. Martin", "Computer Science", 7),
    ("9780201616224", "The Pragmatic Programmer", "Andrew Hunt", "Computer Science", 6),
    ("9780262033848", "Introduction to Algorithms", "Thomas H. Cormen", "Computer Science", 5),
    ("9780201633610", "Design Patterns", "Erich Gamma", "Computer Science", 5),
    ("9781593275099", "Python Crash Course", "Eric Matthes", "Computer Science", 8),
    ("9781491946008", "Fluent Python", "Luciano Ramalho", "Computer Science", 5),
    ("9780136681304", "Computer Networking: A Top-Down Approach", "James F. Kurose", "Computer Science", 5),
    ("9780470128725", "Operating System Concepts", "Abraham Silberschatz", "Computer Science", 4),
    ("9780078022159", "Database System Concepts", "Abraham Silberschatz", "Computer Science", 5),
    ("9780307887894", "The Lean Startup", "Eric Ries", "Business", 6),
    ("9780804139298", "Zero to One", "Peter Thiel", "Business", 6),
    ("9781591844501", "Start With Why", "Simon Sinek", "Business", 6),
    ("9780743269513", "The 7 Habits of Highly Effective People", "Stephen R. Covey", "Self-Help", 7),
    ("9780143130727", "Ikigai", "Hector Garcia", "Self-Help", 7),
    ("9780807014271", "Man's Search for Meaning", "Viktor E. Frankl", "Psychology", 5),
    ("9780375520716", "The Immortal Life of Henrietta Lacks", "Rebecca Skloot", "Biography", 5),
    ("9780316489980", "Long Walk to Freedom", "Nelson Mandela", "Biography", 5),
    ("9780399590504", "Educated", "Tara Westover", "Memoir", 6),
    ("9780553418029", "The Martian", "Andy Weir", "Science Fiction", 7),
]


def seed_books(apps, schema_editor):
    Book = apps.get_model("LibManager", "Book")
    Book.objects.all().delete()
    Book.objects.bulk_create(
        [
            Book(
                isbn=isbn,
                title=title,
                author=author,
                genre=genre,
                total_copies=copies,
                available_copies=copies,
            )
            for isbn, title, author, genre, copies in BOOKS
        ]
    )


class Migration(migrations.Migration):
    dependencies = [
        ("LibManager", "0002_upgrade_models"),
    ]

    operations = [
        migrations.RunPython(seed_books, migrations.RunPython.noop),
    ]
