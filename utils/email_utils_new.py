import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os
from datetime import datetime
import secrets

# Gmail SMTP Configuration
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USERNAME = os.environ.get('GMAIL_USERNAME', 'your-email@gmail.com')
SMTP_PASSWORD = os.environ.get('GMAIL_APP_PASSWORD', 'your-app-password')

def send_email(to_email, subject, html_content, text_content=None, attachments=None):
    """
    Send email using Gmail SMTP
    
    Args:
        to_email (str): Recipient email address
        subject (str): Email subject
        html_content (str): HTML content of the email
        text_content (str): Plain text content (optional)
        attachments (list): List of file paths to attach (optional)
    
    Returns:
        bool: True if email sent successfully, False otherwise
    """
    try:
        # Create message
        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = SMTP_USERNAME
        message["To"] = to_email
        
        # Add text content
        if text_content:
            text_part = MIMEText(text_content, "plain")
            message.attach(text_part)
        
        # Add HTML content
        html_part = MIMEText(html_content, "html")
        message.attach(html_part)
        
        # Add attachments if provided
        if attachments:
            for file_path in attachments:
                if os.path.exists(file_path):
                    with open(file_path, "rb") as attachment:
                        part = MIMEBase('application', 'octet-stream')
                        part.set_payload(attachment.read())
                    
                    encoders.encode_base64(part)
                    part.add_header(
                        'Content-Disposition',
                        f'attachment; filename= {os.path.basename(file_path)}'
                    )
                    message.attach(part)
        
        # Create secure connection and send email
        context = ssl.create_default_context()
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls(context=context)
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.sendmail(SMTP_USERNAME, to_email, message.as_string())
        
        print(f"Email sent successfully to {to_email}")
        return True
        
    except Exception as e:
        print(f"Error sending email to {to_email}: {str(e)}")
        return False

def send_verification_email(user_email, user_name, verification_token, base_url):
    """Send email verification email"""
    verification_url = f"{base_url}/verify-email?token={verification_token}"
    
    subject = "Verify Your University Account"
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Email Verification</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                line-height: 1.6;
                color: #333;
                max-width: 600px;
                margin: 0 auto;
                padding: 20px;
            }}
            .header {{
                background: linear-gradient(135deg, #2c3e50, #3498db);
                color: white;
                padding: 30px;
                text-align: center;
                border-radius: 10px 10px 0 0;
            }}
            .content {{
                background: #f8f9fa;
                padding: 30px;
                border-radius: 0 0 10px 10px;
                border: 1px solid #e9ecef;
            }}
            .button {{
                display: inline-block;
                padding: 12px 30px;
                background: linear-gradient(135deg, #27ae60, #2ecc71);
                color: white;
                text-decoration: none;
                border-radius: 5px;
                font-weight: bold;
                margin: 20px 0;
            }}
            .button:hover {{
                background: linear-gradient(135deg, #229954, #27ae60);
            }}
            .footer {{
                text-align: center;
                margin-top: 30px;
                padding-top: 20px;
                border-top: 1px solid #e9ecef;
                color: #6c757d;
                font-size: 0.9em;
            }}
            .warning {{
                background: #fff3cd;
                border: 1px solid #ffeaa7;
                border-radius: 5px;
                padding: 15px;
                margin: 20px 0;
                color: #856404;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🎓 University Management System</h1>
            <p>Email Verification Required</p>
        </div>
        
        <div class="content">
            <h2>Hello {user_name}!</h2>
            
            <p>Thank you for registering with our University Management System. To complete your registration and secure your account, please verify your email address by clicking the button below:</p>
            
            <div style="text-align: center;">
                <a href="{verification_url}" class="button">✅ Verify Email Address</a>
            </div>
            
            <p>If the button doesn't work, you can copy and paste this link into your browser:</p>
            <p style="word-break: break-all; background: #e9ecef; padding: 10px; border-radius: 5px; font-family: monospace;">
                {verification_url}
            </p>
            
            <div class="warning">
                <strong>⚠️ Security Notice:</strong>
                <ul>
                    <li>This verification link will expire in 24 hours</li>
                    <li>If you didn't create this account, please ignore this email</li>
                    <li>Never share your login credentials with anyone</li>
                </ul>
            </div>
            
            <p>Once verified, you'll be able to:</p>
            <ul>
                <li>Access your student dashboard</li>
                <li>Register for courses</li>
                <li>View your academic records</li>
                <li>Receive important notifications</li>
            </ul>
        </div>
        
        <div class="footer">
            <p>This email was sent from University Management System</p>
            <p>Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
    </body>
    </html>
    """
    
    text_content = f"""
    University Management System - Email Verification
    
    Hello {user_name}!
    
    Thank you for registering with our University Management System. 
    Please verify your email address by visiting this link:
    
    {verification_url}
    
    This verification link will expire in 24 hours.
    
    If you didn't create this account, please ignore this email.
    
    Best regards,
    University Management System Team
    """
    
    return send_email(user_email, subject, html_content, text_content)

def generate_2fa_code():
    """Generate a 6-digit 2FA code"""
    return f"{secrets.randbelow(900000) + 100000:06d}"

def send_2fa_email(user_email, user_name, code):
    """Send 2FA verification code email"""
    subject = "Two-Factor Authentication Code"
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>2FA Code</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                line-height: 1.6;
                color: #333;
                max-width: 600px;
                margin: 0 auto;
                padding: 20px;
            }}
            .header {{
                background: linear-gradient(135deg, #9b59b6, #8e44ad);
                color: white;
                padding: 30px;
                text-align: center;
                border-radius: 10px 10px 0 0;
            }}
            .content {{
                background: #f8f9fa;
                padding: 30px;
                border-radius: 0 0 10px 10px;
                border: 1px solid #e9ecef;
            }}
            .code-box {{
                background: linear-gradient(135deg, #667eea, #764ba2);
                color: white;
                padding: 30px;
                text-align: center;
                border-radius: 10px;
                margin: 20px 0;
                font-size: 2em;
                font-weight: bold;
                letter-spacing: 5px;
                font-family: monospace;
            }}
            .footer {{
                text-align: center;
                margin-top: 30px;
                padding-top: 20px;
                border-top: 1px solid #e9ecef;
                color: #6c757d;
                font-size: 0.9em;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🔐 Two-Factor Authentication</h1>
            <p>Security Code Required</p>
        </div>
        
        <div class="content">
            <h2>Hello {user_name}!</h2>
            
            <p>To complete your login, please enter the following 6-digit verification code:</p>
            
            <div class="code-box">
                {code}
            </div>
            
            <div style="background: #fff3cd; border: 1px solid #ffeaa7; border-radius: 5px; padding: 15px; margin: 20px 0; color: #856404;">
                <strong>⚠️ Security Notice:</strong>
                <ul>
                    <li>This code will expire in 5 minutes</li>
                    <li>Never share this code with anyone</li>
                    <li>If you didn't request this code, please secure your account immediately</li>
                </ul>
            </div>
            
            <p>Enter this code in the verification form to complete your login process.</p>
        </div>
        
        <div class="footer">
            <p>University Management System</p>
            <p>Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
    </body>
    </html>
    """
    
    text_content = f"""
    University Management System - Two-Factor Authentication
    
    Hello {user_name}!
    
    Your verification code is: {code}
    
    This code will expire in 5 minutes.
    Never share this code with anyone.
    
    Enter this code to complete your login.
    
    University Management System Team
    """
    
    return send_email(user_email, subject, html_content, text_content)

def test_email_configuration():
    """Test email configuration"""
    try:
        context = ssl.create_default_context()
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls(context=context)
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
        return True, "Email configuration is working correctly"
    except Exception as e:
        return False, f"Email configuration error: {str(e)}"

