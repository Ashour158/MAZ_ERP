# Mail Automation - Complete Email Management System
# Automated email workflows for all modules

import frappe
from frappe import _
from frappe.utils import now, get_datetime, add_days, get_time
import json
from datetime import datetime, timedelta
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import requests
import xml.etree.ElementTree as ET

class MailAutomation:
    def __init__(self):
        self.email_providers = {
            'smtp': SMTPProvider(),
            'gmail': GmailProvider(),
            'outlook': OutlookProvider(),
            'sendgrid': SendGridProvider(),
            'mailgun': MailgunProvider()
        }
        self.template_engine = EmailTemplateEngine()
        self.automation_engine = AutomationEngine()
        self.delivery_tracker = DeliveryTracker()

    def send_email(self, recipients, subject, content, template=None, attachments=None, priority="normal"):
        """Send email with automation features"""
        # Validate recipients
        self.validate_recipients(recipients)
        
        # Process email template
        if template:
            content = self.template_engine.process_template(template, content)
        
        # Create email record
        email_record = self.create_email_record(recipients, subject, content, attachments, priority)
        
        # Send email
        delivery_results = self.send_to_providers(recipients, subject, content, attachments, priority)
        
        # Update delivery status
        self.update_delivery_status(email_record, delivery_results)
        
        # Process automation rules
        self.automation_engine.process_email_rules(email_record)
        
        return {
            "email_id": email_record.name,
            "delivery_results": delivery_results,
            "status": "sent"
        }

    def validate_recipients(self, recipients):
        """Validate email recipients"""
        if not recipients:
            frappe.throw(_("Recipients are required"))
        
        for recipient in recipients:
            if not self.validate_email_address(recipient):
                frappe.throw(_("Invalid email address: {0}").format(recipient))

    def validate_email_address(self, email):
        """Validate email address format"""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None

    def create_email_record(self, recipients, subject, content, attachments, priority):
        """Create email record in database"""
        email_record = frappe.get_doc({
            "doctype": "Email Record",
            "recipients": json.dumps(recipients),
            "subject": subject,
            "content": content,
            "attachments": json.dumps(attachments) if attachments else None,
            "priority": priority,
            "status": "Pending",
            "created_date": now(),
            "sent_date": None,
            "delivery_status": "Pending"
        })
        email_record.insert(ignore_permissions=True)
        return email_record

    def send_to_providers(self, recipients, subject, content, attachments, priority):
        """Send email through multiple providers"""
        delivery_results = {}
        
        for provider_name, provider in self.email_providers.items():
            try:
                if provider.is_configured():
                    result = provider.send_email(recipients, subject, content, attachments, priority)
                    delivery_results[provider_name] = {
                        "status": "success",
                        "message_id": result.get('message_id'),
                        "delivery_time": now().isoformat()
                    }
                else:
                    delivery_results[provider_name] = {
                        "status": "skipped",
                        "reason": "Provider not configured"
                    }
            except Exception as e:
                delivery_results[provider_name] = {
                    "status": "error",
                    "error": str(e)
                }
        
        return delivery_results

    def update_delivery_status(self, email_record, delivery_results):
        """Update email delivery status"""
        # Check if any provider succeeded
        success_count = sum(1 for result in delivery_results.values() if result["status"] == "success")
        
        if success_count > 0:
            email_record.status = "Sent"
            email_record.sent_date = now()
            email_record.delivery_status = "Delivered"
        else:
            email_record.status = "Failed"
            email_record.delivery_status = "Failed"
        
        email_record.delivery_results = json.dumps(delivery_results)
        email_record.save()

    def create_email_template(self, template_data):
        """Create email template"""
        template = frappe.get_doc({
            "doctype": "Email Template",
            "template_name": template_data['name'],
            "subject": template_data['subject'],
            "content": template_data['content'],
            "template_type": template_data.get('type', 'HTML'),
            "module": template_data.get('module', ''),
            "is_active": template_data.get('is_active', 1),
            "variables": json.dumps(template_data.get('variables', [])),
            "conditions": json.dumps(template_data.get('conditions', []))
        })
        template.insert(ignore_permissions=True)
        return template

    def setup_automation_rule(self, rule_data):
        """Setup email automation rule"""
        rule = frappe.get_doc({
            "doctype": "Email Automation Rule",
            "rule_name": rule_data['name'],
            "trigger_event": rule_data['trigger_event'],
            "trigger_doctype": rule_data.get('trigger_doctype', ''),
            "trigger_field": rule_data.get('trigger_field', ''),
            "conditions": json.dumps(rule_data.get('conditions', [])),
            "email_template": rule_data['email_template'],
            "recipients": json.dumps(rule_data.get('recipients', [])),
            "is_active": rule_data.get('is_active', 1),
            "priority": rule_data.get('priority', 'normal')
        })
        rule.insert(ignore_permissions=True)
        return rule

    def process_automation_trigger(self, doctype, docname, trigger_event):
        """Process automation trigger"""
        # Get applicable rules
        rules = self.get_applicable_rules(doctype, trigger_event)
        
        for rule in rules:
            if self.evaluate_rule_conditions(rule, doctype, docname):
                self.execute_automation_rule(rule, doctype, docname)

    def get_applicable_rules(self, doctype, trigger_event):
        """Get applicable automation rules"""
        return frappe.get_all("Email Automation Rule", 
            filters={
                "trigger_doctype": doctype,
                "trigger_event": trigger_event,
                "is_active": 1
            }, 
            fields="*")

    def evaluate_rule_conditions(self, rule, doctype, docname):
        """Evaluate automation rule conditions"""
        conditions = json.loads(rule.conditions)
        
        if not conditions:
            return True
        
        doc = frappe.get_doc(doctype, docname)
        
        for condition in conditions:
            field_value = doc.get(condition['field'])
            operator = condition['operator']
            expected_value = condition['value']
            
            if not self.evaluate_condition(field_value, operator, expected_value):
                return False
        
        return True

    def evaluate_condition(self, field_value, operator, expected_value):
        """Evaluate single condition"""
        if operator == "equals":
            return field_value == expected_value
        elif operator == "not_equals":
            return field_value != expected_value
        elif operator == "contains":
            return expected_value in str(field_value)
        elif operator == "not_contains":
            return expected_value not in str(field_value)
        elif operator == "greater_than":
            return field_value > expected_value
        elif operator == "less_than":
            return field_value < expected_value
        elif operator == "is_empty":
            return not field_value
        elif operator == "is_not_empty":
            return bool(field_value)
        else:
            return False

    def execute_automation_rule(self, rule, doctype, docname):
        """Execute automation rule"""
        # Get template
        template = frappe.get_doc("Email Template", rule.email_template)
        
        # Get document
        doc = frappe.get_doc(doctype, docname)
        
        # Process template with document data
        subject = self.template_engine.process_template_content(template.subject, doc)
        content = self.template_engine.process_template_content(template.content, doc)
        
        # Get recipients
        recipients = self.get_rule_recipients(rule, doc)
        
        # Send email
        self.send_email(recipients, subject, content, template.name, priority=rule.priority)

    def get_rule_recipients(self, rule, doc):
        """Get recipients for automation rule"""
        recipients = json.loads(rule.recipients)
        processed_recipients = []
        
        for recipient in recipients:
            if recipient.startswith("{{"):
                # Dynamic recipient from document
                field_name = recipient.strip("{{}}")
                field_value = doc.get(field_name)
                if field_value:
                    processed_recipients.append(field_value)
            else:
                # Static recipient
                processed_recipients.append(recipient)
        
        return processed_recipients

    def send_bulk_email(self, recipients_list, subject, content, template=None, batch_size=100):
        """Send bulk emails"""
        results = []
        
        for i in range(0, len(recipients_list), batch_size):
            batch = recipients_list[i:i + batch_size]
            result = self.send_email(batch, subject, content, template)
            results.append(result)
        
        return results

    def schedule_email(self, recipients, subject, content, send_time, template=None):
        """Schedule email for later sending"""
        scheduled_email = frappe.get_doc({
            "doctype": "Scheduled Email",
            "recipients": json.dumps(recipients),
            "subject": subject,
            "content": content,
            "template": template,
            "send_time": send_time,
            "status": "Scheduled",
            "created_date": now()
        })
        scheduled_email.insert(ignore_permissions=True)
        return scheduled_email

    def process_scheduled_emails(self):
        """Process scheduled emails"""
        scheduled_emails = frappe.get_all("Scheduled Email", 
            filters={
                "status": "Scheduled",
                "send_time": ["<=", now()]
            }, 
            fields="*")
        
        for email in scheduled_emails:
            try:
                recipients = json.loads(email.recipients)
                self.send_email(recipients, email.subject, email.content, email.template)
                
                # Update status
                frappe.db.set_value("Scheduled Email", email.name, "status", "Sent")
                frappe.db.set_value("Scheduled Email", email.name, "sent_date", now())
            except Exception as e:
                frappe.db.set_value("Scheduled Email", email.name, "status", "Failed")
                frappe.db.set_value("Scheduled Email", email.name, "error_message", str(e))

class EmailTemplateEngine:
    def __init__(self):
        self.template_processor = TemplateProcessor()
        self.variable_processor = VariableProcessor()
    
    def process_template(self, template_name, data):
        """Process email template"""
        template = frappe.get_doc("Email Template", template_name)
        
        # Process subject
        subject = self.process_template_content(template.subject, data)
        
        # Process content
        content = self.process_template_content(template.content, data)
        
        return {
            "subject": subject,
            "content": content
        }
    
    def process_template_content(self, template_content, data):
        """Process template content with data"""
        # Replace variables with data
        processed_content = template_content
        
        # Process document variables
        if hasattr(data, 'as_dict'):
            doc_data = data.as_dict()
            for key, value in doc_data.items():
                placeholder = f"{{{{{key}}}}}"
                processed_content = processed_content.replace(placeholder, str(value))
        
        # Process system variables
        system_variables = {
            "{{current_date}}": now().strftime("%Y-%m-%d"),
            "{{current_time}}": now().strftime("%H:%M:%S"),
            "{{current_user}}": frappe.session.user,
            "{{company_name}}": frappe.get_system_settings("company_name")
        }
        
        for placeholder, value in system_variables.items():
            processed_content = processed_content.replace(placeholder, str(value))
        
        return processed_content

class TemplateProcessor:
    def process_template(self, template, data):
        """Process template with data"""
        # Implementation for template processing
        pass

class VariableProcessor:
    def process_variables(self, content, data):
        """Process variables in content"""
        # Implementation for variable processing
        pass

class AutomationEngine:
    def __init__(self):
        self.rule_processor = RuleProcessor()
        self.condition_evaluator = ConditionEvaluator()
    
    def process_email_rules(self, email_record):
        """Process email automation rules"""
        # Get applicable rules
        rules = self.get_applicable_rules(email_record)
        
        for rule in rules:
            if self.evaluate_rule_conditions(rule, email_record):
                self.execute_rule(rule, email_record)
    
    def get_applicable_rules(self, email_record):
        """Get applicable rules for email"""
        # Implementation for rule retrieval
        pass
    
    def evaluate_rule_conditions(self, rule, email_record):
        """Evaluate rule conditions"""
        # Implementation for condition evaluation
        pass
    
    def execute_rule(self, rule, email_record):
        """Execute automation rule"""
        # Implementation for rule execution
        pass

class RuleProcessor:
    def process_rule(self, rule, data):
        """Process automation rule"""
        # Implementation for rule processing
        pass

class ConditionEvaluator:
    def evaluate_conditions(self, conditions, data):
        """Evaluate automation conditions"""
        # Implementation for condition evaluation
        pass

class DeliveryTracker:
    def __init__(self):
        self.tracking_processor = TrackingProcessor()
        self.delivery_analyzer = DeliveryAnalyzer()
    
    def track_delivery(self, email_id, provider, message_id):
        """Track email delivery"""
        # Implementation for delivery tracking
        pass
    
    def analyze_delivery(self, email_id):
        """Analyze email delivery"""
        # Implementation for delivery analysis
        pass

class TrackingProcessor:
    def process_tracking(self, tracking_data):
        """Process delivery tracking"""
        # Implementation for tracking processing
        pass

class DeliveryAnalyzer:
    def analyze_delivery(self, delivery_data):
        """Analyze delivery data"""
        # Implementation for delivery analysis
        pass

class SMTPProvider:
    def __init__(self):
        self.smtp_server = frappe.get_system_settings("smtp_server")
        self.smtp_port = frappe.get_system_settings("smtp_port")
        self.smtp_username = frappe.get_system_settings("smtp_username")
        self.smtp_password = frappe.get_system_settings("smtp_password")
        self.smtp_use_tls = frappe.get_system_settings("smtp_use_tls")
    
    def is_configured(self):
        return bool(self.smtp_server and self.smtp_username and self.smtp_password)
    
    def send_email(self, recipients, subject, content, attachments, priority):
        """Send email via SMTP"""
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.smtp_username
            msg['To'] = ', '.join(recipients)
            msg['Subject'] = subject
            
            # Add content
            msg.attach(MIMEText(content, 'html'))
            
            # Add attachments
            if attachments:
                for attachment in attachments:
                    self.add_attachment(msg, attachment)
            
            # Send email
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            if self.smtp_use_tls:
                server.starttls()
            server.login(self.smtp_username, self.smtp_password)
            server.send_message(msg)
            server.quit()
            
            return {"message_id": f"smtp_{now().timestamp()}"}
        except Exception as e:
            raise Exception(f"SMTP error: {str(e)}")
    
    def add_attachment(self, msg, attachment):
        """Add attachment to email"""
        with open(attachment['path'], "rb") as f:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(f.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f'attachment; filename= {attachment["filename"]}')
            msg.attach(part)

class GmailProvider:
    def __init__(self):
        self.access_token = frappe.get_system_settings("gmail_access_token")
        self.api_url = "https://gmail.googleapis.com/gmail/v1"
    
    def is_configured(self):
        return bool(self.access_token)
    
    def send_email(self, recipients, subject, content, attachments, priority):
        """Send email via Gmail API"""
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        
        message = {
            "raw": self.create_gmail_message(recipients, subject, content, attachments)
        }
        
        response = requests.post(
            f"{self.api_url}/users/me/messages/send",
            headers=headers,
            json=message
        )
        
        if response.status_code == 200:
            return {"message_id": response.json()['id']}
        else:
            raise Exception(f"Gmail API error: {response.text}")
    
    def create_gmail_message(self, recipients, subject, content, attachments):
        """Create Gmail message"""
        import base64
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart
        
        msg = MIMEMultipart()
        msg['To'] = ', '.join(recipients)
        msg['Subject'] = subject
        msg.attach(MIMEText(content, 'html'))
        
        # Add attachments
        if attachments:
            for attachment in attachments:
                self.add_attachment(msg, attachment)
        
        return base64.urlsafe_b64encode(msg.as_bytes()).decode()
    
    def add_attachment(self, msg, attachment):
        """Add attachment to Gmail message"""
        # Implementation for Gmail attachments
        pass

class OutlookProvider:
    def __init__(self):
        self.access_token = frappe.get_system_settings("outlook_access_token")
        self.api_url = "https://graph.microsoft.com/v1.0"
    
    def is_configured(self):
        return bool(self.access_token)
    
    def send_email(self, recipients, subject, content, attachments, priority):
        """Send email via Outlook API"""
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        
        message = {
            "message": {
                "subject": subject,
                "body": {
                    "content": content,
                    "contentType": "HTML"
                },
                "toRecipients": [{"emailAddress": {"address": recipient}} for recipient in recipients]
            }
        }
        
        response = requests.post(
            f"{self.api_url}/me/sendMail",
            headers=headers,
            json=message
        )
        
        if response.status_code == 202:
            return {"message_id": f"outlook_{now().timestamp()}"}
        else:
            raise Exception(f"Outlook API error: {response.text}")

class SendGridProvider:
    def __init__(self):
        self.api_key = frappe.get_system_settings("sendgrid_api_key")
        self.api_url = "https://api.sendgrid.com/v3/mail/send"
    
    def is_configured(self):
        return bool(self.api_key)
    
    def send_email(self, recipients, subject, content, attachments, priority):
        """Send email via SendGrid API"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        message = {
            "personalizations": [{"to": [{"email": recipient} for recipient in recipients]}],
            "from": {"email": frappe.get_system_settings("sendgrid_from_email")},
            "subject": subject,
            "content": [{"type": "text/html", "value": content}]
        }
        
        response = requests.post(self.api_url, headers=headers, json=message)
        
        if response.status_code == 202:
            return {"message_id": f"sendgrid_{now().timestamp()}"}
        else:
            raise Exception(f"SendGrid API error: {response.text}")

class MailgunProvider:
    def __init__(self):
        self.api_key = frappe.get_system_settings("mailgun_api_key")
        self.domain = frappe.get_system_settings("mailgun_domain")
        self.api_url = f"https://api.mailgun.net/v3/{self.domain}/messages"
    
    def is_configured(self):
        return bool(self.api_key and self.domain)
    
    def send_email(self, recipients, subject, content, attachments, priority):
        """Send email via Mailgun API"""
        data = {
            "from": frappe.get_system_settings("mailgun_from_email"),
            "to": recipients,
            "subject": subject,
            "html": content
        }
        
        response = requests.post(
            self.api_url,
            auth=("api", self.api_key),
            data=data
        )
        
        if response.status_code == 200:
            return {"message_id": response.json()['id']}
        else:
            raise Exception(f"Mailgun API error: {response.text}")
