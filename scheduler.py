"""
Post Scheduler for Social Media Marketing Agent
================================================
Handles scheduling posts for future publication and immediate publishing.
"""

import os
import time
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from database import Database
import threading


class PostScheduler:
    """Manages post scheduling and publishing."""

    def __init__(self, database: Database):
        """
        Initialize the Post Scheduler.

        Args:
            database: Database instance
        """
        self.db = database
        self.scheduled_posts = {}  # {draft_id: scheduled_datetime}
        self.scheduler_thread = None
        self.running = False

        print("✓ Post Scheduler initialized")

    def schedule_post(self, draft_id: int, publish_datetime: datetime) -> bool:
        """
        Schedule a post for future publication.

        Args:
            draft_id: Draft ID to schedule
            publish_datetime: When to publish

        Returns:
            True if scheduled successfully
        """
        try:
            draft = self.db.get_draft(draft_id)

            if not draft:
                print(f"✗ Draft {draft_id} not found")
                return False

            if draft['status'] != 'approved':
                print(f"✗ Draft {draft_id} must be approved before scheduling")
                return False

            # Store in memory (in production, this should be in database)
            self.scheduled_posts[draft_id] = publish_datetime

            # Update database with schedule info
            self.db.connection.execute(
                "UPDATE drafts SET notes = ? WHERE id = ?",
                (f"Scheduled for: {publish_datetime.strftime('%Y-%m-%d %H:%M')}", draft_id)
            )
            self.db.connection.commit()

            print(f"✓ Draft {draft_id} scheduled for {publish_datetime.strftime('%Y-%m-%d %H:%M')}")
            return True

        except Exception as e:
            print(f"✗ Error scheduling post: {e}")
            return False

    def publish_now(self, draft_id: int) -> Dict[str, Any]:
        """
        Publish a post immediately.

        Args:
            draft_id: Draft ID to publish

        Returns:
            Dict with success status and details
        """
        try:
            draft = self.db.get_draft(draft_id)

            if not draft:
                return {
                    "success": False,
                    "error": "Draft not found"
                }

            if draft['status'] != 'approved':
                return {
                    "success": False,
                    "error": "Draft must be approved before publishing"
                }

            # Update status to published
            self.db.connection.execute(
                "UPDATE drafts SET status = ?, published_at = CURRENT_TIMESTAMP WHERE id = ?",
                ('published', draft_id)
            )
            self.db.connection.commit()

            print(f"✅ Draft {draft_id} published successfully!")

            return {
                "success": True,
                "draft_id": draft_id,
                "post_text": draft['post_text'],
                "image_path": draft['image_path'],
                "published_at": datetime.now().isoformat()
            }

        except Exception as e:
            print(f"✗ Error publishing post: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def cancel_schedule(self, draft_id: int) -> bool:
        """
        Cancel a scheduled post.

        Args:
            draft_id: Draft ID

        Returns:
            True if cancelled successfully
        """
        if draft_id in self.scheduled_posts:
            del self.scheduled_posts[draft_id]

            # Update database
            self.db.connection.execute(
                "UPDATE drafts SET notes = NULL WHERE id = ?",
                (draft_id,)
            )
            self.db.connection.commit()

            print(f"✓ Schedule cancelled for draft {draft_id}")
            return True
        else:
            print(f"✗ No schedule found for draft {draft_id}")
            return False

    def get_scheduled_posts(self) -> Dict[int, datetime]:
        """
        Get all scheduled posts.

        Returns:
            Dict of {draft_id: scheduled_datetime}
        """
        return self.scheduled_posts.copy()

    def start_scheduler(self):
        """Start the background scheduler thread."""
        if self.running:
            print("⚠️  Scheduler is already running")
            return

        self.running = True
        self.scheduler_thread = threading.Thread(target=self._scheduler_loop, daemon=True)
        self.scheduler_thread.start()

        print("✓ Scheduler thread started")

    def stop_scheduler(self):
        """Stop the background scheduler thread."""
        self.running = False
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=5)

        print("✓ Scheduler thread stopped")

    def _scheduler_loop(self):
        """Background loop that checks for posts to publish."""
        print("🔄 Scheduler loop started")

        while self.running:
            try:
                now = datetime.now()

                # Check for posts that need to be published
                posts_to_publish = []

                for draft_id, scheduled_time in list(self.scheduled_posts.items()):
                    if now >= scheduled_time:
                        posts_to_publish.append(draft_id)

                # Publish due posts
                for draft_id in posts_to_publish:
                    print(f"⏰ Publishing scheduled post {draft_id}...")
                    result = self.publish_now(draft_id)

                    if result['success']:
                        # Remove from schedule
                        del self.scheduled_posts[draft_id]
                        print(f"✅ Scheduled post {draft_id} published!")
                    else:
                        print(f"✗ Failed to publish scheduled post {draft_id}: {result.get('error')}")

                # Sleep for 60 seconds before next check
                time.sleep(60)

            except Exception as e:
                print(f"✗ Error in scheduler loop: {e}")
                time.sleep(60)

        print("🔄 Scheduler loop stopped")


# Example usage
if __name__ == "__main__":
    from database import Database

    db = Database("test_drafts.db")
    scheduler = PostScheduler(db)

    # Create a test draft
    draft_id = db.create_draft(
        honey_type="ბროწეულის ძმარი",
        post_text="Test post for scheduling",
        image_path="test.png"
    )

    # Approve it
    db.update_draft_status(draft_id, "approved")

    # Schedule for 5 minutes from now
    future_time = datetime.now() + timedelta(minutes=5)
    scheduler.schedule_post(draft_id, future_time)

    print(f"\nScheduled posts: {scheduler.get_scheduled_posts()}")

    # Or publish immediately
    # result = scheduler.publish_now(draft_id)
    # print(f"\nPublish result: {result}")
