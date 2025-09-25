# Calendar Integration - Universal Calendar System
# Integrates with all modules for comprehensive calendar management

import frappe
from frappe import _
from frappe.utils import now, get_datetime, add_days, get_time
import json
from datetime import datetime, timedelta
import requests
import xml.etree.ElementTree as ET

class CalendarIntegration:
    def __init__(self):
        self.calendar_providers = {
            'google': GoogleCalendarProvider(),
            'outlook': OutlookCalendarProvider(),
            'apple': AppleCalendarProvider(),
            'exchange': ExchangeCalendarProvider()
        }
        self.sync_engine = CalendarSyncEngine()
        self.conflict_resolver = CalendarConflictResolver()

    def create_calendar_event(self, event_data):
        """Create calendar event across all integrated systems"""
        # Validate event data
        self.validate_event_data(event_data)
        
        # Create event in ERPNext
        erpnext_event = self.create_erpnext_event(event_data)
        
        # Sync with external calendars
        sync_results = self.sync_with_external_calendars(event_data)
        
        # Resolve conflicts
        conflicts = self.conflict_resolver.check_conflicts(event_data)
        
        return {
            "erpnext_event": erpnext_event,
            "sync_results": sync_results,
            "conflicts": conflicts
        }

    def validate_event_data(self, event_data):
        """Validate calendar event data"""
        required_fields = ['title', 'start_time', 'end_time', 'organizer']
        for field in required_fields:
            if not event_data.get(field):
                frappe.throw(_("Field {0} is required").format(field))
        
        if event_data['start_time'] >= event_data['end_time']:
            frappe.throw(_("End time must be after start time"))

    def create_erpnext_event(self, event_data):
        """Create event in ERPNext calendar"""
        event = frappe.get_doc({
            "doctype": "Calendar Event",
            "title": event_data['title'],
            "start": event_data['start_time'],
            "end": event_data['end_time'],
            "all_day": event_data.get('all_day', 0),
            "event_type": event_data.get('event_type', 'Meeting'),
            "description": event_data.get('description', ''),
            "location": event_data.get('location', ''),
            "organizer": event_data['organizer'],
            "meeting_link": event_data.get('meeting_link', ''),
            "recurrence": event_data.get('recurrence', ''),
            "reminder": event_data.get('reminder', ''),
            "visibility": event_data.get('visibility', 'Public'),
            "module": event_data.get('module', ''),
            "reference_doctype": event_data.get('reference_doctype', ''),
            "reference_name": event_data.get('reference_name', '')
        })
        
        # Add attendees
        if event_data.get('attendees'):
            for attendee in event_data['attendees']:
                event.append("attendees", {
                    "attendee": attendee['email'],
                    "status": attendee.get('status', 'Invited')
                })
        
        event.insert(ignore_permissions=True)
        return event

    def sync_with_external_calendars(self, event_data):
        """Sync event with external calendar providers"""
        sync_results = {}
        
        for provider_name, provider in self.calendar_providers.items():
            try:
                if provider.is_configured():
                    result = provider.create_event(event_data)
                    sync_results[provider_name] = {
                        "status": "success",
                        "external_event_id": result.get('event_id'),
                        "sync_date": now().isoformat()
                    }
                else:
                    sync_results[provider_name] = {
                        "status": "skipped",
                        "reason": "Provider not configured"
                    }
            except Exception as e:
                sync_results[provider_name] = {
                    "status": "error",
                    "error": str(e)
                }
        
        return sync_results

    def update_calendar_event(self, event_id, event_data):
        """Update calendar event across all systems"""
        # Update ERPNext event
        erpnext_event = frappe.get_doc("Calendar Event", event_id)
        self.update_erpnext_event(erpnext_event, event_data)
        
        # Sync with external calendars
        sync_results = self.sync_with_external_calendars(event_data)
        
        return {
            "erpnext_event": erpnext_event,
            "sync_results": sync_results
        }

    def update_erpnext_event(self, event, event_data):
        """Update ERPNext calendar event"""
        event.title = event_data.get('title', event.title)
        event.start = event_data.get('start_time', event.start)
        event.end = event_data.get('end_time', event.end)
        event.description = event_data.get('description', event.description)
        event.location = event_data.get('location', event.location)
        event.meeting_link = event_data.get('meeting_link', event.meeting_link)
        event.save()

    def delete_calendar_event(self, event_id):
        """Delete calendar event from all systems"""
        # Delete ERPNext event
        frappe.delete_doc("Calendar Event", event_id)
        
        # Delete from external calendars
        sync_results = {}
        for provider_name, provider in self.calendar_providers.items():
            try:
                if provider.is_configured():
                    result = provider.delete_event(event_id)
                    sync_results[provider_name] = {
                        "status": "success",
                        "sync_date": now().isoformat()
                    }
            except Exception as e:
                sync_results[provider_name] = {
                    "status": "error",
                    "error": str(e)
                }
        
        return sync_results

    def get_calendar_events(self, user, start_date, end_date, module=None):
        """Get calendar events for user"""
        # Get ERPNext events
        erpnext_events = self.get_erpnext_events(user, start_date, end_date, module)
        
        # Get external calendar events
        external_events = self.get_external_events(user, start_date, end_date)
        
        # Merge and deduplicate events
        all_events = self.merge_events(erpnext_events, external_events)
        
        return all_events

    def get_erpnext_events(self, user, start_date, end_date, module=None):
        """Get ERPNext calendar events"""
        filters = {
            "start": [">=", start_date],
            "end": ["<=", end_date]
        }
        
        if module:
            filters["module"] = module
        
        events = frappe.get_all("Calendar Event", filters=filters, fields="*")
        
        # Get events where user is attendee
        attendee_events = frappe.get_all("Calendar Event Attendee", 
            filters={"attendee": user}, 
            fields=["parent"], 
            as_dict=True)
        
        attendee_event_ids = [ae.parent for ae in attendee_events]
        attendee_events = frappe.get_all("Calendar Event", 
            filters={"name": ["in", attendee_event_ids]}, 
            fields="*")
        
        # Combine events
        all_events = events + attendee_events
        
        # Remove duplicates
        unique_events = []
        seen_ids = set()
        for event in all_events:
            if event.name not in seen_ids:
                unique_events.append(event)
                seen_ids.add(event.name)
        
        return unique_events

    def get_external_events(self, user, start_date, end_date):
        """Get external calendar events"""
        external_events = []
        
        for provider_name, provider in self.calendar_providers.items():
            try:
                if provider.is_configured():
                    events = provider.get_events(user, start_date, end_date)
                    external_events.extend(events)
            except Exception as e:
                frappe.log_error(f"Error getting {provider_name} events: {str(e)}")
        
        return external_events

    def merge_events(self, erpnext_events, external_events):
        """Merge and deduplicate events"""
        all_events = erpnext_events + external_events
        
        # Remove duplicates based on title, start time, and organizer
        unique_events = []
        seen_events = set()
        
        for event in all_events:
            event_key = (event.get('title', ''), 
                        event.get('start', ''), 
                        event.get('organizer', ''))
            
            if event_key not in seen_events:
                unique_events.append(event)
                seen_events.add(event_key)
        
        return unique_events

    def sync_calendar_data(self, user, provider_name):
        """Sync calendar data for specific user and provider"""
        provider = self.calendar_providers.get(provider_name)
        if not provider or not provider.is_configured():
            return {"status": "error", "message": "Provider not configured"}
        
        try:
            # Get external events
            external_events = provider.get_events(user, 
                now().date() - timedelta(days=30), 
                now().date() + timedelta(days=30))
            
            # Sync events
            sync_results = []
            for event in external_events:
                result = self.sync_external_event(event, user)
                sync_results.append(result)
            
            return {
                "status": "success",
                "synced_events": len(sync_results),
                "results": sync_results
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def sync_external_event(self, external_event, user):
        """Sync external event to ERPNext"""
        # Check if event already exists
        existing_event = frappe.db.exists("Calendar Event", {
            "external_event_id": external_event.get('id'),
            "organizer": user
        })
        
        if existing_event:
            return {"status": "skipped", "reason": "Event already exists"}
        
        # Create ERPNext event
        event_data = {
            "title": external_event.get('title', ''),
            "start_time": external_event.get('start', ''),
            "end_time": external_event.get('end', ''),
            "description": external_event.get('description', ''),
            "location": external_event.get('location', ''),
            "organizer": user,
            "external_event_id": external_event.get('id'),
            "external_provider": external_event.get('provider', ''),
            "module": "Calendar Integration"
        }
        
        try:
            event = self.create_erpnext_event(event_data)
            return {"status": "success", "event_id": event.name}
        except Exception as e:
            return {"status": "error", "error": str(e)}

class GoogleCalendarProvider:
    def __init__(self):
        self.api_url = "https://www.googleapis.com/calendar/v3"
        self.access_token = frappe.get_system_settings("google_calendar_access_token")
    
    def is_configured(self):
        return bool(self.access_token)
    
    def create_event(self, event_data):
        """Create event in Google Calendar"""
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        
        google_event = {
            "summary": event_data['title'],
            "start": {"dateTime": event_data['start_time'].isoformat()},
            "end": {"dateTime": event_data['end_time'].isoformat()},
            "description": event_data.get('description', ''),
            "location": event_data.get('location', '')
        }
        
        response = requests.post(
            f"{self.api_url}/calendars/primary/events",
            headers=headers,
            json=google_event
        )
        
        if response.status_code == 200:
            return {"event_id": response.json()['id']}
        else:
            raise Exception(f"Google Calendar API error: {response.text}")
    
    def get_events(self, user, start_date, end_date):
        """Get events from Google Calendar"""
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        
        params = {
            "timeMin": start_date.isoformat(),
            "timeMax": end_date.isoformat(),
            "singleEvents": True,
            "orderBy": "startTime"
        }
        
        response = requests.get(
            f"{self.api_url}/calendars/primary/events",
            headers=headers,
            params=params
        )
        
        if response.status_code == 200:
            events = response.json().get('items', [])
            return [self.format_google_event(event) for event in events]
        else:
            raise Exception(f"Google Calendar API error: {response.text}")
    
    def format_google_event(self, google_event):
        """Format Google Calendar event for ERPNext"""
        return {
            "id": google_event['id'],
            "title": google_event.get('summary', ''),
            "start": google_event['start'].get('dateTime', ''),
            "end": google_event['end'].get('dateTime', ''),
            "description": google_event.get('description', ''),
            "location": google_event.get('location', ''),
            "provider": "google"
        }
    
    def delete_event(self, event_id):
        """Delete event from Google Calendar"""
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        
        response = requests.delete(
            f"{self.api_url}/calendars/primary/events/{event_id}",
            headers=headers
        )
        
        if response.status_code != 204:
            raise Exception(f"Google Calendar API error: {response.text}")

class OutlookCalendarProvider:
    def __init__(self):
        self.api_url = "https://graph.microsoft.com/v1.0"
        self.access_token = frappe.get_system_settings("outlook_calendar_access_token")
    
    def is_configured(self):
        return bool(self.access_token)
    
    def create_event(self, event_data):
        """Create event in Outlook Calendar"""
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        
        outlook_event = {
            "subject": event_data['title'],
            "start": {
                "dateTime": event_data['start_time'].isoformat(),
                "timeZone": "UTC"
            },
            "end": {
                "dateTime": event_data['end_time'].isoformat(),
                "timeZone": "UTC"
            },
            "body": {
                "content": event_data.get('description', ''),
                "contentType": "text"
            },
            "location": {
                "displayName": event_data.get('location', '')
            }
        }
        
        response = requests.post(
            f"{self.api_url}/me/events",
            headers=headers,
            json=outlook_event
        )
        
        if response.status_code == 201:
            return {"event_id": response.json()['id']}
        else:
            raise Exception(f"Outlook Calendar API error: {response.text}")
    
    def get_events(self, user, start_date, end_date):
        """Get events from Outlook Calendar"""
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        
        params = {
            "startDateTime": start_date.isoformat(),
            "endDateTime": end_date.isoformat(),
            "orderby": "start/dateTime"
        }
        
        response = requests.get(
            f"{self.api_url}/me/events",
            headers=headers,
            params=params
        )
        
        if response.status_code == 200:
            events = response.json().get('value', [])
            return [self.format_outlook_event(event) for event in events]
        else:
            raise Exception(f"Outlook Calendar API error: {response.text}")
    
    def format_outlook_event(self, outlook_event):
        """Format Outlook Calendar event for ERPNext"""
        return {
            "id": outlook_event['id'],
            "title": outlook_event.get('subject', ''),
            "start": outlook_event['start'].get('dateTime', ''),
            "end": outlook_event['end'].get('dateTime', ''),
            "description": outlook_event.get('body', {}).get('content', ''),
            "location": outlook_event.get('location', {}).get('displayName', ''),
            "provider": "outlook"
        }
    
    def delete_event(self, event_id):
        """Delete event from Outlook Calendar"""
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        
        response = requests.delete(
            f"{self.api_url}/me/events/{event_id}",
            headers=headers
        )
        
        if response.status_code != 204:
            raise Exception(f"Outlook Calendar API error: {response.text}")

class AppleCalendarProvider:
    def __init__(self):
        self.api_url = "https://api.apple.com/calendar"
        self.access_token = frappe.get_system_settings("apple_calendar_access_token")
    
    def is_configured(self):
        return bool(self.access_token)
    
    def create_event(self, event_data):
        """Create event in Apple Calendar"""
        # Implementation for Apple Calendar integration
        pass
    
    def get_events(self, user, start_date, end_date):
        """Get events from Apple Calendar"""
        # Implementation for Apple Calendar integration
        pass
    
    def delete_event(self, event_id):
        """Delete event from Apple Calendar"""
        # Implementation for Apple Calendar integration
        pass

class ExchangeCalendarProvider:
    def __init__(self):
        self.api_url = "https://outlook.office365.com/api/v1.0"
        self.access_token = frappe.get_system_settings("exchange_calendar_access_token")
    
    def is_configured(self):
        return bool(self.access_token)
    
    def create_event(self, event_data):
        """Create event in Exchange Calendar"""
        # Implementation for Exchange Calendar integration
        pass
    
    def get_events(self, user, start_date, end_date):
        """Get events from Exchange Calendar"""
        # Implementation for Exchange Calendar integration
        pass
    
    def delete_event(self, event_id):
        """Delete event from Exchange Calendar"""
        # Implementation for Exchange Calendar integration
        pass

class CalendarSyncEngine:
    def __init__(self):
        self.sync_queue = []
        self.sync_processor = SyncProcessor()
    
    def queue_sync(self, event_id, action, data):
        """Queue calendar sync operation"""
        sync_item = {
            "event_id": event_id,
            "action": action,
            "data": data,
            "queued_at": now(),
            "status": "pending"
        }
        self.sync_queue.append(sync_item)
    
    def process_sync_queue(self):
        """Process calendar sync queue"""
        for sync_item in self.sync_queue:
            if sync_item["status"] == "pending":
                try:
                    self.sync_processor.process_sync(sync_item)
                    sync_item["status"] = "completed"
                except Exception as e:
                    sync_item["status"] = "failed"
                    sync_item["error"] = str(e)

class SyncProcessor:
    def process_sync(self, sync_item):
        """Process individual sync item"""
        # Implementation for sync processing
        pass

class CalendarConflictResolver:
    def __init__(self):
        self.conflict_detector = ConflictDetector()
        self.resolution_strategies = {
            "auto_resolve": AutoResolveStrategy(),
            "manual_resolve": ManualResolveStrategy(),
            "priority_based": PriorityBasedStrategy()
        }
    
    def check_conflicts(self, event_data):
        """Check for calendar conflicts"""
        return self.conflict_detector.detect_conflicts(event_data)
    
    def resolve_conflicts(self, conflicts, strategy="auto_resolve"):
        """Resolve calendar conflicts"""
        resolver = self.resolution_strategies.get(strategy)
        if resolver:
            return resolver.resolve(conflicts)
        return conflicts

class ConflictDetector:
    def detect_conflicts(self, event_data):
        """Detect calendar conflicts"""
        # Implementation for conflict detection
        pass

class AutoResolveStrategy:
    def resolve(self, conflicts):
        """Auto-resolve conflicts"""
        # Implementation for auto-resolution
        pass

class ManualResolveStrategy:
    def resolve(self, conflicts):
        """Manual conflict resolution"""
        # Implementation for manual resolution
        pass

class PriorityBasedStrategy:
    def resolve(self, conflicts):
        """Priority-based conflict resolution"""
        # Implementation for priority-based resolution
        pass
