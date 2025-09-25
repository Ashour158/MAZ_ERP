# Enhanced Booking Request DocType - Complete Meeting Management

import frappe
from frappe.model.document import Document
from frappe import _
from frappe.utils import now, get_datetime, add_days, get_time
from frappe.model.naming import make_autoname
import json
from datetime import datetime, timedelta
import requests
import xml.etree.ElementTree as ET

class BookingRequest(Document):
    def autoname(self):
        """Generate unique booking request ID"""
        if not self.booking_id:
            self.booking_id = make_autoname("BRQ-.YYYY.-.MM.-.#####")
        self.name = self.booking_id

    def validate(self):
        """Validate booking request data"""
        self.validate_booking_data()
        self.set_defaults()
        self.validate_time_slots()
        self.validate_participants()
        self.validate_resources()

    def before_save(self):
        """Process before saving"""
        self.calculate_duration()
        self.set_booking_status()
        self.check_conflicts()
        self.generate_meeting_link()

    def after_insert(self):
        """Process after inserting new booking request"""
        self.send_booking_notifications()
        self.create_calendar_event()
        self.update_participant_schedules()
        self.process_approval_workflow()

    def on_update(self):
        """Process on booking request update"""
        self.update_calendar_event()
        self.sync_booking_data()
        self.update_booking_analytics()

    def validate_booking_data(self):
        """Validate booking information"""
        if not self.booking_title:
            frappe.throw(_("Booking title is required"))
        
        if not self.booking_type:
            frappe.throw(_("Booking type is required"))
        
        if not self.start_time:
            frappe.throw(_("Start time is required"))
        
        if not self.end_time:
            frappe.throw(_("End time is required"))
        
        if not self.organizer:
            frappe.throw(_("Organizer is required"))

    def validate_time_slots(self):
        """Validate time slots"""
        if self.start_time >= self.end_time:
            frappe.throw(_("End time must be after start time"))
        
        if self.start_time < now():
            frappe.throw(_("Start time cannot be in the past"))
        
        # Check minimum booking duration
        duration = (self.end_time - self.start_time).total_seconds() / 3600
        if duration < 0.5:  # 30 minutes minimum
            frappe.throw(_("Minimum booking duration is 30 minutes"))

    def validate_participants(self):
        """Validate participants"""
        if not self.participants:
            frappe.throw(_("At least one participant is required"))
        
        # Check for duplicate participants
        participant_emails = [p.email for p in self.participants]
        if len(participant_emails) != len(set(participant_emails)):
            frappe.throw(_("Duplicate participants found"))

    def validate_resources(self):
        """Validate resources"""
        if self.resources:
            for resource in self.resources:
                if not resource.resource_type:
                    frappe.throw(_("Resource type is required for all resources"))
                
                if not resource.resource_name:
                    frappe.throw(_("Resource name is required for all resources"))

    def set_defaults(self):
        """Set default values for new booking request"""
        if not self.booking_type:
            self.booking_type = "Meeting"
        
        if not self.booking_status:
            self.booking_status = "Pending"
        
        if not self.priority:
            self.priority = "Medium"
        
        if not self.booking_category:
            self.booking_category = "Internal"

    def calculate_duration(self):
        """Calculate booking duration"""
        if self.start_time and self.end_time:
            duration = (self.end_time - self.start_time).total_seconds() / 3600
            self.duration = round(duration, 2)
            
            # Set duration in minutes
            self.duration_minutes = int(duration * 60)

    def set_booking_status(self):
        """Set booking status based on conditions"""
        if self.booking_status == "Pending":
            # Check if auto-approval is enabled
            if self.auto_approve:
                self.booking_status = "Approved"
            else:
                self.booking_status = "Pending Approval"
        
        # Check if booking is in the past
        if self.start_time < now():
            self.booking_status = "Completed"

    def check_conflicts(self):
        """Check for booking conflicts"""
        conflicts = self.find_conflicts()
        if conflicts:
            self.conflicts = json.dumps(conflicts)
            self.has_conflicts = 1
        else:
            self.conflicts = None
            self.has_conflicts = 0

    def find_conflicts(self):
        """Find booking conflicts"""
        conflicts = []
        
        # Check for participant conflicts
        for participant in self.participants:
            participant_conflicts = frappe.db.sql("""
                SELECT 
                    br.name,
                    br.booking_title,
                    br.start_time,
                    br.end_time
                FROM `tabBooking Request` br
                JOIN `tabBooking Participant` bp ON br.name = bp.parent
                WHERE bp.email = %s
                AND br.booking_status IN ('Approved', 'Confirmed')
                AND br.name != %s
                AND (
                    (br.start_time <= %s AND br.end_time > %s) OR
                    (br.start_time < %s AND br.end_time >= %s) OR
                    (br.start_time >= %s AND br.end_time <= %s)
                )
            """, (
                participant.email,
                self.name,
                self.start_time, self.start_time,
                self.end_time, self.end_time,
                self.start_time, self.end_time
            ), as_dict=True)
            
            if participant_conflicts:
                conflicts.extend(participant_conflicts)
        
        # Check for resource conflicts
        if self.resources:
            for resource in self.resources:
                resource_conflicts = frappe.db.sql("""
                    SELECT 
                        br.name,
                        br.booking_title,
                        br.start_time,
                        br.end_time
                    FROM `tabBooking Request` br
                    JOIN `tabBooking Resource` br_res ON br.name = br_res.parent
                    WHERE br_res.resource_name = %s
                    AND br.booking_status IN ('Approved', 'Confirmed')
                    AND br.name != %s
                    AND (
                        (br.start_time <= %s AND br.end_time > %s) OR
                        (br.start_time < %s AND br.end_time >= %s) OR
                        (br.start_time >= %s AND br.end_time <= %s)
                    )
                """, (
                    resource.resource_name,
                    self.name,
                    self.start_time, self.start_time,
                    self.end_time, self.end_time,
                    self.start_time, self.end_time
                ), as_dict=True)
                
                if resource_conflicts:
                    conflicts.extend(resource_conflicts)
        
        return conflicts

    def generate_meeting_link(self):
        """Generate meeting link for virtual meetings"""
        if self.booking_type == "Virtual Meeting" or self.is_virtual:
            # Generate unique meeting link
            meeting_id = self.generate_meeting_id()
            self.meeting_link = f"https://meet.erpnext.com/{meeting_id}"
            self.meeting_id = meeting_id

    def generate_meeting_id(self):
        """Generate unique meeting ID"""
        import uuid
        return str(uuid.uuid4())[:8]

    def send_booking_notifications(self):
        """Send booking notifications"""
        # Send notification to organizer
        self.send_organizer_notification()
        
        # Send notifications to participants
        self.send_participant_notifications()
        
        # Send notifications to approvers
        if self.booking_status == "Pending Approval":
            self.send_approver_notifications()

    def send_organizer_notification(self):
        """Send notification to organizer"""
        frappe.get_doc({
            "doctype": "Booking Notification",
            "user": self.organizer,
            "booking_request": self.name,
            "notification_type": "Booking Created",
            "message": f"Booking request {self.booking_id} has been created",
            "is_read": 0,
            "created_date": now()
        }).insert(ignore_permissions=True)

    def send_participant_notifications(self):
        """Send notifications to participants"""
        for participant in self.participants:
            frappe.get_doc({
                "doctype": "Booking Notification",
                "user": participant.email,
                "booking_request": self.name,
                "notification_type": "Meeting Invitation",
                "message": f"You have been invited to {self.booking_title}",
                "is_read": 0,
                "created_date": now()
            }).insert(ignore_permissions=True)

    def send_approver_notifications(self):
        """Send notifications to approvers"""
        approvers = self.get_approvers()
        for approver in approvers:
            frappe.get_doc({
                "doctype": "Booking Notification",
                "user": approver,
                "booking_request": self.name,
                "notification_type": "Approval Required",
                "message": f"Booking request {self.booking_id} requires your approval",
                "is_read": 0,
                "created_date": now()
            }).insert(ignore_permissions=True)

    def get_approvers(self):
        """Get list of approvers"""
        approvers = []
        
        # Get department approvers
        if self.department:
            department_approvers = frappe.db.sql("""
                SELECT approver
                FROM `tabDepartment Approver` 
                WHERE department = %s
            """, self.department, as_dict=True)
            approvers.extend([da.approver for da in department_approvers])
        
        # Get booking type approvers
        booking_type_approvers = frappe.db.sql("""
            SELECT approver
            FROM `tabBooking Type Approver` 
            WHERE booking_type = %s
        """, self.booking_type, as_dict=True)
        approvers.extend([bta.approver for bta in booking_type_approvers])
        
        return list(set(approvers))

    def create_calendar_event(self):
        """Create calendar event"""
        calendar_event = frappe.get_doc({
            "doctype": "Calendar Event",
            "title": self.booking_title,
            "start": self.start_time,
            "end": self.end_time,
            "all_day": 0,
            "event_type": self.booking_type,
            "description": self.description,
            "location": self.location,
            "meeting_link": self.meeting_link,
            "organizer": self.organizer,
            "booking_request": self.name
        })
        calendar_event.insert(ignore_permissions=True)
        
        # Add participants to calendar event
        for participant in self.participants:
            calendar_event.append("attendees", {
                "attendee": participant.email,
                "status": "Invited"
            })
        
        calendar_event.save()

    def update_participant_schedules(self):
        """Update participant schedules"""
        for participant in self.participants:
            # Update participant's calendar
            self.update_participant_calendar(participant.email)
            
            # Send calendar invitation
            self.send_calendar_invitation(participant.email)

    def update_participant_calendar(self, participant_email):
        """Update participant's calendar"""
        # Add to participant's personal calendar
        frappe.get_doc({
            "doctype": "Personal Calendar Event",
            "user": participant_email,
            "title": self.booking_title,
            "start": self.start_time,
            "end": self.end_time,
            "event_type": "Meeting",
            "description": self.description,
            "location": self.location,
            "meeting_link": self.meeting_link,
            "booking_request": self.name
        }).insert(ignore_permissions=True)

    def send_calendar_invitation(self, participant_email):
        """Send calendar invitation"""
        # Generate calendar invitation
        invitation_data = self.generate_calendar_invitation()
        
        # Send email invitation
        self.send_email_invitation(participant_email, invitation_data)

    def generate_calendar_invitation(self):
        """Generate calendar invitation data"""
        return {
            "title": self.booking_title,
            "start": self.start_time.isoformat(),
            "end": self.end_time.isoformat(),
            "location": self.location,
            "description": self.description,
            "meeting_link": self.meeting_link,
            "organizer": self.organizer,
            "participants": [p.email for p in self.participants]
        }

    def send_email_invitation(self, participant_email, invitation_data):
        """Send email invitation"""
        # Send email with calendar invitation
        frappe.sendmail(
            recipients=[participant_email],
            subject=f"Meeting Invitation: {self.booking_title}",
            message=self.generate_email_message(invitation_data),
            reference_doctype=self.doctype,
            reference_name=self.name
        )

    def generate_email_message(self, invitation_data):
        """Generate email message"""
        message = f"""
        <h2>Meeting Invitation</h2>
        <p><strong>Title:</strong> {invitation_data['title']}</p>
        <p><strong>Date:</strong> {invitation_data['start']}</p>
        <p><strong>Duration:</strong> {self.duration} hours</p>
        <p><strong>Location:</strong> {invitation_data['location']}</p>
        <p><strong>Organizer:</strong> {invitation_data['organizer']}</p>
        """
        
        if invitation_data['meeting_link']:
            message += f"<p><strong>Meeting Link:</strong> <a href='{invitation_data['meeting_link']}'>{invitation_data['meeting_link']}</a></p>"
        
        if invitation_data['description']:
            message += f"<p><strong>Description:</strong> {invitation_data['description']}</p>"
        
        return message

    def process_approval_workflow(self):
        """Process approval workflow"""
        if self.booking_status == "Pending Approval":
            # Create approval request
            approval_request = frappe.get_doc({
                "doctype": "Booking Approval",
                "booking_request": self.name,
                "approver": self.get_primary_approver(),
                "approval_status": "Pending",
                "requested_date": now(),
                "approval_notes": self.approval_notes
            })
            approval_request.insert(ignore_permissions=True)

    def get_primary_approver(self):
        """Get primary approver"""
        approvers = self.get_approvers()
        if approvers:
            return approvers[0]
        return None

    def update_calendar_event(self):
        """Update calendar event"""
        calendar_event = frappe.get_doc("Calendar Event", {"booking_request": self.name})
        if calendar_event:
            calendar_event.title = self.booking_title
            calendar_event.start = self.start_time
            calendar_event.end = self.end_time
            calendar_event.description = self.description
            calendar_event.location = self.location
            calendar_event.meeting_link = self.meeting_link
            calendar_event.save()

    def sync_booking_data(self):
        """Sync booking data across systems"""
        # Sync with external calendar systems
        if self.external_calendar_id:
            self.sync_with_external_calendar()

    def update_booking_analytics(self):
        """Update booking analytics"""
        # Calculate booking metrics
        metrics = self.calculate_booking_metrics()
        
        # Update analytics
        frappe.db.set_value("Booking Request", self.name, "analytics", json.dumps(metrics))

    def calculate_booking_metrics(self):
        """Calculate booking metrics"""
        return {
            "duration": self.duration,
            "participant_count": len(self.participants),
            "resource_count": len(self.resources) if self.resources else 0,
            "conflict_count": len(json.loads(self.conflicts)) if self.conflicts else 0,
            "approval_time": self.calculate_approval_time(),
            "last_updated": now().isoformat()
        }

    def calculate_approval_time(self):
        """Calculate approval time"""
        if self.booking_status == "Approved":
            approval_time = frappe.db.get_value("Booking Approval", 
                {"booking_request": self.name, "approval_status": "Approved"}, 
                "approved_date")
            if approval_time:
                return (approval_time - self.creation).total_seconds() / 3600
        return 0

    def sync_with_external_calendar(self):
        """Sync with external calendar"""
        # Implementation for external calendar sync
        pass

    @frappe.whitelist()
    def approve_booking(self, approver, approval_notes=None):
        """Approve booking request"""
        if self.booking_status != "Pending Approval":
            frappe.throw(_("Booking request is not pending approval"))
        
        # Update approval record
        approval = frappe.get_doc("Booking Approval", {
            "booking_request": self.name,
            "approver": approver
        })
        approval.approval_status = "Approved"
        approval.approved_date = now()
        approval.approval_notes = approval_notes
        approval.save()
        
        # Update booking status
        self.booking_status = "Approved"
        self.save()
        
        # Send approval notifications
        self.send_approval_notifications()
        
        return {"status": "success", "message": "Booking request approved"}

    @frappe.whitelist()
    def reject_booking(self, approver, rejection_reason):
        """Reject booking request"""
        if self.booking_status != "Pending Approval":
            frappe.throw(_("Booking request is not pending approval"))
        
        # Update approval record
        approval = frappe.get_doc("Booking Approval", {
            "booking_request": self.name,
            "approver": approver
        })
        approval.approval_status = "Rejected"
        approval.rejected_date = now()
        approval.rejection_reason = rejection_reason
        approval.save()
        
        # Update booking status
        self.booking_status = "Rejected"
        self.save()
        
        # Send rejection notifications
        self.send_rejection_notifications()
        
        return {"status": "success", "message": "Booking request rejected"}

    def send_approval_notifications(self):
        """Send approval notifications"""
        # Notify organizer
        frappe.get_doc({
            "doctype": "Booking Notification",
            "user": self.organizer,
            "booking_request": self.name,
            "notification_type": "Booking Approved",
            "message": f"Booking request {self.booking_id} has been approved",
            "is_read": 0,
            "created_date": now()
        }).insert(ignore_permissions=True)
        
        # Notify participants
        for participant in self.participants:
            frappe.get_doc({
                "doctype": "Booking Notification",
                "user": participant.email,
                "booking_request": self.name,
                "notification_type": "Meeting Confirmed",
                "message": f"Meeting {self.booking_title} has been confirmed",
                "is_read": 0,
                "created_date": now()
            }).insert(ignore_permissions=True)

    def send_rejection_notifications(self):
        """Send rejection notifications"""
        # Notify organizer
        frappe.get_doc({
            "doctype": "Booking Notification",
            "user": self.organizer,
            "booking_request": self.name,
            "notification_type": "Booking Rejected",
            "message": f"Booking request {self.booking_id} has been rejected",
            "is_read": 0,
            "created_date": now()
        }).insert(ignore_permissions=True)

    @frappe.whitelist()
    def cancel_booking(self, cancellation_reason):
        """Cancel booking request"""
        if self.booking_status in ["Completed", "Cancelled"]:
            frappe.throw(_("Cannot cancel completed or already cancelled booking"))
        
        # Update booking status
        self.booking_status = "Cancelled"
        self.cancellation_reason = cancellation_reason
        self.cancelled_date = now()
        self.save()
        
        # Update calendar event
        calendar_event = frappe.get_doc("Calendar Event", {"booking_request": self.name})
        if calendar_event:
            calendar_event.event_type = "Cancelled"
            calendar_event.save()
        
        # Send cancellation notifications
        self.send_cancellation_notifications()
        
        return {"status": "success", "message": "Booking request cancelled"}

    def send_cancellation_notifications(self):
        """Send cancellation notifications"""
        # Notify all participants
        for participant in self.participants:
            frappe.get_doc({
                "doctype": "Booking Notification",
                "user": participant.email,
                "booking_request": self.name,
                "notification_type": "Meeting Cancelled",
                "message": f"Meeting {self.booking_title} has been cancelled",
                "is_read": 0,
                "created_date": now()
            }).insert(ignore_permissions=True)

    @frappe.whitelist()
    def get_booking_availability(self, start_time, end_time, participants=None, resources=None):
        """Get booking availability"""
        # Check participant availability
        participant_availability = self.check_participant_availability(start_time, end_time, participants)
        
        # Check resource availability
        resource_availability = self.check_resource_availability(start_time, end_time, resources)
        
        return {
            "participant_availability": participant_availability,
            "resource_availability": resource_availability,
            "is_available": participant_availability["is_available"] and resource_availability["is_available"]
        }

    def check_participant_availability(self, start_time, end_time, participants):
        """Check participant availability"""
        if not participants:
            return {"is_available": True, "conflicts": []}
        
        conflicts = []
        for participant in participants:
            participant_conflicts = frappe.db.sql("""
                SELECT 
                    br.name,
                    br.booking_title,
                    br.start_time,
                    br.end_time
                FROM `tabBooking Request` br
                JOIN `tabBooking Participant` bp ON br.name = bp.parent
                WHERE bp.email = %s
                AND br.booking_status IN ('Approved', 'Confirmed')
                AND (
                    (br.start_time <= %s AND br.end_time > %s) OR
                    (br.start_time < %s AND br.end_time >= %s) OR
                    (br.start_time >= %s AND br.end_time <= %s)
                )
            """, (
                participant,
                start_time, start_time,
                end_time, end_time,
                start_time, end_time
            ), as_dict=True)
            
            if participant_conflicts:
                conflicts.extend(participant_conflicts)
        
        return {
            "is_available": len(conflicts) == 0,
            "conflicts": conflicts
        }

    def check_resource_availability(self, start_time, end_time, resources):
        """Check resource availability"""
        if not resources:
            return {"is_available": True, "conflicts": []}
        
        conflicts = []
        for resource in resources:
            resource_conflicts = frappe.db.sql("""
                SELECT 
                    br.name,
                    br.booking_title,
                    br.start_time,
                    br.end_time
                FROM `tabBooking Request` br
                JOIN `tabBooking Resource` br_res ON br.name = br_res.parent
                WHERE br_res.resource_name = %s
                AND br.booking_status IN ('Approved', 'Confirmed')
                AND (
                    (br.start_time <= %s AND br.end_time > %s) OR
                    (br.start_time < %s AND br.end_time >= %s) OR
                    (br.start_time >= %s AND br.end_time <= %s)
                )
            """, (
                resource,
                start_time, start_time,
                end_time, end_time,
                start_time, end_time
            ), as_dict=True)
            
            if resource_conflicts:
                conflicts.extend(resource_conflicts)
        
        return {
            "is_available": len(conflicts) == 0,
            "conflicts": conflicts
        }
