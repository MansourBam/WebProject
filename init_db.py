#!/usr/bin/env python3
"""
Database initialization script for University Management System
This script creates the database schema and inserts demo data
"""

from database_fallback import test_connection, create_database_schema, insert_sample_data

def main():
    print("Initializing University Management System Database...")
    
    # Test connection
    success, message = test_connection()
    if not success:
        print(f"Database connection failed: {message}")
        return False
    
    print("Database connection successful!")
    
    # Create schema
    print("Creating database schema...")
    if not create_database_schema():
        print("Failed to create database schema")
        return False
    
    print("Database schema created successfully!")
    
    # Insert sample data
    print("Inserting demo data...")
    if not insert_sample_data():
        print("Failed to insert demo data")
        return False
    
    print("Demo data inserted successfully!")
    print("\n" + "="*50)
    print("DATABASE INITIALIZATION COMPLETE!")
    print("="*50)
    print("\nDemo Accounts:")
    print("Admin: admin@university.edu / admin123")
    print("Student: student@university.edu / student123")
    print("Teacher: teacher@university.edu / teacher123")
    print("\nYou can now run the application with: python app.py")
    
    return True

if __name__ == "__main__":
    main()

