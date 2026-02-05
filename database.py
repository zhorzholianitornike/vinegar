"""
Database Module for Social Media Marketing Agent
=================================================
SQLite database for storing post drafts, images, and user edits.
"""

import sqlite3
import os
from datetime import datetime
from typing import Optional, List, Dict, Any


class Database:
    """Handles all database operations for the marketing agent."""

    def __init__(self, db_path: str = "drafts.db"):
        """
        Initialize database connection.

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self.connection = None

        # Create database and tables if they don't exist
        self.initialize_database()

        print(f"✓ Database initialized: {db_path}")

    def initialize_database(self):
        """Create database tables if they don't exist."""
        self.connection = sqlite3.connect(self.db_path, check_same_thread=False)
        self.connection.row_factory = sqlite3.Row  # Return rows as dictionaries

        cursor = self.connection.cursor()

        # Create drafts table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS drafts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                honey_type TEXT NOT NULL,
                post_text TEXT NOT NULL,
                image_path TEXT,
                status TEXT DEFAULT 'draft',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                published_at TIMESTAMP,
                telegram_message_id INTEGER,
                notes TEXT
            )
        """)

        # Create edit history table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS edit_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                draft_id INTEGER NOT NULL,
                old_text TEXT,
                new_text TEXT,
                edited_by TEXT DEFAULT 'user',
                edited_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (draft_id) REFERENCES drafts(id)
            )
        """)

        self.connection.commit()

    def create_draft(
        self,
        honey_type: str,
        post_text: str,
        image_path: Optional[str] = None,
        telegram_message_id: Optional[int] = None
    ) -> int:
        """
        Create a new draft post.

        Args:
            honey_type: Type of honey
            post_text: Generated post text
            image_path: Path to generated image
            telegram_message_id: Telegram message ID (if sent to bot)

        Returns:
            Draft ID
        """
        cursor = self.connection.cursor()

        cursor.execute("""
            INSERT INTO drafts (honey_type, post_text, image_path, telegram_message_id)
            VALUES (?, ?, ?, ?)
        """, (honey_type, post_text, image_path, telegram_message_id))

        self.connection.commit()

        draft_id = cursor.lastrowid
        print(f"✓ Draft created with ID: {draft_id}")

        return draft_id

    def get_draft(self, draft_id: int) -> Optional[Dict[str, Any]]:
        """
        Get a specific draft by ID.

        Args:
            draft_id: Draft ID

        Returns:
            Draft data as dictionary, or None if not found
        """
        cursor = self.connection.cursor()

        cursor.execute("SELECT * FROM drafts WHERE id = ?", (draft_id,))
        row = cursor.fetchone()

        if row:
            return dict(row)
        return None

    def get_all_drafts(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get all drafts, optionally filtered by status.

        Args:
            status: Filter by status ('draft', 'approved', 'published')

        Returns:
            List of drafts
        """
        cursor = self.connection.cursor()

        if status:
            cursor.execute(
                "SELECT * FROM drafts WHERE status = ? ORDER BY created_at DESC",
                (status,)
            )
        else:
            cursor.execute("SELECT * FROM drafts ORDER BY created_at DESC")

        rows = cursor.fetchall()
        return [dict(row) for row in rows]

    def update_draft_text(self, draft_id: int, new_text: str, edited_by: str = "user") -> bool:
        """
        Update draft text and record in edit history.

        Args:
            draft_id: Draft ID
            new_text: New text content
            edited_by: Who edited it ('user', 'gemini', 'telegram')

        Returns:
            True if successful
        """
        cursor = self.connection.cursor()

        # Get old text first
        draft = self.get_draft(draft_id)
        if not draft:
            print(f"✗ Draft {draft_id} not found")
            return False

        old_text = draft["post_text"]

        # Update draft
        cursor.execute("""
            UPDATE drafts
            SET post_text = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (new_text, draft_id))

        # Record in edit history
        cursor.execute("""
            INSERT INTO edit_history (draft_id, old_text, new_text, edited_by)
            VALUES (?, ?, ?, ?)
        """, (draft_id, old_text, new_text, edited_by))

        self.connection.commit()

        print(f"✓ Draft {draft_id} updated")
        return True

    def update_draft_status(self, draft_id: int, status: str) -> bool:
        """
        Update draft status.

        Args:
            draft_id: Draft ID
            status: New status ('draft', 'approved', 'published', 'rejected')

        Returns:
            True if successful
        """
        cursor = self.connection.cursor()

        cursor.execute("""
            UPDATE drafts
            SET status = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (status, draft_id))

        self.connection.commit()

        print(f"✓ Draft {draft_id} status updated to: {status}")
        return True

    def update_draft_image(self, draft_id: int, new_image_path: str) -> bool:
        """
        Update draft image path.

        Args:
            draft_id: Draft ID
            new_image_path: Path to new image

        Returns:
            True if successful
        """
        cursor = self.connection.cursor()

        cursor.execute("""
            UPDATE drafts
            SET image_path = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (new_image_path, draft_id))

        self.connection.commit()

        print(f"✓ Draft {draft_id} image updated")
        return True

    def get_edit_history(self, draft_id: int) -> List[Dict[str, Any]]:
        """
        Get edit history for a draft.

        Args:
            draft_id: Draft ID

        Returns:
            List of edits
        """
        cursor = self.connection.cursor()

        cursor.execute("""
            SELECT * FROM edit_history
            WHERE draft_id = ?
            ORDER BY edited_at DESC
        """, (draft_id,))

        rows = cursor.fetchall()
        return [dict(row) for row in rows]

    def delete_draft(self, draft_id: int) -> bool:
        """
        Delete a draft and its edit history.

        Args:
            draft_id: Draft ID

        Returns:
            True if successful
        """
        cursor = self.connection.cursor()

        # Delete edit history first (foreign key)
        cursor.execute("DELETE FROM edit_history WHERE draft_id = ?", (draft_id,))

        # Delete draft
        cursor.execute("DELETE FROM drafts WHERE id = ?", (draft_id,))

        self.connection.commit()

        print(f"✓ Draft {draft_id} deleted")
        return True

    def get_latest_draft(self) -> Optional[Dict[str, Any]]:
        """
        Get the most recently created draft.

        Returns:
            Latest draft or None
        """
        cursor = self.connection.cursor()

        cursor.execute("""
            SELECT * FROM drafts
            ORDER BY created_at DESC
            LIMIT 1
        """)

        row = cursor.fetchone()

        if row:
            return dict(row)
        return None

    def close(self):
        """Close database connection."""
        if self.connection:
            self.connection.close()
            print("✓ Database connection closed")


# Example usage and testing
if __name__ == "__main__":
    print("=" * 50)
    print("Database Module Test")
    print("=" * 50 + "\n")

    # Initialize database
    db = Database("test_drafts.db")

    # Create a test draft
    draft_id = db.create_draft(
        honey_type="ბროწეულის ძმარი",
        post_text="ბუნებრივი ბროწეულის ძმარი თქვენი ჯანმრთელობისთვის! 🍯",
        image_path="honey_image.png"
    )

    # Get the draft
    draft = db.get_draft(draft_id)
    print(f"\nRetrieved draft: {draft['honey_type']}")

    # Update the text
    db.update_draft_text(
        draft_id,
        "განახლებული ტექსტი: ბუნებრივი ბროწეულის ძმარი! 🍯✨",
        edited_by="user"
    )

    # Get edit history
    history = db.get_edit_history(draft_id)
    print(f"\nEdit history entries: {len(history)}")

    # Get all drafts
    all_drafts = db.get_all_drafts()
    print(f"\nTotal drafts: {len(all_drafts)}")

    # Close connection
    db.close()

    print("\n✓ Test completed successfully!")
