import mysql.connector
import re
import datetime

try:
    # Try to connect to the database
    mydb = mysql.connector.connect(
        host = "localhost",
        user = "root",
        password = "Abdul20012002!",
        database = "book_store1"
    )

    if mydb.is_connected():
        print("You are now connected to the database")
except mysql.connector.Error as error:
        print("Your given credentials are wrong, please enter down below", error)
        # If theyre wrong, you input new credentials
        try:
            host = input("Enter the host: ")
            user = input("Enter the username: ")
            password = input("Enter the password: ")
            database = input("Enter the database name: ")
            # Try to connect to the database again with new credentials
            mydb = mysql.connector.connect(
                host=host,
                user=user,
                password=password,
                database=database
            )
            if mydb.is_connected():
                print("You are now connected to the database")
        except mysql.connector.Error:
            print("Connection error, credentials are incorrect. Try again.")
            exit()

# An object for the user's cart
userCart = {"userid": 0, "isbn": 0, "qty": 0}

# An object for the user with its values

user = {"fname": "", "lname": "", "address": "", "city": "", "state": "", "zip":  0, "phone": 0, "email": "", "userid": 0, "password": "", "creditcardtype": "", "creditcardnumber": 0}


def member_registration():
  cursor = mydb.cursor()

  filter_email = "^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$"
  filter_number = "^[0-9]+$"
  filter_zip = "^[0-9]{5}$"

  fname = input("Enter your first name: ")
  lname = input("Enter your last name: ")
  address = input("Enter your address: ")
  city = input("Enter your city: ")
  state = input("Enter your state: ")
  zip_code = input("Enter your Zip Code: ")
  phonenumber = input("Enter your phone number: ")
  email = input("Enter your email address: ")
  password = input("Enter your password: ")

  # A bunch of if statements to check if the values are correct.
  if fname.isalpha() == False:
    print("Invalid name, Please enter a name with alphabetic characters only")
    return
  if lname.isalpha() == False:
      print("Invalid name, Please enter a name with alphabetic characters only")
      return
  if address == None:
      print("Invalid address, enter a valid address")
      return
  if city.isalpha() == False:
      print("Invalid name, please enter with alphabetic characters only")
      return
  if state.isalpha() == False:
      print("Invalid name, please enter with alphabetic characters only")
      return
  if re.match(filter_zip, zip_code) == False:
      print("Invalid zip, please enter a 5 digit zip code")
      return
  if re.match(filter_number, phonenumber) == False:
      print("Please enter a valid phone number with digits only.")
      return
  if re.match(filter_email, email) == False:
      print("Please enter a valid email address")

  # Checking if the email (The key attribute of the user) Is used by another user AND inputing all values into the new member.
  try:
      cursor.execute("INSERT INTO MEMBERS (fname, lname, address, city, state, zip, phone, email, password) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)", (fname, lname, address, city, state, zip_code, phonenumber, email, password))
      mydb.commit()
      print("You have been registered to the system.")
  except mysql.connector.Error as error:
      print("Something went wrong, try again:", error)
      mydb.rollback()
      return


def login_member(user):
  # Ask the user for their login details.
  email = input("Enter your email please: ")
  password = input("Enter your password please: ")

  #Keys for the user
  keys = ['fname', 'lname', 'address', 'city', 'state', 'zip', 'phone', 'email', 'userid', 'password', 'creditcardtype', 'creditcardnumber']

  try:
      # Connect to the database to execute queries
      with mydb.cursor() as cursor:
          cursor.execute("SELECT * FROM members WHERE email=%s", (email,))
          result = cursor.fetchone()
      if result == None:
          print("Invalid login, try again")
      else:
          # if the inputted password = the user's password, run this.
          pwd = result[9]
          if password == pwd:
               # Override user dictionary with data from the database
                for i in range(len(keys)):
                    user[keys[i]] = result[i]
                print("Login successful!\n")
                while True:
                    print("******************************************************")
                    print("***")
                    print("***       Welcome to the online book store ")
                    print("***")
                    print("******************************************************")
                    print("1- Browse by subject")
                    print("2- Search by Authro/Title")
                    print("3- Check out")
                    print("4- logout")
                    choice = input("Type in your option: ")

                    if choice == "1":
                        browse_by_subject()
                    elif choice == "2":
                        search_by_author_or_title()
                    elif choice == "3":
                        check_out()
                    if choice == "4":
                        userCart.clear()
                        user.clear()
                        return
                    else:
                        print("Invalid, Please try again.")
  except mysql.connector.Error as e:
      print("Error connecting to the database", e)
      return


def browse_by_subject():
    try:
        cursor = mydb.cursor()
        cursor.execute("SELECT DISTINCT subject FROM books ORDER BY subject ASC")
        results = cursor.fetchall()
        for result in results:
            print(result[0])

        print("Type the subject you want to browse, or press ENTER to return to the menu.\n")
        subject = input("Subject: ").upper()
        if subject is not None:
            # Use parameterized queries to prevent SQL injection attacks

            cursor.execute("SELECT * FROM books WHERE subject=%s ORDER BY title", (subject,))
            results = cursor.fetchall()
            PAGE_SIZE = 3
            num_pages = len(results) // PAGE_SIZE + 1
            page_num = 1
            while True:
                start_index = (page_num - 1) * PAGE_SIZE
                end_index = start_index + PAGE_SIZE
                current_page = results[start_index:end_index]
                for book in current_page:
                    print(f"""Author: {book[1]}\nTitle: {book[2]}\nISBN: {book[0]}\nPrice: ({book[3]})\nSubject: {book[4]}\n""")
                if len(results) > PAGE_SIZE:
                    print(f"Page {page_num} of {num_pages}\n")

                choice = input("Type (n) for next page, (p) for previous page, or press (enter) to add to cart or (q) return to the menu: ")
                if choice == 'n':
                    if page_num < num_pages:
                        page_num += 1
                elif choice == 'p':
                    if page_num > 1:
                        page_num -= 1
                elif choice == 'q':
                    break
                else:
                    print("Type the ISBN of the book you want to add to your cart, or press ENTER to continue browsing.")
                    isbn = input("ISBN: ")
                    if isbn:
                        cursor.execute("SELECT * FROM books WHERE isbn=%s", (isbn,))
                        book = cursor.fetchone()
                        if book:
                            qty = input("Enter quantity: ")
                            if qty.isdigit() and int(qty) > 0:
                                userCart["userid"] = user["userid"]
                                userCart["isbn"] = book[0]
                                userCart["qty"] = qty
                                cursor.execute("INSERT INTO cart (userid, isbn, qty) VALUES (%s, %s, %s)", (userCart["userid"], userCart["isbn"], userCart["qty"]))
                                mydb.commit()
                                print(f"{qty} of {book[1]} have been added to your cart.")
                        else:
                            print("Invalid ISBN.")
    except mysql.connector.Error as err:
        print(f"Error: {err}")

#Function that lets the user search by the author or by the title

def search_by_author_or_title():
    cursor = mydb.cursor()
    while True:
        print("***")
        print("***       Search by Author/Title")
        print("***")
        print("1- Author Search")
        print("2- Title Search")
        print("3- Go Back to Main Menu")
        choice = input("Type in your option: ")
        if choice == "1":
            author = input("Enter author's name or a part of it: ")
            cursor.execute("SELECT * FROM books WHERE author LIKE %s", (f"%{author}%",))
            results = cursor.fetchall()
            PAGE_SIZE = 3  # number of books per page
            num_pages = len(results) // PAGE_SIZE + 1
            page_num = 1
            while True:
                start_index = (page_num - 1) * PAGE_SIZE
                end_index = start_index + PAGE_SIZE
                current_page = results[start_index:end_index]
                for book in current_page:
                    print(f"""Author: {book[1]}\nTitle: {book[2]}\nISBN: {book[0]}\nPrice: ({book[3]})\nSubject: {book[4]}\n""")
                if len(results) > PAGE_SIZE:
                    print(f"Page {page_num} of {num_pages}\n")
                choice = input("Type 'n' for next page, 'p' for previous page, or press enter to add to cart or q return to the main menu: ")
                if choice == 'n':
                    if page_num < num_pages:
                        page_num += 1
                elif choice == 'p':
                    if page_num > 1:
                        page_num -= 1
                elif choice == 'q':
                    break
                else:
                    
                    #Searches for the book by the isbn or just browsing

                    print("Type the ISBN of the book you want to add to your cart, or press ENTER to continue browsing.")
                    isbn = input("ISBN: ")
                    if isbn:
                        cursor.execute("SELECT * FROM books WHERE isbn=%s", (isbn,))
                        book = cursor.fetchone()
                        if book:
                            qty = input("Enter quantity: ")
                            if qty.isdigit() and int(qty) > 0:
                                userCart["userid"] = user["userid"]
                                userCart["isbn"] = book[0]
                                userCart["qty"] = qty
                                cursor.execute("INSERT INTO cart (userid, isbn, qty) VALUES (%s, %s, %s)", (userCart["userid"], userCart["isbn"], userCart["qty"]))
                                mydb.commit()
                                print(f"{qty} of {book[1]} have been added to your cart.")
                        else:
                            print("Invalid ISBN.")

        # Searching for a book by the title
        elif choice == "2":
            title = input("Enter book title or a part of it: ")
            cursor.execute("SELECT * FROM books WHERE title LIKE %s", (f"%{title}%",))
            results = cursor.fetchall()
            PAGE_SIZE = 3 # how many books per page 
            num_pages = len(results) // PAGE_SIZE + 1
            page_num = 1
            while True:
                start_index = (page_num - 1) * PAGE_SIZE
                end_index = start_index + PAGE_SIZE
                current_page = results[start_index:end_index]
                for book in current_page:
                    print(f"""Author: {book[1]}\nTitle: {book[2]}\nISBN: {book[0]}\nPrice: ({book[3]})\nSubject: {book[4]}\n""")
                if len(results) > PAGE_SIZE:
                    print(f"Page {page_num} of {num_pages}\n")

                choice = input("Type 'n' for next page, 'p' for previous page, or press enter to add to cart or q return to the main menu: ")
                if choice == 'n':
                    if page_num < num_pages:
                        page_num += 1
                elif choice == 'p':
                    if page_num > 1:
                        page_num -= 1
                elif choice == 'q':
                    break
                else:
                    print("Type the ISBN of the book you want to add to your cart, or press ENTER to continue browsing.")
                    isbn = input("ISBN: ")
                    if isbn:
                        cursor.execute("SELECT * FROM books WHERE isbn=%s", (isbn,))
                        book = cursor.fetchone()
                        if book:
                            qty = input("Enter quantity: ")
                            if qty.isdigit() and int(qty) > 0:
                                userCart["userid"] = user["userid"]
                                userCart["isbn"] = book[0]
                                userCart["qty"] = qty
                                cursor.execute("INSERT INTO cart (userid, isbn, qty) VALUES (%s, %s, %s)", (userCart["userid"], userCart["isbn"], userCart["qty"]))
                                mydb.commit()
                                print(f"{qty} of {book[1]} have been added to your cart.")
                        else:
                            print("Invalid ISBN.")
        elif choice == "3":
            return


def check_out():
    cursor = mydb.cursor()

    # Display cart contents
    cursor.execute("SELECT books.isbn, books.title, books.price, cart.qty FROM books INNER JOIN cart ON books.isbn=cart.isbn WHERE cart.userid=%s", (user["userid"],))
    results = cursor.fetchall()
    total_price = 0

    print("\n\t\t\tInvoice for Order no." + str(cursor.lastrowid))
    print("Shipping Address: \t\t\t\t Billing Address:")
    print(f"Name: {user['fname']} {user['lname']} \t\t\t\t Name: {user['fname']} {user['lname']}")
    print(f"Address: {user['address']} \t\t\t\t Address: {user['address']}")
    print(f"\t{user['city']}, {user['state']} {user['zip']} \t\t\t  {user['city']}, {user['state']} {user['zip']}")
    print("------------------------------------------------------------------")
    print("ISBN\t\tTitle\t\t\t\t\tPrice\tQty\tTotal")
    print("------------------------------------------------------------------")

    for row in results:
        book_isbn = row[0]
        book_title = row[1]
        book_price = row[2]
        qty = row[3]
        print(f"{book_isbn}\t{book_title[:40]:40s}\t{book_price}\t{qty}\t{book_price*qty}")
        total_price += book_price*qty

    print("------------------------------------------------------------------")
    print(f"Total = {total_price}\n")

    # Use user's current address for shipping
    shipping_address = user["address"]
    shipping_city = user["city"]
    shipping_state = user["state"]
    shipping_zip = user["zip"]

    # Display estimated delivery date
    today = datetime.datetime.now()
    estimated_delivery_date = today + datetime.timedelta(days=7)
    print(f"Estimated Delivery Date: {estimated_delivery_date.strftime('%A, %B %d, %Y')}\n")

    # Confirm checkout
    confirm_checkout = input("Proceed to checkout? (Y/N) ")
    if confirm_checkout.lower() == "y":
        # Save the order to the Order table
        cursor.execute("INSERT INTO orders (userid, received, shipAddress, shipCity, shipState, shipZip) VALUES (%s, %s, %s, %s, %s, %s)", (user["userid"], today, shipping_address, shipping_city, shipping_state, shipping_zip))
        mydb.commit()

        # Get the order ID of the newly inserted order
        order_id = cursor.lastrowid

        # Save order details to 'odetails' table
        for row in results:
            book_isbn = row[0]
            qty = row[3]
            book_price = row[2]
            cursor.execute("INSERT INTO odetails (ono, isbn, qty, price) VALUES (%s, %s, %s, %s)", (order_id, book_isbn, qty, book_price))
            mydb.commit()

        # Clear cart wasn't sure if we drop db cart or lcl or both so i
        # commented out the db one
        # cursor.execute("DELETE FROM cart WHERE userid=%s", (user["userid"],))
        userCart.clear()

        print("\n\nYour order has been processed. Thank you for shopping with us!")
    else:
        print("\n\nYour order has been canceled.")



def main():
    while True:
        print("**********************************************************************")
        print("***")
        print("***       Welcome to the online book store ")
        print("***")
        print("**********************************************************************")
        print("1- Member Login")
        print("2- New Member Registration")
        print("3- Quit")
        choice = input("Type in your option: ")

        if choice == "1":
            login_member(user)
        if choice == "2":
            member_registration()
        elif choice == "3":
            mydb.close()
            user.clear()
            exit()
        else:
            print("Invalid choice. Please try again.")


# call the main function to start the program
main()
