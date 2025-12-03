Book Catalogue Web Application

This project is a web application built with Flask that allows users to maintain a personal book catalogue. Users can search for books by ISBN or title using the Google Books API, view search results, and add selected books to their account. Each book stores the title, author, page count, rating, and a thumbnail image if available. Users can also delete books from their list, and the app provides feedback using Flask flash messages.

The application supports multiple users through a simple registration and login system. Logging in stores the user’s session, and logging out clears it, returning the user to the login page. Two accounts are included for testing: admin/password and test1/test1. Users can also register new accounts to try the app.

The solution works by combining Flask, the Google Books API, and SQLite. Search requests query the API and parse the JSON response. If multiple results are returned, users can select which book to add. Each book is saved in the database with a reference to the user who added it, keeping data separate between accounts.

The database consists of two main tables: users for account information and books for book data. A foreign key links books to their respective users. Flask handles sessions, routing, and feedback messages, while SQLite provides persistent storage. This structure allows the app to support multiple users while keeping the interface simple and intuitive.