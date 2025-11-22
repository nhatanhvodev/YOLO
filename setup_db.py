"""
Script to create and initialize the MySQL database for the traffic monitoring system.
Run this after installing MySQL and before starting the app with USE_DB=1.
"""
import pymysql
import sys

def setup_database():
    """Create database, tables, and initial data."""
    connection = None
    try:
        # Connect to MySQL server (without specifying database)
        print("Connecting to MySQL server...")
        connection = pymysql.connect(
            host='localhost',
            user='root',
            password='12345',
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        
        with connection.cursor() as cursor:
            # Create database
            print("Creating database 'datn'...")
            cursor.execute("CREATE DATABASE IF NOT EXISTS datn")
            cursor.execute("USE datn")
            
            # Create nametransportation table
            print("Creating 'nametransportation' table...")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS nametransportation(
                    id_name INT PRIMARY KEY,
                    vh_name VARCHAR(255)
                )
            """)
            
            # Insert vehicle types
            print("Inserting vehicle types...")
            cursor.execute("""
                INSERT INTO nametransportation(id_name, vh_name)
                VALUES (1,'OTO'),(2,'Xe May'),(3,'Xe Dap'),(4,'Xe Tai'),(5,'Xe Bus')
                ON DUPLICATE KEY UPDATE vh_name=VALUES(vh_name)
            """)
            
            # Create transportationviolation table
            print("Creating 'transportationviolation' table...")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS transportationviolation(
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    id_name INT,
                    date_violate DATE,
                    FOREIGN KEY(id_name) REFERENCES nametransportation(id_name)
                )
            """)
            
            # Check if we need initial data
            cursor.execute("SELECT COUNT(*) as count FROM transportationviolation")
            result = cursor.fetchone()
            
            if result['count'] == 0:
                print("Inserting initial violation data...")
                cursor.execute("""
                    INSERT INTO transportationviolation(id_name, date_violate)
                    VALUES (1,'2023-02-12'), (2,'2023-02-12'), (3,'2023-02-12'),
                           (4,'2023-02-12'), (5,'2023-02-12')
                """)
            else:
                print(f"Database already contains {result['count']} violation records.")
            
            # Commit changes
            connection.commit()
            print("\n✓ Database setup completed successfully!")
            print("You can now run the app with: $env:USE_DB='1'; python python_project\\app_server.py")
            
    except pymysql.err.OperationalError as e:
        print(f"\n✗ Error connecting to MySQL: {e}")
        print("\nPlease ensure:")
        print("1. MySQL server is running")
        print("2. Username is 'root' and password is '12345'")
        print("   (or update credentials in python_project/app_server.py)")
        sys.exit(1)
        
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        sys.exit(1)
        
    finally:
        if connection:
            connection.close()

if __name__ == '__main__':
    setup_database()
