import pyodbc
import os
from contextlib import contextmanager
from utils.security_utils import hash_password
from models.user import User

# SQL Server configuration
SQL_SERVER = 'DESKTOP-E6D60KM\SQLEXP2017'
SQL_DATABASE = 'university_management'  # Make sure this database exists
SQL_USERNAME = 'sa'
SQL_PASSWORD = '2003'
SQL_DRIVER = 'ODBC Driver 17 for SQL Server'  # Make sure this driver is installed

def get_master_conn_str():
    return (
        f'DRIVER={{{SQL_DRIVER}}};'
        f'SERVER={SQL_SERVER};'
        f'DATABASE=master;'
        f'UID={SQL_USERNAME};'
        f'PWD={SQL_PASSWORD}'
    )

CONN_STR = (
    f'DRIVER={{{SQL_DRIVER}}};'
    f'SERVER={SQL_SERVER};'
    f'DATABASE={SQL_DATABASE};'
    f'UID={SQL_USERNAME};'
    f'PWD={SQL_PASSWORD}'
)

def create_database():
    """Create the database if it doesn't exist"""
    try:
        # Connect to master database first
        conn = pyodbc.connect(get_master_conn_str(), autocommit=True)
        cursor = conn.cursor()
        
        # Check if database exists
        cursor.execute(f"SELECT database_id FROM sys.databases WHERE Name = '{SQL_DATABASE}'")
        if cursor.fetchone() is None:
            print(f"Creating database {SQL_DATABASE}...")
            cursor.execute(f"CREATE DATABASE {SQL_DATABASE}")
            print("Database created successfully")
        else:
            print(f"Database {SQL_DATABASE} already exists")
        
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"Error creating database: {e}")
        return False

def get_db_connection():
    """Get database connection"""
    try:
        conn = pyodbc.connect(CONN_STR)
        return conn
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return None

def execute_query(query, params=None, fetch=False, fetchone=False):
    """Execute database query"""
    conn = None
    try:
        conn = get_db_connection()
        if not conn:
            print("Failed to get database connection")
            return None
            
        cursor = conn.cursor()
        
        try:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            if fetch:
                result = cursor.fetchall()
                if not result:
                    return []
                    
                # Get column names from cursor description
                columns = [column[0] for column in cursor.description]
                
                # Convert rows to dictionaries
                return [dict(zip(columns, row)) for row in result]
                
            elif fetchone:
                row = cursor.fetchone()
                if not row:
                    return None
                    
                # Get column names from cursor description
                columns = [column[0] for column in cursor.description]
                
                # Convert row to dictionary
                return dict(zip(columns, row))
                
            else:
                conn.commit()
                return True
                
        finally:
            cursor.close()
            
    except Exception as e:
        print(f"Error executing query: {e}")
        print(f"Query: {query}")
        print(f"Params: {params}")
        if conn:
            conn.rollback()
        return None
    finally:
        if conn:
            conn.close()

def test_connection():
    """Test database connection"""
    try:
        # First ensure database exists
        if not create_database():
            return False, "Failed to create/verify database"
            
        conn = get_db_connection()
        if not conn:
            return False, "Failed to get database connection"
            
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        return True, "Connection successful"
    except Exception as e:
        return False, str(e)

def create_database_schema():
    """Create database schema for SQL Server"""
    try:
        conn = get_db_connection()
        if not conn:
            print("Failed to get database connection")
            return False
        cursor = conn.cursor()
        print("Connected to database successfully")
        
        # Drop existing tables
        drop_queries = [
            "IF OBJECT_ID('Enrollments', 'U') IS NOT NULL DROP TABLE Enrollments",
            "IF OBJECT_ID('Homework', 'U') IS NOT NULL DROP TABLE Homework",
            "IF OBJECT_ID('Courses', 'U') IS NOT NULL DROP TABLE Courses",
            "IF OBJECT_ID('Students', 'U') IS NOT NULL DROP TABLE Students",
            "IF OBJECT_ID('Teachers', 'U') IS NOT NULL DROP TABLE Teachers",
            "IF OBJECT_ID('Users', 'U') IS NOT NULL DROP TABLE Users"
        ]
        
        for query in drop_queries:
            print(f"Executing: {query}")
            cursor.execute(query)
        print("Dropped existing tables")
        
        # Create Users table first
        print("Creating Users table...")
        cursor.execute("""
            CREATE TABLE Users (
                UserID INT IDENTITY(1,1) PRIMARY KEY,
                Email NVARCHAR(100) NOT NULL,
                Password NVARCHAR(256) NOT NULL,
                Name NVARCHAR(100) NOT NULL,
                Role NVARCHAR(20) NOT NULL CHECK (Role IN ('student', 'teacher', 'admin')),
                Verified BIT DEFAULT 0,
                VerifyToken NVARCHAR(128),
                Nationality NVARCHAR(50),
                Gender NVARCHAR(10),
                Status NVARCHAR(20),
                Major NVARCHAR(50),
                CreatedAt DATETIME DEFAULT GETDATE(),
                CONSTRAINT UQ_User_Email UNIQUE (Email)
            )
        """)
        print("Users table created")

        # Create Students table
        print("Creating Students table...")
        cursor.execute("""
            CREATE TABLE Students (
                StudentID INT IDENTITY(1,1) PRIMARY KEY,
                FullName NVARCHAR(100) NOT NULL,
                Nationality NVARCHAR(50) NOT NULL,
                Status NVARCHAR(20) NOT NULL DEFAULT 'Active',
                UniversityNumber NVARCHAR(20) NOT NULL,
                Email NVARCHAR(100) NOT NULL,
                Major NVARCHAR(50) NOT NULL,
                Gender NVARCHAR(10) DEFAULT 'Male',
                Phone NVARCHAR(20),
                CreatedAt DATETIME DEFAULT GETDATE(),
                CONSTRAINT UQ_Student_UniversityNumber UNIQUE (UniversityNumber),
                CONSTRAINT UQ_Student_Email UNIQUE (Email)
            )
        """)
        print("Students table created")

        # Create Teachers table
        print("Creating Teachers table...")
        cursor.execute("""
            CREATE TABLE Teachers (
                TeacherID INT IDENTITY(1,1) PRIMARY KEY,
                TeacherFullName NVARCHAR(100) NOT NULL,
                Email NVARCHAR(100) NOT NULL,
                Major NVARCHAR(50),
                Phone NVARCHAR(20),
                HireDate DATE DEFAULT GETDATE(),
                Department NVARCHAR(50),
                CreatedAt DATETIME DEFAULT GETDATE(),
                CONSTRAINT UQ_Teacher_Email UNIQUE (Email)
            )
        """)
        print("Teachers table created")

        # Create Courses table
        print("Creating Courses table...")
        cursor.execute("""
            CREATE TABLE Courses (
                CourseID INT IDENTITY(1,1) PRIMARY KEY,
                CourseName NVARCHAR(100) NOT NULL,
                CourseCode NVARCHAR(20) NOT NULL,
                CreditHours INT NOT NULL,
                Section NVARCHAR(10),
                Room NVARCHAR(20),
                TimeSchedule NVARCHAR(100),
                TeacherID INT,
                MaxStudents INT DEFAULT 30,
                CreatedAt DATETIME DEFAULT GETDATE(),
                CONSTRAINT UQ_Course_Code UNIQUE (CourseCode),
                FOREIGN KEY (TeacherID) REFERENCES Teachers(TeacherID)
            )
        """)
        print("Courses table created")

        # Create Enrollments table
        print("Creating Enrollments table...")
        cursor.execute("""
            CREATE TABLE Enrollments (
                EnrollmentID INT IDENTITY(1,1) PRIMARY KEY,
                StudentID INT NOT NULL,
                CourseID INT NOT NULL,
                EnrollmentDate DATETIME DEFAULT GETDATE(),
                Grade NVARCHAR(2),
                Status NVARCHAR(20) DEFAULT 'Active',
                FOREIGN KEY (StudentID) REFERENCES Students(StudentID),
                FOREIGN KEY (CourseID) REFERENCES Courses(CourseID),
                CONSTRAINT UQ_Enrollment UNIQUE (StudentID, CourseID)
            )
        """)
        print("Enrollments table created")

        # Create Homework table
        print("Creating Homework table...")
        cursor.execute("""
            CREATE TABLE Homework (
                HomeworkID INT IDENTITY(1,1) PRIMARY KEY,
                CourseID INT NOT NULL,
                Title NVARCHAR(200) NOT NULL,
                Description NVARCHAR(MAX),
                DueDate DATETIME NOT NULL,
                CreatedAt DATETIME DEFAULT GETDATE(),
                FOREIGN KEY (CourseID) REFERENCES Courses(CourseID)
            )
        """)
        print("Homework table created")

        # Create HomeworkSubmissions table
        print("Creating HomeworkSubmissions table...")
        cursor.execute("""
            CREATE TABLE HomeworkSubmissions (
                SubmissionID INT IDENTITY(1,1) PRIMARY KEY,
                HomeworkID INT NOT NULL,
                StudentID INT NOT NULL,
                SubmissionText NVARCHAR(MAX),
                SubmittedAt DATETIME DEFAULT GETDATE(),
                Grade DECIMAL(5,2),
                Feedback NVARCHAR(MAX),
                FOREIGN KEY (HomeworkID) REFERENCES Homework(HomeworkID),
                FOREIGN KEY (StudentID) REFERENCES Students(StudentID),
                CONSTRAINT UQ_Submission UNIQUE (HomeworkID, StudentID)
            )
        """)
        print("HomeworkSubmissions table created")

        # Create Attendance table
        print("Creating Attendance table...")
        cursor.execute("""
            CREATE TABLE Attendance (
                AttendanceID INT IDENTITY(1,1) PRIMARY KEY,
                StudentID INT NOT NULL,
                CourseID INT NOT NULL,
                Date DATE NOT NULL,
                Status NVARCHAR(20) NOT NULL CHECK (Status IN ('Present', 'Absent', 'Late')),
                Notes NVARCHAR(200),
                FOREIGN KEY (StudentID) REFERENCES Students(StudentID),
                FOREIGN KEY (CourseID) REFERENCES Courses(CourseID),
                CONSTRAINT UQ_Attendance UNIQUE (StudentID, CourseID, Date)
            )
        """)
        print("Attendance table created")

        # Create Participation table
        print("Creating Participation table...")
        cursor.execute("""
            CREATE TABLE Participation (
                ParticipationID INT IDENTITY(1,1) PRIMARY KEY,
                StudentID INT NOT NULL,
                CourseID INT NOT NULL,
                Date DATE NOT NULL,
                Score INT NOT NULL CHECK (Score >= 0 AND Score <= 10),
                Comments NVARCHAR(200),
                FOREIGN KEY (StudentID) REFERENCES Students(StudentID),
                FOREIGN KEY (CourseID) REFERENCES Courses(CourseID)
            )
        """)
        print("Participation table created")

        conn.commit()
        print("Database schema created successfully")
        return True
        
    except Exception as e:
        print(f"Error creating database schema: {e}")
        if conn:
            conn.rollback()
        return False
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def insert_sample_data():
    """Insert sample data into the database (SQL Server syntax)"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Insert sample admin user
            admin = {
                'email': 'admin@university.edu',
                'password': hash_password('admin123'),
                'name': 'System Administrator',
                'role': 'admin',
                'verified': 1,
                'nationality': 'Saudi Arabia',
                'gender': 'Male',
                'status': 'Active'
            }
            cursor.execute("""
                INSERT INTO Users (Email, Password, Name, Role, Verified, Nationality, Gender, Status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (admin['email'], admin['password'], admin['name'], admin['role'], 
                  admin['verified'], admin['nationality'], admin['gender'], admin['status']))
            
            # Insert sample student user
            student = {
                'email': 'student@university.edu',
                'password': hash_password('student123'),
                'name': 'John Student',
                'role': 'student',
                'verified': 1,
                'nationality': 'Saudi Arabia',
                'gender': 'Male',
                'status': 'Active',
                'major': 'Computer Science'
            }
            cursor.execute("""
                INSERT INTO Users (Email, Password, Name, Role, Verified, Nationality, Gender, Status, Major)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (student['email'], student['password'], student['name'], student['role'],
                  student['verified'], student['nationality'], student['gender'], 
                  student['status'], student['major']))
            
            # Insert sample teacher user
            teacher = {
                'email': 'teacher@university.edu',
                'password': hash_password('teacher123'),
                'name': 'Dr. Jane Teacher',
                'role': 'teacher',
                'verified': 1,
                'nationality': 'Saudi Arabia',
                'gender': 'Female',
                'status': 'Active',
                'major': 'Computer Science'
            }
            cursor.execute("""
                INSERT INTO Users (Email, Password, Name, Role, Verified, Nationality, Gender, Status, Major)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (teacher['email'], teacher['password'], teacher['name'], teacher['role'],
                  teacher['verified'], teacher['nationality'], teacher['gender'],
                  teacher['status'], teacher['major']))
            
            conn.commit()
            print("Sample data inserted successfully")
            return True
    except Exception as e:
        print(f"Error inserting sample data: {e}")
        return False

if __name__ == "__main__":
    # Test connection and initialize database
    success, message = test_connection()
    print(f"Connection test: {message}")
    
    if success:
        create_database_schema()
        insert_sample_data()

