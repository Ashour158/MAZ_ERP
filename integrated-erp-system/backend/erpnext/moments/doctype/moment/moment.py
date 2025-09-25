# Enhanced Moment DocType - Facebook-like Social Features

import frappe
from frappe.model.document import Document
from frappe import _
from frappe.utils import now, get_datetime, add_days, get_time
from frappe.model.naming import make_autoname
import json
from datetime import datetime, timedelta
import base64
import hashlib
import re

class Moment(Document):
    def autoname(self):
        """Generate unique moment ID"""
        if not self.moment_id:
            self.moment_id = make_autoname("MOM-.YYYY.-.MM.-.#####")
        self.name = self.moment_id

    def validate(self):
        """Validate moment data"""
        self.validate_moment_data()
        self.set_defaults()
        self.validate_content()
        self.validate_mentions()
        self.validate_location()

    def before_save(self):
        """Process before saving"""
        self.process_content()
        self.extract_hashtags()
        self.extract_mentions()
        self.set_privacy_settings()
        self.generate_preview()

    def after_insert(self):
        """Process after inserting new moment"""
        self.send_notifications()
        self.update_user_activity()
        self.create_activity_log()
        self.process_ai_analysis()

    def on_update(self):
        """Process on moment update"""
        self.update_engagement_metrics()
        self.sync_moment_data()

    def validate_moment_data(self):
        """Validate moment information"""
        if not self.content and not self.attachments:
            frappe.throw(_("Moment must have content or attachments"))
        
        if not self.author:
            frappe.throw(_("Author is required"))
        
        if not self.moment_type:
            frappe.throw(_("Moment type is required"))

    def validate_content(self):
        """Validate moment content"""
        if self.content:
            # Check content length
            if len(self.content) > 2000:
                frappe.throw(_("Content cannot exceed 2000 characters"))
            
            # Check for inappropriate content
            if self.contains_inappropriate_content():
                frappe.throw(_("Content contains inappropriate material"))

    def validate_mentions(self):
        """Validate user mentions"""
        if self.mentions:
            for mention in self.mentions:
                if not frappe.db.exists("User", mention.user):
                    frappe.throw(_("Mentioned user {0} does not exist").format(mention.user))

    def validate_location(self):
        """Validate location data"""
        if self.location:
            if not self.location.get("latitude") or not self.location.get("longitude"):
                frappe.throw(_("Invalid location data"))

    def set_defaults(self):
        """Set default values for new moment"""
        if not self.moment_type:
            self.moment_type = "Text"
        
        if not self.privacy:
            self.privacy = "Public"
        
        if not self.status:
            self.status = "Published"
        
        if not self.posted_date:
            self.posted_date = now()

    def process_content(self):
        """Process moment content"""
        if self.content:
            # Process emojis
            self.content = self.process_emojis(self.content)
            
            # Process links
            self.content = self.process_links(self.content)
            
            # Process hashtags
            self.content = self.process_hashtags(self.content)
            
            # Process mentions
            self.content = self.process_mentions(self.content)

    def extract_hashtags(self):
        """Extract hashtags from content"""
        if self.content:
            hashtags = re.findall(r'#(\w+)', self.content)
            self.hashtags = json.dumps(hashtags)
            
            # Create hashtag records
            for hashtag in hashtags:
                self.create_hashtag_record(hashtag)

    def extract_mentions(self):
        """Extract mentions from content"""
        if self.content:
            mentions = re.findall(r'@(\w+)', self.content)
            self.mentions = json.dumps(mentions)
            
            # Create mention records
            for mention in mentions:
                self.create_mention_record(mention)

    def set_privacy_settings(self):
        """Set privacy settings for moment"""
        if self.privacy == "Private":
            self.visibility = "Author Only"
        elif self.privacy == "Friends":
            self.visibility = "Friends Only"
        elif self.privacy == "Department":
            self.visibility = "Department Only"
        else:
            self.visibility = "Public"

    def generate_preview(self):
        """Generate moment preview"""
        preview_data = {
            "content_preview": self.content[:100] + "..." if len(self.content) > 100 else self.content,
            "attachment_count": len(self.attachments) if self.attachments else 0,
            "hashtag_count": len(json.loads(self.hashtags)) if self.hashtags else 0,
            "mention_count": len(json.loads(self.mentions)) if self.mentions else 0,
            "location": self.location.get("name") if self.location else None
        }
        
        self.preview = json.dumps(preview_data)

    def send_notifications(self):
        """Send notifications for new moment"""
        # Notify mentioned users
        if self.mentions:
            for mention in json.loads(self.mentions):
                self.send_mention_notification(mention)
        
        # Notify followers
        self.send_follower_notifications()
        
        # Notify department members if department moment
        if self.privacy == "Department":
            self.send_department_notifications()

    def update_user_activity(self):
        """Update user activity metrics"""
        # Update author's activity
        author_activity = frappe.get_doc("User Activity", {"user": self.author})
        if not author_activity:
            author_activity = frappe.get_doc({
                "doctype": "User Activity",
                "user": self.author,
                "moments_count": 0,
                "total_likes": 0,
                "total_comments": 0,
                "total_shares": 0
            })
            author_activity.insert(ignore_permissions=True)
        
        author_activity.moments_count += 1
        author_activity.save()

    def create_activity_log(self):
        """Create activity log for moment"""
        activity_log = frappe.get_doc({
            "doctype": "Moment Activity",
            "moment": self.name,
            "activity_type": "Created",
            "user": self.author,
            "activity_date": now(),
            "description": f"Created moment: {self.moment_id}"
        })
        activity_log.insert(ignore_permissions=True)

    def process_ai_analysis(self):
        """Process AI analysis for moment"""
        # Sentiment analysis
        sentiment = self.analyze_sentiment()
        
        # Content classification
        content_type = self.classify_content()
        
        # Safety analysis
        safety_score = self.analyze_safety()
        
        # Update moment with AI insights
        self.ai_analysis = json.dumps({
            "sentiment": sentiment,
            "content_type": content_type,
            "safety_score": safety_score,
            "analysis_date": now().isoformat()
        })
        
        self.save()

    def analyze_sentiment(self):
        """Analyze sentiment of moment content"""
        if not self.content:
            return "neutral"
        
        # Simple sentiment analysis
        positive_words = ["happy", "great", "awesome", "amazing", "love", "excellent", "wonderful"]
        negative_words = ["sad", "bad", "terrible", "awful", "hate", "disappointed", "angry"]
        
        content_lower = self.content.lower()
        positive_count = sum(1 for word in positive_words if word in content_lower)
        negative_count = sum(1 for word in negative_words if word in content_lower)
        
        if positive_count > negative_count:
            return "positive"
        elif negative_count > positive_count:
            return "negative"
        else:
            return "neutral"

    def classify_content(self):
        """Classify content type"""
        if not self.content:
            return "text"
        
        content_lower = self.content.lower()
        
        # Check for different content types
        if any(word in content_lower for word in ["work", "project", "meeting", "office"]):
            return "work_related"
        elif any(word in content_lower for word in ["celebration", "party", "birthday", "anniversary"]):
            return "celebration"
        elif any(word in content_lower for word in ["help", "support", "assistance"]):
            return "support"
        elif any(word in content_lower for word in ["idea", "suggestion", "feedback"]):
            return "idea"
        else:
            return "general"

    def analyze_safety(self):
        """Analyze content safety"""
        if not self.content:
            return 1.0
        
        # Check for inappropriate content
        inappropriate_words = ["spam", "scam", "fraud", "illegal"]
        content_lower = self.content.lower()
        
        inappropriate_count = sum(1 for word in inappropriate_words if word in content_lower)
        
        if inappropriate_count > 0:
            return 0.0
        else:
            return 1.0

    def update_engagement_metrics(self):
        """Update engagement metrics"""
        # Calculate engagement score
        engagement_score = self.calculate_engagement_score()
        
        # Update moment with engagement data
        self.engagement_score = engagement_score
        self.save()

    def calculate_engagement_score(self):
        """Calculate engagement score"""
        likes = self.likes_count or 0
        comments = self.comments_count or 0
        shares = self.shares_count or 0
        views = self.views_count or 0
        
        # Calculate engagement score
        engagement_score = (likes * 1) + (comments * 2) + (shares * 3) + (views * 0.1)
        
        return engagement_score

    def sync_moment_data(self):
        """Sync moment data across systems"""
        # Sync with external social platforms if configured
        if self.external_platform_id:
            self.sync_with_external_platform()

    def contains_inappropriate_content(self):
        """Check for inappropriate content"""
        if not self.content:
            return False
        
        # List of inappropriate words (simplified)
        inappropriate_words = ["spam", "scam", "fraud", "illegal", "inappropriate"]
        content_lower = self.content.lower()
        
        return any(word in content_lower for word in inappropriate_words)

    def process_emojis(self, content):
        """Process emojis in content"""
        # Convert emoji codes to actual emojis
        emoji_map = {
            ":smile:": "😊",
            ":heart:": "❤️",
            ":thumbs_up:": "👍",
            ":thumbs_down:": "👎",
            ":laugh:": "😂",
            ":angry:": "😠",
            ":sad:": "😢",
            ":love:": "😍"
        }
        
        for code, emoji in emoji_map.items():
            content = content.replace(code, emoji)
        
        return content

    def process_links(self, content):
        """Process links in content"""
        # Convert URLs to clickable links
        url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        content = re.sub(url_pattern, r'<a href="\g<0>" target="_blank">\g<0></a>', content)
        
        return content

    def process_hashtags(self, content):
        """Process hashtags in content"""
        # Convert hashtags to clickable links
        hashtag_pattern = r'#(\w+)'
        content = re.sub(hashtag_pattern, r'<a href="/hashtag/\1" class="hashtag">#\1</a>', content)
        
        return content

    def process_mentions(self, content):
        """Process mentions in content"""
        # Convert mentions to clickable links
        mention_pattern = r'@(\w+)'
        content = re.sub(mention_pattern, r'<a href="/user/\1" class="mention">@\1</a>', content)
        
        return content

    def create_hashtag_record(self, hashtag):
        """Create hashtag record"""
        if not frappe.db.exists("Hashtag", hashtag):
            frappe.get_doc({
                "doctype": "Hashtag",
                "hashtag": hashtag,
                "usage_count": 1,
                "first_used": now(),
                "last_used": now()
            }).insert(ignore_permissions=True)
        else:
            # Update hashtag usage
            hashtag_doc = frappe.get_doc("Hashtag", hashtag)
            hashtag_doc.usage_count += 1
            hashtag_doc.last_used = now()
            hashtag_doc.save()

    def create_mention_record(self, mention):
        """Create mention record"""
        frappe.get_doc({
            "doctype": "Moment Mention",
            "moment": self.name,
            "mentioned_user": mention,
            "mention_date": now()
        }).insert(ignore_permissions=True)

    def send_mention_notification(self, mentioned_user):
        """Send notification to mentioned user"""
        frappe.get_doc({
            "doctype": "Moment Notification",
            "user": mentioned_user,
            "moment": self.name,
            "notification_type": "Mention",
            "message": f"You were mentioned in a moment by {self.author}",
            "is_read": 0,
            "created_date": now()
        }).insert(ignore_permissions=True)

    def send_follower_notifications(self):
        """Send notifications to followers"""
        # Get author's followers
        followers = frappe.db.sql("""
            SELECT follower
            FROM `tabUser Follow` 
            WHERE following = %s
        """, self.author, as_dict=True)
        
        for follower in followers:
            frappe.get_doc({
                "doctype": "Moment Notification",
                "user": follower.follower,
                "moment": self.name,
                "notification_type": "New Moment",
                "message": f"{self.author} shared a new moment",
                "is_read": 0,
                "created_date": now()
            }).insert(ignore_permissions=True)

    def send_department_notifications(self):
        """Send notifications to department members"""
        # Get author's department
        author_department = frappe.db.get_value("Employee", {"user": self.author}, "department")
        
        if author_department:
            # Get department members
            department_members = frappe.db.sql("""
                SELECT user
                FROM `tabEmployee` 
                WHERE department = %s AND user != %s
            """, (author_department, self.author), as_dict=True)
            
            for member in department_members:
                frappe.get_doc({
                    "doctype": "Moment Notification",
                    "user": member.user,
                    "moment": self.name,
                    "notification_type": "Department Moment",
                    "message": f"{self.author} shared a moment in your department",
                    "is_read": 0,
                    "created_date": now()
                }).insert(ignore_permissions=True)

    def sync_with_external_platform(self):
        """Sync moment with external platform"""
        # Implementation for external platform sync
        pass

    @frappe.whitelist()
    def like_moment(self, user):
        """Like a moment"""
        # Check if already liked
        if frappe.db.exists("Moment Like", {"moment": self.name, "user": user}):
            frappe.throw(_("You have already liked this moment"))
        
        # Create like record
        like = frappe.get_doc({
            "doctype": "Moment Like",
            "moment": self.name,
            "user": user,
            "like_date": now()
        })
        like.insert(ignore_permissions=True)
        
        # Update like count
        self.likes_count = (self.likes_count or 0) + 1
        self.save()
        
        # Send notification to author
        if user != self.author:
            frappe.get_doc({
                "doctype": "Moment Notification",
                "user": self.author,
                "moment": self.name,
                "notification_type": "Like",
                "message": f"{user} liked your moment",
                "is_read": 0,
                "created_date": now()
            }).insert(ignore_permissions=True)
        
        return {"status": "success", "likes_count": self.likes_count}

    @frappe.whitelist()
    def unlike_moment(self, user):
        """Unlike a moment"""
        # Check if liked
        like = frappe.get_doc("Moment Like", {"moment": self.name, "user": user})
        if like:
            like.delete()
            
            # Update like count
            self.likes_count = max(0, (self.likes_count or 0) - 1)
            self.save()
        
        return {"status": "success", "likes_count": self.likes_count}

    @frappe.whitelist()
    def add_comment(self, user, comment_content):
        """Add comment to moment"""
        if not comment_content:
            frappe.throw(_("Comment content is required"))
        
        # Create comment
        comment = frappe.get_doc({
            "doctype": "Moment Comment",
            "moment": self.name,
            "user": user,
            "comment": comment_content,
            "comment_date": now()
        })
        comment.insert(ignore_permissions=True)
        
        # Update comment count
        self.comments_count = (self.comments_count or 0) + 1
        self.save()
        
        # Send notification to author
        if user != self.author:
            frappe.get_doc({
                "doctype": "Moment Notification",
                "user": self.author,
                "moment": self.name,
                "notification_type": "Comment",
                "message": f"{user} commented on your moment",
                "is_read": 0,
                "created_date": now()
            }).insert(ignore_permissions=True)
        
        return {"status": "success", "comments_count": self.comments_count}

    @frappe.whitelist()
    def share_moment(self, user):
        """Share a moment"""
        # Create share record
        share = frappe.get_doc({
            "doctype": "Moment Share",
            "moment": self.name,
            "user": user,
            "share_date": now()
        })
        share.insert(ignore_permissions=True)
        
        # Update share count
        self.shares_count = (self.shares_count or 0) + 1
        self.save()
        
        # Send notification to author
        if user != self.author:
            frappe.get_doc({
                "doctype": "Moment Notification",
                "user": self.author,
                "moment": self.name,
                "notification_type": "Share",
                "message": f"{user} shared your moment",
                "is_read": 0,
                "created_date": now()
            }).insert(ignore_permissions=True)
        
        return {"status": "success", "shares_count": self.shares_count}

    @frappe.whitelist()
    def get_moment_feed(self, user, limit=20, offset=0):
        """Get moment feed for user"""
        # Get moments based on user's connections and privacy settings
        moments = frappe.db.sql("""
            SELECT 
                m.name,
                m.moment_id,
                m.content,
                m.author,
                m.posted_date,
                m.moment_type,
                m.privacy,
                m.likes_count,
                m.comments_count,
                m.shares_count,
                m.location,
                m.attachments,
                m.hashtags,
                m.mentions,
                m.preview
            FROM `tabMoment` m
            WHERE (
                m.privacy = 'Public' OR
                (m.privacy = 'Friends' AND m.author IN (
                    SELECT following FROM `tabUser Follow` WHERE follower = %s
                )) OR
                (m.privacy = 'Department' AND m.author IN (
                    SELECT e.user FROM `tabEmployee` e 
                    WHERE e.department = (
                        SELECT department FROM `tabEmployee` WHERE user = %s
                    )
                ))
            )
            ORDER BY m.posted_date DESC
            LIMIT %s OFFSET %s
        """, (user, user, limit, offset), as_dict=True)
        
        return moments

    @frappe.whitelist()
    def get_moment_details(self, moment_id):
        """Get detailed moment information"""
        moment = frappe.get_doc("Moment", {"moment_id": moment_id})
        
        # Get comments
        comments = frappe.db.sql("""
            SELECT 
                c.user,
                c.comment,
                c.comment_date
            FROM `tabMoment Comment` c
            WHERE c.moment = %s
            ORDER BY c.comment_date ASC
        """, moment.name, as_dict=True)
        
        # Get likes
        likes = frappe.db.sql("""
            SELECT 
                l.user,
                l.like_date
            FROM `tabMoment Like` l
            WHERE l.moment = %s
            ORDER BY l.like_date DESC
        """, moment.name, as_dict=True)
        
        return {
            "moment": moment.as_dict(),
            "comments": comments,
            "likes": likes
        }
