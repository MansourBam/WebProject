import re
from config import ALLOWED_COUNTRIES, ALLOWED_MAJORS

def validate_email(email):
    """Validate email format"""
    if not email:
        return False, "Email is required"
    
    if not re.match(r'^[^@\s]+@[^@\s]+\.[^@\s]+$', email):
        return False, "Please enter a valid email address"
    
    if len(email) > 100:
        return False, "Email must be less than 100 characters"
    
    return True, ""

def validate_password(password):
    """Validate password strength"""
    if not password:
        return False, "Password is required"
    
    if len(password) < 6:
        return False, "Password must be at least 6 characters long"
    
    if len(password) > 255:
        return False, "Password must be less than 255 characters"
    
    return True, ""

def validate_name(name):
    """Validate name format"""
    if not name:
        return False, "Name is required"
    
    name = name.strip()
    if len(name) < 3:
        return False, "Name must be at least 3 characters long"
    
    if len(name) > 100:
        return False, "Name must be less than 100 characters"
    
    return True, ""

def validate_university_number(university_number):
    """Validate university number format"""
    if not university_number:
        return False, "University number is required"
    
    if not re.match(r'^[0-9]{7,10}$', university_number):
        return False, "University number must be 7-10 digits"
    
    return True, ""

def validate_phone(phone):
    """Validate phone number format (optional field)"""
    if not phone:
        return True, ""  # Phone is optional
    
    if not re.match(r'^\+?[0-9\s\-\(\)]{10,20}$', phone):
        return False, "Please enter a valid phone number"
    
    return True, ""

def validate_nationality(nationality):
    """Validate nationality selection"""
    if not nationality:
        return False, "Nationality is required"
    
    if nationality not in ALLOWED_COUNTRIES:
        return False, "Please select a valid nationality"
    
    return True, ""

def validate_major(major):
    """Validate major selection"""
    if not major:
        return False, "Major is required"
    
    if major not in ALLOWED_MAJORS:
        return False, "Please select a valid major"
    
    return True, ""

def validate_status(status):
    """Validate status selection"""
    if not status:
        return False, "Status is required"
    
    if status not in ['Active', 'Inactive', 'Graduated']:
        return False, "Please select a valid status"
    
    return True, ""

def validate_gender(gender):
    """Validate gender selection"""
    if not gender:
        return False, "Gender is required"
    
    if gender not in ['Male', 'Female']:
        return False, "Please select a valid gender"
    
    return True, ""

def validate_role(role):
    """Validate role selection"""
    if not role:
        return False, "Role is required"
    
    if role not in ['student', 'teacher', 'admin']:
        return False, "Please select a valid role"
    
    return True, ""

def validate_form_data(data, required_fields):
    """Validate form data against required fields"""
    errors = []
    
    for field, validator in required_fields.items():
        value = data.get(field, '').strip() if isinstance(data.get(field), str) else data.get(field)
        
        if validator == 'email':
            valid, message = validate_email(value)
        elif validator == 'password':
            valid, message = validate_password(value)
        elif validator == 'name':
            valid, message = validate_name(value)
        elif validator == 'university_number':
            valid, message = validate_university_number(value)
        elif validator == 'phone':
            valid, message = validate_phone(value)
        elif validator == 'nationality':
            valid, message = validate_nationality(value)
        elif validator == 'major':
            valid, message = validate_major(value)
        elif validator == 'status':
            valid, message = validate_status(value)
        elif validator == 'gender':
            valid, message = validate_gender(value)
        elif validator == 'role':
            valid, message = validate_role(value)
        else:
            continue
        
        if not valid:
            errors.append(message)
    
    return errors

