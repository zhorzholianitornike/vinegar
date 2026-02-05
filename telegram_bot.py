"""
Telegram Bot for Social Media Marketing Agent
==============================================
Handles user interactions via Telegram with inline keyboard buttons.
Sends generated posts (photo + text) and allows approval, regeneration, or editing.
"""

import os
import telebot
from telebot import types
from typing import Optional, Callable
from database import Database
from text_generator import TextGenerator
from image_generator import ImageGenerator


class MarketingBot:
    """Telegram bot for social media marketing workflow."""

    def __init__(
        self,
        bot_token: str,
        database: Database,
        text_generator: TextGenerator,
        image_generator: ImageGenerator,
        admin_chat_id: Optional[int] = None
    ):
        """
        Initialize the Telegram bot.

        Args:
            bot_token: Telegram bot token from @BotFather
            database: Database instance
            text_generator: Text generator instance
            image_generator: Image generator instance
            admin_chat_id: Chat ID of the admin user (optional)
        """
        self.bot = telebot.TeleBot(bot_token)
        self.db = database
        self.text_gen = text_generator
        self.image_gen = image_generator
        self.admin_chat_id = admin_chat_id

        # Store current draft ID for callback context
        self.current_draft_id = None

        # Register handlers
        self._register_handlers()

        print("✓ Telegram Bot initialized")

    def _register_handlers(self):
        """Register all bot command and callback handlers."""

        @self.bot.message_handler(commands=['start', 'help'])
        def send_welcome(message):
            """Welcome message."""
            welcome_text = """
👋 გამარჯობა! მე ვარ სოციალური მედიის მარკეტინგის აგენტი.

📋 ხელმისაწვდომი ბრძანებები:
/create - შექმენი ახალი პოსტი
/status - დრაფტების სტატუსი
/help - დახმარება

🍯 მაგალითი: /create ბროწეულის ძმარი
"""
            self.bot.reply_to(message, welcome_text)

        @self.bot.message_handler(commands=['create'])
        def create_post(message):
            """Create a new marketing post."""
            # Parse honey type from command
            parts = message.text.split(maxsplit=1)

            if len(parts) < 2:
                self.bot.reply_to(
                    message,
                    "❌ გთხოვ, მიუთითე ძმრის ტიპი.\n\nმაგალითი: /create ბროწეულის ძმარი"
                )
                return

            honey_type = parts[1]

            # Send "processing" message
            processing_msg = self.bot.reply_to(
                message,
                f"⏳ ვქმნი პოსტს {honey_type}-ის შესახებ...\n\n"
                "🎨 ვაგენერირებ სურათს...\n"
                "📝 ვწერ ტექსტს..."
            )

            try:
                # Generate image
                image_path = self.image_gen.generate_honey_marketing_image(honey_type)

                if not image_path:
                    self.bot.edit_message_text(
                        "❌ სურათის გენერაცია ვერ მოხერხდა. გთხოვ, სცადე თავიდან.",
                        message.chat.id,
                        processing_msg.message_id
                    )
                    return

                # Generate text
                post_text = self.text_gen.generate_facebook_post(
                    honey_type=honey_type,
                    tone="friendly",
                    include_emoji=True
                )

                if not post_text:
                    self.bot.edit_message_text(
                        "❌ ტექსტის გენერაცია ვერ მოხერხდა. გთხოვ, სცადე თავიდან.",
                        message.chat.id,
                        processing_msg.message_id
                    )
                    return

                # Delete processing message
                self.bot.delete_message(message.chat.id, processing_msg.message_id)

                # Send the complete post
                self._send_post_for_review(message.chat.id, honey_type, post_text, image_path)

            except Exception as e:
                self.bot.edit_message_text(
                    f"❌ შეცდომა: {str(e)}",
                    message.chat.id,
                    processing_msg.message_id
                )

        @self.bot.message_handler(commands=['status'])
        def show_status(message):
            """Show status of all drafts."""
            drafts = self.db.get_all_drafts()

            if not drafts:
                self.bot.reply_to(message, "📭 დრაფტები არ არის.")
                return

            status_text = "📊 დრაფტების სტატუსი:\n\n"

            for draft in drafts[:10]:  # Show last 10
                status_emoji = {
                    'draft': '📝',
                    'approved': '✅',
                    'published': '🎉',
                    'rejected': '❌'
                }.get(draft['status'], '❓')

                status_text += (
                    f"{status_emoji} #{draft['id']} - {draft['honey_type']}\n"
                    f"   სტატუსი: {draft['status']}\n"
                    f"   შექმნილია: {draft['created_at'][:16]}\n\n"
                )

            self.bot.reply_to(message, status_text)

        @self.bot.callback_query_handler(func=lambda call: True)
        def handle_callback(call):
            """Handle inline button callbacks."""
            action = call.data

            if action.startswith("approve_"):
                draft_id = int(action.split("_")[1])
                self._approve_draft(call.message, draft_id)

            elif action.startswith("regenerate_text_"):
                draft_id = int(action.split("_")[2])
                self._regenerate_text(call.message, draft_id)

            elif action.startswith("regenerate_image_"):
                draft_id = int(action.split("_")[2])
                self._regenerate_image(call.message, draft_id)

            elif action.startswith("edit_"):
                draft_id = int(action.split("_")[1])
                self._open_dashboard(call.message, draft_id)

            elif action.startswith("reject_"):
                draft_id = int(action.split("_")[1])
                self._reject_draft(call.message, draft_id)

            # Answer callback to remove loading state
            self.bot.answer_callback_query(call.id)

    def _send_post_for_review(
        self,
        chat_id: int,
        honey_type: str,
        post_text: str,
        image_path: str
    ):
        """Send generated post with inline buttons for review."""

        # Save to database
        draft_id = self.db.create_draft(
            honey_type=honey_type,
            post_text=post_text,
            image_path=image_path
        )

        self.current_draft_id = draft_id

        # Create inline keyboard
        markup = types.InlineKeyboardMarkup(row_width=2)

        markup.add(
            types.InlineKeyboardButton("✅ დადასტურება", callback_data=f"approve_{draft_id}"),
            types.InlineKeyboardButton("❌ უარყოფა", callback_data=f"reject_{draft_id}")
        )

        markup.add(
            types.InlineKeyboardButton("🔄 ტექსტის შეცვლა", callback_data=f"regenerate_text_{draft_id}"),
            types.InlineKeyboardButton("🎨 ფოტოს შეცვლა", callback_data=f"regenerate_image_{draft_id}")
        )

        markup.add(
            types.InlineKeyboardButton("✏️ დაშბორდზე რედაქტირება", callback_data=f"edit_{draft_id}")
        )

        # Send photo with caption and buttons
        with open(image_path, 'rb') as photo:
            caption = f"🍯 {honey_type}\n\n{post_text}\n\n📋 Draft ID: #{draft_id}"

            sent_message = self.bot.send_photo(
                chat_id,
                photo,
                caption=caption,
                reply_markup=markup
            )

            # Update draft with telegram message ID
            self.db.connection.execute(
                "UPDATE drafts SET telegram_message_id = ? WHERE id = ?",
                (sent_message.message_id, draft_id)
            )
            self.db.connection.commit()

    def _approve_draft(self, message, draft_id: int):
        """Approve a draft and mark as ready for publishing."""
        self.db.update_draft_status(draft_id, "approved")

        self.bot.edit_message_caption(
            caption=message.caption + "\n\n✅ დამტკიცებულია!",
            chat_id=message.chat.id,
            message_id=message.message_id,
            reply_markup=None  # Remove buttons
        )

        self.bot.send_message(
            message.chat.id,
            f"✅ დრაფტი #{draft_id} დამტკიცებულია და მზადაა გამოსაქვეყნებლად!"
        )

    def _reject_draft(self, message, draft_id: int):
        """Reject a draft."""
        self.db.update_draft_status(draft_id, "rejected")

        self.bot.edit_message_caption(
            caption=message.caption + "\n\n❌ უარყოფილია",
            chat_id=message.chat.id,
            message_id=message.message_id,
            reply_markup=None
        )

    def _regenerate_text(self, message, draft_id: int):
        """Regenerate only the text for a draft."""
        draft = self.db.get_draft(draft_id)

        if not draft:
            self.bot.send_message(message.chat.id, "❌ დრაფტი არ მოიძებნა.")
            return

        # Generate new text
        new_text = self.text_gen.generate_facebook_post(
            honey_type=draft['honey_type'],
            tone="friendly",
            include_emoji=True
        )

        if new_text:
            self.db.update_draft_text(draft_id, new_text, edited_by="gemini")

            # Update message
            new_caption = f"🍯 {draft['honey_type']}\n\n{new_text}\n\n📋 Draft ID: #{draft_id}\n🔄 ტექსტი განახლებულია!"

            # Recreate buttons
            markup = self._create_review_markup(draft_id)

            self.bot.edit_message_caption(
                caption=new_caption,
                chat_id=message.chat.id,
                message_id=message.message_id,
                reply_markup=markup
            )
        else:
            self.bot.send_message(message.chat.id, "❌ ტექსტის გენერაცია ვერ მოხერხდა.")

    def _regenerate_image(self, message, draft_id: int):
        """Regenerate only the image for a draft."""
        draft = self.db.get_draft(draft_id)

        if not draft:
            self.bot.send_message(message.chat.id, "❌ დრაფტი არ მოიძებნა.")
            return

        # Generate new image
        new_image_path = self.image_gen.generate_honey_marketing_image(draft['honey_type'])

        if new_image_path:
            self.db.update_draft_image(draft_id, new_image_path)

            # Send new photo (can't edit photo in Telegram, must send new)
            self._send_post_for_review(
                message.chat.id,
                draft['honey_type'],
                draft['post_text'],
                new_image_path
            )

            # Delete old message
            self.bot.delete_message(message.chat.id, message.message_id)
        else:
            self.bot.send_message(message.chat.id, "❌ სურათის გენერაცია ვერ მოხერხდა.")

    def _open_dashboard(self, message, draft_id: int):
        """Provide link to dashboard for editing."""
        dashboard_url = os.getenv("DASHBOARD_URL", "http://localhost:8501")

        self.bot.send_message(
            message.chat.id,
            f"✏️ დაშბორდზე რედაქტირებისთვის:\n{dashboard_url}/?draft_id={draft_id}",
            reply_markup=types.InlineKeyboardMarkup().add(
                types.InlineKeyboardButton("🌐 დაშბორდზე გადასვლა", url=f"{dashboard_url}/?draft_id={draft_id}")
            )
        )

    def _create_review_markup(self, draft_id: int) -> types.InlineKeyboardMarkup:
        """Create inline keyboard for review."""
        markup = types.InlineKeyboardMarkup(row_width=2)

        markup.add(
            types.InlineKeyboardButton("✅ დადასტურება", callback_data=f"approve_{draft_id}"),
            types.InlineKeyboardButton("❌ უარყოფა", callback_data=f"reject_{draft_id}")
        )

        markup.add(
            types.InlineKeyboardButton("🔄 ტექსტის შეცვლა", callback_data=f"regenerate_text_{draft_id}"),
            types.InlineKeyboardButton("🎨 ფოტოს შეცვლა", callback_data=f"regenerate_image_{draft_id}")
        )

        markup.add(
            types.InlineKeyboardButton("✏️ დაშბორდზე რედაქტირება", callback_data=f"edit_{draft_id}")
        )

        return markup

    def start_polling(self):
        """Start the bot in polling mode."""
        print("🤖 Telegram Bot started polling...")
        self.bot.infinity_polling()

    def stop(self):
        """Stop the bot."""
        self.bot.stop_polling()
        print("🤖 Telegram Bot stopped")


# Example usage
if __name__ == "__main__":
    print("⚠️  This module should be run from main.py")
    print("Use: python main.py")
