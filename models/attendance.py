try:
    from database_sqlserver import execute_query
except ImportError:
    from database_fallback import execute_query
from datetime import datetime, date, timedelta
import json

class Attendance:
    def __init__(self, attendance_id=None, student_id=None, course=None, 
                 attendance_date=None, status='Present', notes=None, 
                 recorded_by=None, recorded_at=None):
        self.attendance_id = attendance_id
        self.student_id = student_id
        self.course = course
        self.attendance_date = attendance_date or date.today()
        self.status = status  # Present, Absent, Late, Excused
        self.notes = notes
        self.recorded_by = recorded_by
        self.recorded_at = recorded_at or datetime.now()
    
    def save(self):
        """Save attendance record to database"""
        try:
            if self.attendance_id:
                # Update existing attendance
                query = """UPDATE Attendance SET student_id = ?, course = ?, 
                          attendance_date = ?, status = ?, notes = ?, 
                          recorded_by = ?, recorded_at = ?
                          WHERE attendance_id = ?"""
                params = (self.student_id, self.course, self.attendance_date,
                         self.status, self.notes, self.recorded_by, self.recorded_at,
                         self.attendance_id)
            else:
                # Create new attendance record
                query = """INSERT INTO Attendance (student_id, course, attendance_date, 
                          status, notes, recorded_by, recorded_at)
                          VALUES (?, ?, ?, ?, ?, ?, ?)"""
                params = (self.student_id, self.course, self.attendance_date,
                         self.status, self.notes, self.recorded_by, self.recorded_at)
            
            result = execute_query(query, params)
            if result and not self.attendance_id:
                self.attendance_id = result
            return result is not None
        except Exception as e:
            print(f"Error saving attendance: {e}")
            return False
    
    def delete(self):
        """Delete attendance record from database"""
        try:
            if self.attendance_id:
                query = "DELETE FROM Attendance WHERE attendance_id = ?"
                result = execute_query(query, (self.attendance_id,))
                return result is not None
            return False
        except Exception as e:
            print(f"Error deleting attendance: {e}")
            return False
    
    @classmethod
    def get_all(cls):
        """Get all attendance records"""
        try:
            query = "SELECT * FROM Attendance ORDER BY attendance_date DESC, course ASC"
            result = execute_query(query, fetch=True)
            if result:
                return [cls(**row) for row in result]
            return []
        except Exception as e:
            print(f"Error getting all attendance: {e}")
            return []
    
    @classmethod
    def get_by_id(cls, attendance_id):
        """Get attendance record by ID"""
        try:
            query = "SELECT * FROM Attendance WHERE attendance_id = ?"
            result = execute_query(query, (attendance_id,), fetchone=True)
            if result:
                return cls(**result)
            return None
        except Exception as e:
            print(f"Error getting attendance by ID: {e}")
            return None
    
    @classmethod
    def get_by_student(cls, student_id, course=None, start_date=None, end_date=None):
        """Get attendance records for a specific student"""
        try:
            query = "SELECT * FROM Attendance WHERE student_id = ?"
            params = [student_id]
            
            if course:
                query += " AND course = ?"
                params.append(course)
            
            if start_date:
                query += " AND attendance_date >= ?"
                params.append(start_date)
            
            if end_date:
                query += " AND attendance_date <= ?"
                params.append(end_date)
            
            query += " ORDER BY attendance_date DESC"
            
            result = execute_query(query, params, fetch=True)
            if result:
                return [cls(**row) for row in result]
            return []
        except Exception as e:
            print(f"Error getting attendance by student: {e}")
            return []
    
    @classmethod
    def get_by_course(cls, course, attendance_date=None):
        """Get attendance records for a specific course"""
        try:
            if attendance_date:
                query = "SELECT * FROM Attendance WHERE course = ? AND attendance_date = ?"
                params = (course, attendance_date)
            else:
                query = "SELECT * FROM Attendance WHERE course = ? ORDER BY attendance_date DESC"
                params = (course,)
            
            result = execute_query(query, params, fetch=True)
            if result:
                return [cls(**row) for row in result]
            return []
        except Exception as e:
            print(f"Error getting attendance by course: {e}")
            return []
    
    @classmethod
    def get_by_date(cls, attendance_date):
        """Get attendance records for a specific date"""
        try:
            query = "SELECT * FROM Attendance WHERE attendance_date = ? ORDER BY course ASC"
            result = execute_query(query, (attendance_date,), fetch=True)
            if result:
                return [cls(**row) for row in result]
            return []
        except Exception as e:
            print(f"Error getting attendance by date: {e}")
            return []
    
    @classmethod
    def get_student_statistics(cls, student_id, course=None):
        """Get attendance statistics for a student"""
        try:
            base_query = "SELECT status, COUNT(*) as count FROM Attendance WHERE student_id = ?"
            params = [student_id]
            
            if course:
                base_query += " AND course = ?"
                params.append(course)
            
            base_query += " GROUP BY status"
            
            result = execute_query(base_query, params, fetch=True)
            
            stats = {
                'Present': 0,
                'Absent': 0,
                'Late': 0,
                'Excused': 0,
                'total': 0
            }
            
            if result:
                for row in result:
                    stats[row['status']] = row['count']
                    stats['total'] += row['count']
            
            # Calculate percentages
            if stats['total'] > 0:
                stats['present_percentage'] = round((stats['Present'] / stats['total']) * 100, 2)
                stats['absent_percentage'] = round((stats['Absent'] / stats['total']) * 100, 2)
                stats['late_percentage'] = round((stats['Late'] / stats['total']) * 100, 2)
                stats['excused_percentage'] = round((stats['Excused'] / stats['total']) * 100, 2)
            else:
                stats['present_percentage'] = 0
                stats['absent_percentage'] = 0
                stats['late_percentage'] = 0
                stats['excused_percentage'] = 0
            
            return stats
        except Exception as e:
            print(f"Error getting student attendance statistics: {e}")
            return {}
    
    @classmethod
    def get_course_statistics(cls, course, attendance_date=None):
        """Get attendance statistics for a course"""
        try:
            base_query = "SELECT status, COUNT(*) as count FROM Attendance WHERE course = ?"
            params = [course]
            
            if attendance_date:
                base_query += " AND attendance_date = ?"
                params.append(attendance_date)
            
            base_query += " GROUP BY status"
            
            result = execute_query(base_query, params, fetch=True)
            
            stats = {
                'Present': 0,
                'Absent': 0,
                'Late': 0,
                'Excused': 0,
                'total': 0
            }
            
            if result:
                for row in result:
                    stats[row['status']] = row['count']
                    stats['total'] += row['count']
            
            # Calculate percentages
            if stats['total'] > 0:
                stats['present_percentage'] = round((stats['Present'] / stats['total']) * 100, 2)
                stats['absent_percentage'] = round((stats['Absent'] / stats['total']) * 100, 2)
                stats['late_percentage'] = round((stats['Late'] / stats['total']) * 100, 2)
                stats['excused_percentage'] = round((stats['Excused'] / stats['total']) * 100, 2)
            else:
                stats['present_percentage'] = 0
                stats['absent_percentage'] = 0
                stats['late_percentage'] = 0
                stats['excused_percentage'] = 0
            
            return stats
        except Exception as e:
            print(f"Error getting course attendance statistics: {e}")
            return {}
    
    @classmethod
    def mark_attendance_for_course(cls, course, attendance_date, student_attendance_data, recorded_by):
        """Mark attendance for multiple students in a course"""
        try:
            success_count = 0
            for student_id, status in student_attendance_data.items():
                # Check if attendance already exists
                existing = execute_query(
                    "SELECT attendance_id FROM Attendance WHERE student_id = ? AND course = ? AND attendance_date = ?",
                    (student_id, course, attendance_date),
                    fetchone=True
                )
                
                if existing:
                    # Update existing record
                    attendance = cls.get_by_id(existing['attendance_id'])
                    attendance.status = status
                    attendance.recorded_by = recorded_by
                    attendance.recorded_at = datetime.now()
                else:
                    # Create new record
                    attendance = cls(
                        student_id=student_id,
                        course=course,
                        attendance_date=attendance_date,
                        status=status,
                        recorded_by=recorded_by
                    )
                
                if attendance.save():
                    success_count += 1
            
            return success_count
        except Exception as e:
            print(f"Error marking attendance for course: {e}")
            return 0
    
    def get_status_color(self):
        """Get color code for attendance status"""
        colors = {
            'Present': '#28a745',    # Green
            'Absent': '#dc3545',     # Red
            'Late': '#ffc107',       # Yellow
            'Excused': '#17a2b8'     # Teal
        }
        return colors.get(self.status, '#6c757d')
    
    def get_status_icon(self):
        """Get icon for attendance status"""
        icons = {
            'Present': 'bi-check-circle-fill',
            'Absent': 'bi-x-circle-fill',
            'Late': 'bi-clock-fill',
            'Excused': 'bi-info-circle-fill'
        }
        return icons.get(self.status, 'bi-question-circle-fill')
    
    def validate(self):
        """Validate attendance data"""
        errors = []
        
        # Validate student_id
        if not self.student_id:
            errors.append("Student ID is required")
        
        # Validate course
        if not self.course or len(self.course.strip()) < 2:
            errors.append("Course must be specified")
        elif len(self.course) > 100:
            errors.append("Course name must be less than 100 characters")
        
        # Validate attendance_date
        if not self.attendance_date:
            errors.append("Attendance date is required")
        elif self.attendance_date > date.today():
            errors.append("Attendance date cannot be in the future")
        
        # Validate status
        valid_statuses = ['Present', 'Absent', 'Late', 'Excused']
        if self.status not in valid_statuses:
            errors.append("Invalid attendance status")
        
        # Validate notes length
        if self.notes and len(self.notes) > 500:
            errors.append("Notes must be less than 500 characters")
        
        return errors
    
    def to_dict(self):
        """Convert attendance to dictionary"""
        return {
            'attendance_id': self.attendance_id,
            'student_id': self.student_id,
            'course': self.course,
            'attendance_date': self.attendance_date.isoformat() if self.attendance_date else None,
            'status': self.status,
            'notes': self.notes,
            'recorded_by': self.recorded_by,
            'recorded_at': self.recorded_at.isoformat() if self.recorded_at else None,
            'status_color': self.get_status_color(),
            'status_icon': self.get_status_icon()
        }
    
    def __repr__(self):
        return f"<Attendance {self.student_id} - {self.course} ({self.attendance_date})>"

