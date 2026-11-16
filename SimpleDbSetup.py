import sqlite3
from pathlib import Path
import tkinter as tk
from tkinter import messagebox

# Although this is quite jank, I was bored at 1am and havent touched python in about a year, please forgive me.

LocationCache = [] # General Cache for the wipe
conn = None  # the live connection for this run


def Setup():
    global conn
    folder = Path(__file__).parent  # Parent is assumed as root during setup, Root is not touched

    db_path = folder / "mydata.db"  # Set path
    conn = sqlite3.connect(db_path)  # Connect DB
    LocationCache.append(db_path)  # Cache DB for later purge
    LocationCache.append(Path(__file__))  # Cache the script itself for later purge
    conn.execute("CREATE TABLE IF NOT EXISTS items (id INTEGER PRIMARY KEY, title TEXT NOT NULL CHECK (title <> ''), author TEXT NOT NULL CHECK (author <> ''), year INTEGER)")
    conn.commit()  # Set up very basic DB For a book catalogue with a Unique ID, Non null author and name, but nullable year.


def Cleanup():
    # Purge everything we cached (db + script). Close sql first so the file isn't locked.
    if conn is not None: # Check if connection, if so, close it
        conn.close() 
    for path in LocationCache: # For all whos paths exist, set path to nil / delete
        try:
            if path.exists():
                path.unlink()
        except OSError:
            pass

# CRUD

def read_books(): # Returns all book tables
    return conn.execute("SELECT id, title, author, year FROM items ORDER BY id").fetchall()

def create_book(title, author, year): # Creates book with placed in values
    conn.execute("INSERT INTO items (title, author, year) VALUES (?, ?, ?)", (title, author, year))
    conn.commit() # Instantly commit for safety, repeats on other 3

def update_book(book_id, title, author, year): # Update others where id = same
    conn.execute("UPDATE items SET title = ?, author = ?, year = ? WHERE id = ?", (title, author, year, book_id))
    conn.commit()

def delete_book(book_id): # Delete based off id
    conn.execute("DELETE FROM items WHERE id = ?", (book_id,))
    conn.commit()

# UI

def build_ui():
    root = tk.Tk() # Set up handler for ui
    root.title("Book Catalogue") # Tutke
    root.geometry("420x420") # Size

    listbox = tk.Listbox(root, width=70) # List and info
    listbox.pack(padx=10, pady=10, fill="both", expand=True)

    form = tk.Frame(root)
    form.pack(padx=10, fill="x") # General Form data
    tk.Label(form, text="Title").grid(row=0, column=0, sticky="w")
    tk.Label(form, text="Author").grid(row=1, column=0, sticky="w")
    tk.Label(form, text="Year").grid(row=2, column=0, sticky="w")

    title_var = tk.StringVar()
    author_var = tk.StringVar() # Set entries
    year_var = tk.StringVar()
    tk.Entry(form, textvariable=title_var, width=40).grid(row=0, column=1, pady=2)
    tk.Entry(form, textvariable=author_var, width=40).grid(row=1, column=1, pady=2)
    tk.Entry(form, textvariable=year_var, width=40).grid(row=2, column=1, pady=2)

    rows = []  # keeps book records aligned with listbox lines

    def refresh(): 
        rows.clear()
        listbox.delete(0, tk.END) # Delete all in py cache
        for book in read_books():
            rows.append(book) # Set new row of book
            bid, title, author, year = book # Set vars for text insert
            listbox.insert(tk.END, f"[{bid}] {title} — Author: {author} (Year {year if year is not None else '—'})")

    def selected_id():
        sel = listbox.curselection() # Check current selected item
        return rows[sel[0]][0] if sel else None # Return OUR item ID if item found selected

    def parse_year():
        text = year_var.get().strip() # simplify
        if text == "":
            return None  # year is nullable
        if not text.isdigit(): # Error if not int
            messagebox.showerror("Invalid year", "Year must be a number (or left blank).")
            raise ValueError
        return int(text) # Int

    def on_add():
        try:
            year = parse_year() # Ensure year is a valid year (int or null)
        except ValueError:
            return
        try:
            create_book(title_var.get().strip(), author_var.get().strip(), year) # Attempt to create
        except sqlite3.IntegrityError:
            messagebox.showerror("Missing data", "Title and author are required.") # Return error if missing fields
            return
        refresh() # Refresh because major change

    def on_update():
        bid = selected_id() # Get current id
        if bid is None: # Ensure selection
            messagebox.showinfo("No selection", "Pick a book from the list first.")
            return
        try:
            year = parse_year() # Ensure proper year
        except ValueError:
            return
        try:
            update_book(bid, title_var.get().strip(), author_var.get().strip(), year) # Attempt book update
        except sqlite3.IntegrityError:
            messagebox.showerror("Missing data", "Title and author are required.") # Return visual error
            return
        refresh() # Refresh because of change

    def on_delete(): 
        bid = selected_id() # Get selected's id if selected
        if bid is None:
            messagebox.showinfo("No selection", "Pick a book from the list first.")
            return
        delete_book(bid) # Run delete function, simple
        refresh() # reload everything

    def on_select(_event): # Proper selection event
        sel = listbox.curselection() # Get selection
        if not sel:
            return
        _, title, author, year = rows[sel[0]] # Get all info of selected
        title_var.set(title) # force set vars to match info
        author_var.set(author)
        year_var.set("" if year is None else str(year)) # Handle null or year

    def on_wipe():
        if not messagebox.askyesno("Wipe everything?"):
            return
        Cleanup() # Run the purge function in a sense.
        root.destroy()  # closing after purge; nothing left to save

    listbox.bind("<<ListboxSelect>>", on_select) # Bind listening event for on select

    btns = tk.Frame(root) # Set up updates with proper functions on click
    btns.pack(padx=10, pady=10, fill="x")
    tk.Button(btns, text="Add", width=9, command=on_add).pack(side="left", padx=3)
    tk.Button(btns, text="Update", width=9, command=on_update).pack(side="left", padx=3)
    tk.Button(btns, text="Delete", width=9, command=on_delete).pack(side="left", padx=3)
    tk.Button(btns, text="Refresh", width=9, command=refresh).pack(side="left", padx=3)
    tk.Button(btns, text="Wipe All", width=9, fg="red", command=on_wipe).pack(side="right", padx=3)

    def on_close():
        # Closes sql connection and ui element, keeps db and base
        if conn is not None:
            conn.close()
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_close) # On lack of window existing
    refresh() # Refresh for any finalized populated data appearing
    root.mainloop() # Start the web


Setup() # Init backend
build_ui() # Ui init
