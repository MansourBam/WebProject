try:
    from database_sqlserver import execute_query
except ImportError:
    from database_fallback import execute_query
from datetime import datetime, date, timedelta
import json

class Participation:
    def __init__(self, participation_id=None, student_id=None, course=None, 
                 activity_type=None, activity_date=None, points=0, 
                 description=None, recorded_by=None, recorded_at=None):
        self.participation_id = participation_id
        self.student_id = student_id
        self.course = course
        self.activity_type = activity_type  # Discussion, Presentation, Question, Assignment, Quiz, Project
        self.activity_date = activity_date or date.today()
        self.points = points or 0
        self.description = description
        self.recorded_by = recorded_by
        self.recorded_at = recorded_at or datetime.now()
    
    def save(self):
        """Save participation record to database"""
        try:
            if self.participation_id:
                # Update existing participation
                query = """UPDATE Participation SET student_id = ?, course = ?, 
                          activity_type = ?, activity_date = ?, points = ?, 
                          description = ?, recorded_by = ?, recorded_at = ?
                          WHERE participation_id = ?"""
                params = (self.student_id, self.course, self.activity_type,
                         self.activity_date, self.points, self.description,
                         self.recorded_by, self.recorded_at, self.participation_id)
            else:
                # Create new participation record
                query = """INSERT INTO Participation (student_id, course, activity_type, 
                          activity_date, points, description, recorded_by, recorded_at)
                          VALUES (?, ?, ?, ?, ?, ?, ?, ?)"""
                params = (self.student_id, self.course, self.activity_type,
                         self.activity_date, self.points, self.description,
                         self.recorded_by, self.recorded_at)
            
            result = execute_query(query, params)
            if result and not self.participation_id:
                self.participation_id = result
            return result is not None
        except Exception as e:
            print(f"Error saving participation: {e}")
            return False
    
    def delete(self):
        """Delete participation record from database"""
        try:
            if self.participation_id:
                query = "DELETE FROM Participation WHERE participation_id = ?"
                result = execute_query(query, (self.participation_id,))
                return result is not None
            return False
        except Exception as e:
            print(f"Error deleting participation: {e}")
            return False
    
    @classmethod
    def get_all(cls):
        """Get all participation records"""
        try:
            query = "SELECT * FROM Participation ORDER BY activity_date DESC, course ASC"
            result = execute_query(query, fetch=True)
            if result:
                return [cls(**row) for row in result]
            return []
        except Exception as e:
            print(f"Error getting all participation: {e}")
            return []
    
    @classmethod
    def get_by_id(cls, participation_id):
        """Get participation record by ID"""
        try:
            query = "SELECT * FROM Participation WHERE participation_id = ?"
            result = execute_query(query, (participation_id,), fetchone=True)
            if result:
                return cls(**result)
            return None
        except Exception as e:
            print(f"Error getting participation by ID: {e}")
            return None
    
    @classmethod
    def get_by_student(cls, student_id, course=None, start_date=None, end_date=None):
        """Get participation records for a specific student"""
        try:
            query = "SELECT * FROM Participation WHERE student_id = ?"
            params = [student_id]
            
            if course:
                query += " AND course = ?"
                params.append(course)
            
            if start_date:
                query += " AND activity_date >= ?"
                params.append(start_date)
            
            if end_date:
                query += " AND activity_date <= ?"
                params.append(end_date)
            
            query += " ORDER BY activity_date DESC"
            
            result = execute_query(query, params, fetch=True)
            if result:
                return [cls(**row) for row in result]
            return []
        except Exception as e:
            print(f"Error getting participation by student: {e}")
            return []
    
    @classmethod
    def get_by_course(cls, course, activity_date=None):
        """Get participation records for a specific course"""
        try:
            if activity_date:
                query = "SELECT * FROM Participation WHERE course = ? AND activity_date = ?"
                params = (course, activity_date)
            else:
                query = "SELECT * FROM Participation WHERE course = ? ORDER BY activity_date DESC"
                params = (course,)
            
            result = execute_query(query, params, fetch=True)
            if result:
                return [cls(**row) for row in result]
            return []
        except Exception as e:
            print(f"Error getting participation by course: {e}")
            return []
    
    @classmethod
    def get_student_statistics(cls, student_id, course=None):
        """Get participation statistics for a student"""
        try:
            base_query = """SELECT activity_type, COUNT(*) as count, SUM(points) as total_points 
                           FROM Participation WHERE student_id = ?"""
            params = [student_id]
            
            if course:
                base_query += " AND course = ?"
                params.append(course)
            
            base_query += " GROUP BY activity_type"
            
            result = execute_query(base_query, params, fetch=True)
            
            stats = {
                'total_activities': 0,
                'total_points': 0,
                'activities_by_type': {},
                'points_by_type': {}
            }
            
            if result:
                for row in result:
                    activity_type = row['activity_type']
                    count = row['count']
                    points = row['total_points'] or 0
                    
                    stats['activities_by_type'][activity_type] = count
                    stats['points_by_type'][activity_type] = points
                    stats['total_activities'] += count
                    stats['total_points'] += points
            
            # Get average points per activity
            if stats['total_activities'] > 0:
                stats['average_points'] = round(stats['total_points'] / stats['total_activities'], 2)
            else:
                stats['average_points'] = 0
            
            return stats
        except Exception as e:
            print(f"Error getting student participation statistics: {e}")
            return {}
    
    @classmethod
    def get_course_statistics(cls, course):
        """Get participation statistics for a course"""
        try:
            # Get total statistics
            total_query = """SELECT COUNT(*) as total_activities, SUM(points) as total_points,
                            COUNT(DISTINCT student_id) as active_students
                            FROM Participation WHERE course = ?"""
            total_result = execute_query(total_query, (course,), fetchone=True)
            
            # Get statistics by activity type
            type_query = """SELECT activity_type, COUNT(*) as count, SUM(points) as total_points,
                           AVG(points) as avg_points
                           FROM Participation WHERE course = ?
                           GROUP BY activity_type"""
            type_result = execute_query(type_query, (course,), fetch=True)
            
            stats = {
                'total_activities': total_result['total_activities'] if total_result else 0,
                'total_points': total_result['total_points'] if total_result else 0,
                'active_students': total_result['active_students'] if total_result else 0,
                'activities_by_type': {},
                'points_by_type': {},
                'avg_points_by_type': {}
            }
            
            if type_result:
                for row in type_result:
                    activity_type = row['activity_type']
                    stats['activities_by_type'][activity_type] = row['count']
                    stats['points_by_type'][activity_type] = row['total_points'] or 0
                    stats['avg_points_by_type'][activity_type] = round(row['avg_points'] or 0, 2)
            
            return stats
        except Exception as e:
            print(f"Error getting course participation statistics: {e}")
            return {}
    
    @classmethod
    def get_leaderboard(cls, course=None, limit=10):
        """Get participation leaderboard"""
        try:
            base_query = """SELECT s.full_name, s.university_number, p.student_id,
                           COUNT(*) as total_activities, SUM(p.points) as total_points
                           FROM Participation p
                           JOIN Students s ON p.student_id = s.StudentID
                           WHERE 1=1"""
            params = []
            
            if course:
                base_query += " AND p.course = ?"
                params.append(course)
            
            base_query += """ GROUP BY p.student_id, s.full_name, s.university_number
                             ORDER BY total_points DESC, total_activities DESC
                             LIMIT ?"""
            params.append(limit)
            
            result = execute_query(base_query, params, fetch=True)
            
            leaderboard = []
            if result:
                for i, row in enumerate(result, 1):
                    leaderboard.append({
                        'rank': i,
                        'student_name': row['full_name'],
                        'university_number': row['university_number'],
                        'student_id': row['student_id'],
                        'total_activities': row['total_activities'],
                        'total_points': row['total_points']
                    })
            
            return leaderboard
        except Exception as e:
            print(f"Error getting participation leaderboard: {e}")
            return []
    
    def get_activity_color(self):
        """Get color code for activity type"""
        colors = {
            'Discussion': '#17a2b8',      # Teal
            'Presentation': '#6f42c1',    # Purple
            'Question': '#fd7e14',        # Orange
            'Assignment': '#28a745',      # Green
            'Quiz': '#dc3545',            # Red
            'Project': '#007bff'          # Blue
        }
        return colors.get(self.activity_type, '#6c757d')
    
    def get_activity_icon(self):
        """Get icon for activity type"""
        icons = {
            'Discussion': 'bi-chat-dots-fill',
            'Presentation': 'bi-easel-fill',
            'Question': 'bi-question-circle-fill',
            'Assignment': 'bi-file-text-fill',
            'Quiz': 'bi-clipboard-check-fill',
            'Project': 'bi-folder-fill'
        }
        return icons.get(self.activity_type, 'bi-star-fill')
    
    def get_points_badge_class(self):
        """Get CSS class for points badge"""
        if self.points >= 10:
            return 'badge-success'
        elif self.points >= 5:
            return 'badge-warning'
        elif self.points > 0:
            return 'badge-info'
        else:
            return 'badge-secondary'
    
    def validate(self):
        """Validate participation data"""
        errors = []
        
        # Validate student_id
        if not self.student_id:
            errors.append("Student ID is required")
        
        # Validate course
        if not self.course or len(self.course.strip()) < 2:
            errors.append("Course must be specified")
        elif len(self.course) > 100:
            errors.append("Course name must be less than 100 characters")
        
        # Validate activity_type
        valid_types = ['Discussion', 'Presentation', 'Question', 'Assignment', 'Quiz', 'Project']
        if not self.activity_type or self.activity_type not in valid_types:
            errors.append("Invalid activity type")
        
        # Validate activity_date
        if not self.activity_date:
            errors.append("Activity date is required")
        elif self.activity_date > date.today():
            errors.append("Activity date cannot be in the future")
        
        # Validate points
        if self.points is None:
            errors.append("Points value is required")
        elif not isinstance(self.points, (int, float)):
            errors.append("Points must be a number")
        elif self.points < 0:
            errors.append("Points cannot be negative")
        elif self.points > 100:
            errors.append("Points cannot exceed 100")
        
        # Validate description length
        if self.description and len(self.description) > 1000:
            errors.append("Description must be less than 1000 characters")
        
        return errors
    
    def to_dict(self):
        """Convert participation to dictionary"""
        return {
            'participation_id': self.participation_id,
            'student_id': self.student_id,
            'course': self.course,
            'activity_type': self.activity_type,
            'activity_date': self.activity_date.isoformat() if self.activity_date else None,
            'points': self.points,
            'description': self.description,
            'recorded_by': self.recorded_by,
            'recorded_at': self.recorded_at.isoformat() if self.recorded_at else None,
            'activity_color': self.get_activity_color(),
            'activity_icon': self.get_activity_icon(),
            'points_badge_class': self.get_points_badge_class()
        }
    
    def __repr__(self):
        return f"<Participation {self.student_id} - {self.activity_type} ({self.points} pts)>"

