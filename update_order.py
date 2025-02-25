import psycopg2
import argparse

# Database connection parameters
DB_PARAMS = {
    'dbname': 'storedb',
    'user': 'myuser',
    'password': 'mypassword',
    'host': 'localhost',
    'port': 5432
}

# Function to connect to the database
def connect_db():
    return psycopg2.connect(**DB_PARAMS)

# Add an order for a user
def add_order(username, product_name, quantity):
    try:
        conn = connect_db()
        cur = conn.cursor()

        # Get user_id from users table
        cur.execute("SELECT user_id FROM users WHERE email = %s;", (username,))
        user = cur.fetchone()
        if not user:
            print(f"User '{username}' not found.")
            return
        user_id = user[0]

        # Get product_id from products table
        cur.execute("SELECT product_id FROM products WHERE name = %s;", (product_name,))
        product = cur.fetchone()
        if not product:
            print(f"Product '{product_name}' not found.")
            return
        product_id = product[0]

        # Insert order into orders table
        cur.execute(
            "INSERT INTO orders (user_id, product_id, quantity) VALUES (%s, %s, %s);",
            (user_id, product_id, quantity)
        )
        conn.commit()
        print(f"Order placed for {quantity}x '{product_name}' by {username}.")

    except Exception as e:
        print("An error occurred:", e)
        conn.rollback()
    finally:
        cur.close()
        conn.close()

# Show how much each user spent
def show_total_spent():
    try:
        conn = connect_db()
        cur = conn.cursor()
        cur.execute("""
            SELECT u.first_name || ' ' || u.last_name AS user_name, SUM(o.quantity * p.price) AS total_spent
            FROM orders o
            JOIN users u ON o.user_id = u.user_id
            JOIN products p ON o.product_id = p.product_id
            GROUP BY u.first_name, u.last_name
            ORDER BY total_spent DESC;
        """)
        results = cur.fetchall()

        print("\nCustomer Spending Summary:")
        print("-----------------------------------------")
        for user_name, total in results:
            print(f"{user_name}: ${total:.2f}")

    except Exception as e:
        print("An error occurred:", e)
    finally:
        cur.close()
        conn.close()

def search_costumer(search):
    try:
        conn = connect_db()
        cur = conn.cursor()
        cur.execute("""
            SELECT u.first_name || ' ' || u.last_name AS user_name
            FROM users u
            WHERE u.first_name ILIKE %s
                or u.last_name ILIKE %s ;
        """, ('%' + search + '%', '%' + search + '%'))
        results = cur.fetchall()
        if results:
            print(f"\nCustomer Matching '{search}':")
            print("-----------------------------------------")
            for user_name in results:
                print(f"{user_name[0]}")
            print("\n")
        else:
            print(f"\nNo Customer found Matching '{search}'\n")


    except Exception as e:
        print("An error occurred:", e)
    finally:
        cur.close()
        conn.close()



# Argument parsing
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Manage Orders for the StoreDB")
    parser.add_argument('--user', type=str, help="User's email for the order")
    parser.add_argument('--product', type=str, help="Product name to order")
    parser.add_argument('--quantity', type=int, help="Quantity of the product")
    parser.add_argument('--show-spending', action='store_true', help="Display how much each customer spent")
    parser.add_argument('--search', type=str, help="Search for user by pattern")

    args = parser.parse_args()

    if args.user and args.product and args.quantity:
        add_order(args.user, args.product, args.quantity)
    elif args.show_spending:
        show_total_spent()
    elif args.search:
        search_costumer(args.search)    
    else:
        parser.print_help()
