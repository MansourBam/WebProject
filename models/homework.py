try:
    from database_sqlserver import execute_query
except ImportError:
    from database_fallback import execute_query
from datetime import datetime, timedelta
import json

class Homework:
    def __init__(self, homework_id=None, title=None, description=None, course=None, 
                 assigned_by=None, due_date=None, status='Pending', priority='Medium',
                 student_id=None, submission_text=None, submission_file=None, 
                 submitted_at=None, grade=None, feedback=None, created_at=None):
        self.homework_id = homework_id
        self.title = title
        self.description = description
        self.course = course
        self.assigned_by = assigned_by
        self.due_date = due_date
        self.status = status  # Pending, In Progress, Submitted, Graded, Overdue
        self.priority = priority  # Low, Medium, High, Critical
        self.student_id = student_id
        self.submission_text = submission_text
        self.submission_file = submission_file
        self.submitted_at = submitted_at
        self.grade = grade
        self.feedback = feedback
        self.created_at = created_at or datetime.now()
    
    def save(self):
        """Save homework to database"""
        try:
            if self.homework_id:
                # Update existing homework
                query = """UPDATE Homework SET title = ?, description = ?, course = ?, 
                          assigned_by = ?, due_date = ?, status = ?, priority = ?, 
                          student_id = ?, submission_text = ?, submission_file = ?, 
                          submitted_at = ?, grade = ?, feedback = ?
                          WHERE homework_id = ?"""
                params = (self.title, self.description, self.course, self.assigned_by,
                         self.due_date, self.status, self.priority, self.student_id,
                         self.submission_text, self.submission_file, self.submitted_at,
                         self.grade, self.feedback, self.homework_id)
            else:
                # Create new homework
                query = """INSERT INTO Homework (title, description, course, assigned_by, 
                          due_date, status, priority, student_id, submission_text, 
                          submission_file, submitted_at, grade, feedback, created_at)
                          VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""
                params = (self.title, self.description, self.course, self.assigned_by,
                         self.due_date, self.status, self.priority, self.student_id,
                         self.submission_text, self.submission_file, self.submitted_at,
                         self.grade, self.feedback, self.created_at)
            
            result = execute_query(query, params)
            if result and not self.homework_id:
                self.homework_id = result
            return result is not None
        except Exception as e:
            print(f"Error saving homework: {e}")
            return False
    
    def delete(self):
        """Delete homework from database"""
        try:
            if self.homework_id:
                query = "DELETE FROM Homework WHERE homework_id = ?"
                result = execute_query(query, (self.homework_id,))
                return result is not None
            return False
        except Exception as e:
            print(f"Error deleting homework: {e}")
            return False
    
    @classmethod
    def get_all(cls):
        """Get all homework assignments"""
        try:
            query = "SELECT * FROM Homework ORDER BY due_date ASC"
            result = execute_query(query, fetch=True)
            if result:
                return [cls(**row) for row in result]
            return []
        except Exception as e:
            print(f"Error getting all homework: {e}")
            return []
    
    @classmethod
    def get_by_id(cls, homework_id):
        """Get homework by ID"""
        try:
            query = "SELECT * FROM Homework WHERE homework_id = ?"
            result = execute_query(query, (homework_id,), fetchone=True)
            if result:
                return cls(**result)
            return None
        except Exception as e:
            print(f"Error getting homework by ID: {e}")
            return None
    
    @classmethod
    def get_by_student(cls, student_id):
        """Get homework assignments for a specific student"""
        try:
            query = """SELECT * FROM Homework 
                      WHERE student_id = ? OR student_id IS NULL 
                      ORDER BY due_date ASC"""
            result = execute_query(query, (student_id,), fetch=True)
            if result:
                return [cls(**row) for row in result]
            return []
        except Exception as e:
            print(f"Error getting homework by student: {e}")
            return []
    
    @classmethod
    def get_by_course(cls, course):
        """Get homework assignments for a specific course"""
        try:
            query = "SELECT * FROM Homework WHERE course = ? ORDER BY due_date ASC"
            result = execute_query(query, (course,), fetch=True)
            if result:
                return [cls(**row) for row in result]
            return []
        except Exception as e:
            print(f"Error getting homework by course: {e}")
            return []
    
    @classmethod
    def get_overdue(cls):
        """Get overdue homework assignments"""
        try:
            current_time = datetime.now()
            query = """SELECT * FROM Homework 
                      WHERE due_date < ? AND status NOT IN ('Submitted', 'Graded')
                      ORDER BY due_date ASC"""
            result = execute_query(query, (current_time,), fetch=True)
            if result:
                return [cls(**row) for row in result]
            return []
        except Exception as e:
            print(f"Error getting overdue homework: {e}")
            return []
    
    @classmethod
    def get_pending(cls, student_id=None):
        """Get pending homework assignments"""
        try:
            if student_id:
                query = """SELECT * FROM Homework 
                          WHERE (student_id = ? OR student_id IS NULL) 
                          AND status = 'Pending'
                          ORDER BY due_date ASC"""
                params = (student_id,)
            else:
                query = "SELECT * FROM Homework WHERE status = 'Pending' ORDER BY due_date ASC"
                params = ()
            
            result = execute_query(query, params, fetch=True)
            if result:
                return [cls(**row) for row in result]
            return []
        except Exception as e:
            print(f"Error getting pending homework: {e}")
            return []
    
    def submit(self, submission_text=None, submission_file=None):
        """Submit homework assignment"""
        try:
            self.submission_text = submission_text
            self.submission_file = submission_file
            self.submitted_at = datetime.now()
            self.status = 'Submitted'
            return self.save()
        except Exception as e:
            print(f"Error submitting homework: {e}")
            return False
    
    def grade(self, grade, feedback=None):
        """Grade homework assignment"""
        try:
            self.grade = grade
            self.feedback = feedback
            self.status = 'Graded'
            return self.save()
        except Exception as e:
            print(f"Error grading homework: {e}")
            return False
    
    def is_overdue(self):
        """Check if homework is overdue"""
        if not self.due_date:
            return False
        return datetime.now() > self.due_date and self.status not in ['Submitted', 'Graded']
    
    def days_until_due(self):
        """Get number of days until due date"""
        if not self.due_date:
            return None
        delta = self.due_date - datetime.now()
        return delta.days
    
    def get_priority_color(self):
        """Get color code for priority level"""
        colors = {
            'Low': '#28a745',      # Green
            'Medium': '#ffc107',   # Yellow
            'High': '#fd7e14',     # Orange
            'Critical': '#dc3545'  # Red
        }
        return colors.get(self.priority, '#6c757d')
    
    def get_status_color(self):
        """Get color code for status"""
        colors = {
            'Pending': '#6c757d',      # Gray
            'In Progress': '#007bff',  # Blue
            'Submitted': '#28a745',    # Green
            'Graded': '#17a2b8',       # Teal
            'Overdue': '#dc3545'       # Red
        }
        return colors.get(self.status, '#6c757d')
    
    def validate(self):
        """Validate homework data"""
        errors = []
        
        # Validate title
        if not self.title or len(self.title.strip()) < 3:
            errors.append("Title must be at least 3 characters long")
        elif len(self.title) > 200:
            errors.append("Title must be less than 200 characters")
        
        # Validate description
        if self.description and len(self.description) > 2000:
            errors.append("Description must be less than 2000 characters")
        
        # Validate course
        if not self.course or len(self.course.strip()) < 2:
            errors.append("Course must be specified")
        elif len(self.course) > 100:
            errors.append("Course name must be less than 100 characters")
        
        # Validate due date
        if self.due_date and self.due_date < datetime.now():
            if not self.homework_id:  # Only check for new homework
                errors.append("Due date cannot be in the past")
        
        # Validate status
        valid_statuses = ['Pending', 'In Progress', 'Submitted', 'Graded', 'Overdue']
        if self.status not in valid_statuses:
            errors.append("Invalid status")
        
        # Validate priority
        valid_priorities = ['Low', 'Medium', 'High', 'Critical']
        if self.priority not in valid_priorities:
            errors.append("Invalid priority level")
        
        # Validate grade
        if self.grade is not None:
            try:
                grade_value = float(self.grade)
                if grade_value < 0 or grade_value > 100:
                    errors.append("Grade must be between 0 and 100")
            except (ValueError, TypeError):
                errors.append("Grade must be a valid number")
        
        return errors
    
    def to_dict(self):
        """Convert homework to dictionary"""
        return {
            'homework_id': self.homework_id,
            'title': self.title,
            'description': self.description,
            'course': self.course,
            'assigned_by': self.assigned_by,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'status': self.status,
            'priority': self.priority,
            'student_id': self.student_id,
            'submission_text': self.submission_text,
            'submission_file': self.submission_file,
            'submitted_at': self.submitted_at.isoformat() if self.submitted_at else None,
            'grade': self.grade,
            'feedback': self.feedback,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'is_overdue': self.is_overdue(),
            'days_until_due': self.days_until_due(),
            'priority_color': self.get_priority_color(),
            'status_color': self.get_status_color()
        }
    
    def __repr__(self):
        return f"<Homework {self.title} ({self.course})>"

