import pickle
import os
from datetime import date, timedelta, datetime

# File names for binary storage
BOOK_FILE = "books.dat"
ISSUED_FILE = "issued.dat"
TRANSACTION_FILE = "transactions.dat"

# Library settings
LOAN_DAYS = 14
FINE_PER_DAY = 5


# ---------- FILE HANDLING FUNCTIONS ----------

def load_data(filename):
    """Load records from a binary file."""
    if not os.path.exists(filename):
        return []

    try:
        with open(filename, "rb") as file:
            return pickle.load(file)
    except (EOFError, pickle.UnpicklingError, OSError) as error:
        print("Warning: Could not read", filename, "-", error)
        return []


def save_data(filename, data):
    """Save records to a binary file."""
    try:
        with open(filename, "wb") as file:
            pickle.dump(data, file)
        return True
    except (OSError, pickle.PickleError) as error:
        print("Error saving file:", error)
        return False


# ---------- BOOK MANAGEMENT FUNCTIONS ----------

def add_book():
    """Add a new book to the library."""
    books = load_data(BOOK_FILE)

    book_id = input("Enter Book ID: ").strip()
    if not book_id:
        print("Book ID cannot be empty.")
        return

    for book in books:
        if book["book_id"].lower() == book_id.lower():
            print("Book ID already exists.")
            return

    title = input("Enter book title: ").strip()
    author = input("Enter author name: ").strip()

    if not title or not author:
        print("Title and author cannot be empty.")
        return

    try:
        quantity = int(input("Enter quantity: "))
        if quantity <= 0:
            print("Quantity must be greater than zero.")
            return
    except ValueError:
        print("Please enter a valid whole number.")
        return

    book = {
        "book_id": book_id,
        "title": title,
        "author": author,
        "quantity": quantity
    }

    books.append(book)

    if save_data(BOOK_FILE, books):
        print("Book added successfully!")


def view_books():
    """Display all books in the library."""
    books = load_data(BOOK_FILE)

    if not books:
        print("No books found in the library.")
        return

    print("\\n--- LIBRARY BOOKS ---")
    print("-" * 75)
    print(f"{'Book ID':<12}{'Title':<25}{'Author':<23}{'Quantity':<10}")
    print("-" * 75)

    for book in books:
        print(
            f"{book['book_id']:<12}"
            f"{book['title'][:24]:<25}"
            f"{book['author'][:22]:<23}"
            f"{book['quantity']:<10}"
        )

    print("-" * 75)


def search_books():
    """Search for books by title or author."""
    books = load_data(BOOK_FILE)
    keyword = input("Enter title or author to search: ").strip().lower()

    if not keyword:
        print("Please enter a search term.")
        return

    found = False

    for book in books:
        if (keyword in book["title"].lower()
                or keyword in book["author"].lower()):
            print(
                f"ID: {book['book_id']} | "
                f"Title: {book['title']} | "
                f"Author: {book['author']} | "
                f"Available: {book['quantity']}"
            )
            found = True

    if not found:
        print("No matching books found.")


# ---------- BOOK ISSUE FUNCTION ----------

def issue_book():
    """Issue a book to a student."""
    books = load_data(BOOK_FILE)
    issued = load_data(ISSUED_FILE)
    transactions = load_data(TRANSACTION_FILE)

    book_id = input("Enter Book ID to issue: ").strip()

    selected_book = None

    for book in books:
        if book["book_id"].lower() == book_id.lower():
            selected_book = book
            break

    if selected_book is None:
        print("Book not found.")
        return

    if selected_book["quantity"] <= 0:
        print("Sorry, this book is currently unavailable.")
        return

    student = input("Enter student name: ").strip()
    if not student:
        print("Student name cannot be empty.")
        return

    student_id = input("Enter student ID: ").strip()
    if not student_id:
        print("Student ID cannot be empty.")
        return

    issue_id = datetime.now().strftime("%Y%m%d%H%M%S%f")
    issue_date = date.today()
    due_date = issue_date + timedelta(days=LOAN_DAYS)

    record = {
        "issue_id": issue_id,
        "book_id": selected_book["book_id"],
        "title": selected_book["title"],
        "student": student,
        "student_id": student_id,
        "issue_date": str(issue_date),
        "due_date": str(due_date),
        "return_date": None,
        "fine": 0,
        "status": "Issued"
    }

    selected_book["quantity"] -= 1

    if not save_data(BOOK_FILE, books):
        return

    issued.append(record)

    if not save_data(ISSUED_FILE, issued):
        selected_book["quantity"] += 1
        save_data(BOOK_FILE, books)
        print("Issue cancelled because the issue record could not be saved.")
        return

    transactions.append({
        "issue_id": issue_id,
        "action": "ISSUE",
        "book_id": selected_book["book_id"],
        "title": selected_book["title"],
        "student": student,
        "student_id": student_id,
        "date": str(issue_date),
        "fine": 0
    })

    if not save_data(TRANSACTION_FILE, transactions):
        print("Warning: Transaction history could not be saved.")

    print("\\nBook issued successfully!")
    print("Issue ID:", issue_id)
    print("Student:", student)
    print("Issue date:", issue_date)
    print("Due date:", due_date)
    print("Fine after due date: Rs.", FINE_PER_DAY, "per day")


# ---------- BOOK RETURN FUNCTION ----------

def return_book():
    """Return a book and calculate any late fine."""
    books = load_data(BOOK_FILE)
    issued = load_data(ISSUED_FILE)
    transactions = load_data(TRANSACTION_FILE)

    issue_id = input("Enter Issue ID: ").strip()

    record = None
    for item in issued:
        if item["issue_id"] == issue_id and item["status"] == "Issued":
            record = item
            break

    if record is None:
        print("Active issue record not found.")
        return

    try:
        due_date = date.fromisoformat(record["due_date"])
    except ValueError:
        print("Invalid due date in the issue record.")
        return

    return_date = date.today()
    late_days = max(0, (return_date - due_date).days)
    fine = late_days * FINE_PER_DAY

    selected_book = None
    for book in books:
        if book["book_id"] == record["book_id"]:
            selected_book = book
            break

    if selected_book is None:
        print("Book inventory record is missing. Return cancelled.")
        return

    record["return_date"] = str(return_date)
    record["fine"] = fine
    record["status"] = "Returned"
    selected_book["quantity"] += 1

    if not save_data(BOOK_FILE, books):
        return

    if not save_data(ISSUED_FILE, issued):
        selected_book["quantity"] -= 1
        record["return_date"] = None
        record["fine"] = 0
        record["status"] = "Issued"
        save_data(BOOK_FILE, books)
        print("Return cancelled because the issue record could not be saved.")
        return

    transactions.append({
        "issue_id": issue_id,
        "action": "RETURN",
        "book_id": record["book_id"],
        "title": record["title"],
        "student": record["student"],
        "student_id": record["student_id"],
        "date": str(return_date),
        "fine": fine
    })

    if not save_data(TRANSACTION_FILE, transactions):
        print("Warning: Transaction history could not be saved.")

    print("\\nBook returned successfully!")
    print("Book:", record["title"])
    print("Student:", record["student"])
    print("Due date:", due_date)
    print("Return date:", return_date)
    print("Late days:", late_days)
    print("Fine: Rs.", fine)


# ---------- ISSUED BOOKS FUNCTION ----------

def view_issued_books():
    """Display books that have not yet been returned."""
    issued = load_data(ISSUED_FILE)
    active_records = [
        item for item in issued if item["status"] == "Issued"
    ]

    if not active_records:
        print("No books are currently issued.")
        return

    print("\\n--- CURRENTLY ISSUED BOOKS ---")
    for item in active_records:
        print("-" * 45)
        print("Issue ID:", item["issue_id"])
        print("Book:", item["title"])
        print("Book ID:", item["book_id"])
        print("Student:", item["student"])
        print("Student ID:", item["student_id"])
        print("Issue date:", item["issue_date"])
        print("Due date:", item["due_date"])

    print("-" * 45)


# ---------- TRANSACTION HISTORY FUNCTION ----------

def view_transaction_history():
    """Display all issue and return transactions."""
    transactions = load_data(TRANSACTION_FILE)

    if not transactions:
        print("No transaction history available.")
        return

    print("\\n--- TRANSACTION HISTORY ---")
    for item in transactions:
        print("-" * 45)
        print("Issue ID:", item["issue_id"])
        print("Action:", item["action"])
        print("Book:", item["title"])
        print("Book ID:", item["book_id"])
        print("Student:", item["student"])
        print("Student ID:", item["student_id"])
        print("Date:", item["date"])
        print("Fine: Rs.", item["fine"])

    print("-" * 45)


# ---------- MAIN MENU ----------

def main():
    """Display the menu and execute the selected operation."""
    while True:
        print("\\n===================================")
        print("     LIBRARY MANAGEMENT SYSTEM")
        print("===================================")
        print("1. Add New Book")
        print("2. View All Books")
        print("3. Search Books")
        print("4. Issue Book")
        print("5. Return Book")
        print("6. View Issued Books")
        print("7. View Transaction History")
        print("8. Exit")
        print("===================================")

        try:
            choice = input("Enter your choice (1-8): ").strip()

            if choice == "1":
                add_book()
            elif choice == "2":
                view_books()
            elif choice == "3":
                search_books()
            elif choice == "4":
                issue_book()
            elif choice == "5":
                return_book()
            elif choice == "6":
                view_issued_books()
            elif choice == "7":
                view_transaction_history()
            elif choice == "8":
                print("Thank you for using the Library Management System!")
                break
            else:
                print("Invalid choice. Please enter a number from 1 to 8.")

        except (EOFError, KeyboardInterrupt):
            print("\\nProgram closed.")
            break
        except (OSError, ValueError, KeyError, TypeError) as error:
            print("An error occurred:", error)


if __name__ == "__main__":
    main()
