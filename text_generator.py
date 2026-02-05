"""
Text Generator using Google Gemini API
=======================================
This module handles text generation using Google's Gemini models.
Generates engaging Facebook posts in Georgian language for organic honey marketing.
"""

import os
import google.generativeai as genai
from typing import Optional


class TextGenerator:
    """Generates marketing text using Google Gemini API."""

    def __init__(self, api_key: str, model_name: str = "gemini-1.5-flash"):
        """
        Initialize the Text Generator.

        Args:
            api_key: Google Gemini API key
            model_name: Model to use (default: gemini-1.5-flash)
                       Options: 'gemini-1.5-flash', 'gemini-1.5-pro'
        """
        self.api_key = api_key
        self.model_name = model_name

        # Configure Gemini
        genai.configure(api_key=api_key)

        # Initialize the model
        self.model = genai.GenerativeModel(model_name)

        print(f"✓ Text Generator initialized (Model: {model_name})")

    def generate_facebook_post(
        self,
        honey_type: str,
        tone: str = "friendly",
        include_emoji: bool = True,
        max_length: int = 300
    ) -> Optional[str]:
        """
        Generate a Facebook post in Georgian about organic honey.

        Args:
            honey_type: Type of honey in Georgian (e.g., "ბროწეულის ძმარი")
            tone: Tone of the post ('friendly', 'professional', 'enthusiastic')
            include_emoji: Whether to include emojis
            max_length: Maximum character length of the post

        Returns:
            Generated text in Georgian, or None if generation failed
        """
        try:
            # Create a detailed prompt in Georgian for better results
            prompt = f"""
შექმენი მიმზიდველი Facebook პოსტი ორგანული {honey_type}-ის შესახებ.

მოთხოვნები:
- **ენა: მხოლოდ ქართული**
- ტონი: {tone}
- სიგრძე: მაქსიმუმ {max_length} სიმბოლო
- მოიცავს:
  • ძმრის სარგებელს ჯანმრთელობისთვის
  • მის ბუნებრივ წარმოშობას
  • იმის მიზეზს, თუ რატომ არის ეს ძმარი განსაკუთრებული
  • მოწოდებას მოქმედებისკენ (Call-to-Action)
{"- გამოიყენე შესაბამისი ემოჯები" if include_emoji else "- ემოჯების გარეშე"}

არ გამოიყენო ჰეშთეგები. არ დაწერო "სათაური:" ან "პოსტი:" - დაიწყე პირდაპირ ტექსტით.
დაწერე ისე, რომ ადამიანებს სურდეთ პროდუქტის შეძენა.
"""

            print(f"📝 Generating Georgian text for: {honey_type}...")

            # Generate content
            response = self.model.generate_content(prompt)

            if response.text:
                generated_text = response.text.strip()
                print(f"✓ Generated {len(generated_text)} characters")
                return generated_text
            else:
                print("✗ No text was generated")
                return None

        except Exception as e:
            print(f"✗ Error generating text: {e}")
            return None

    def generate_honey_info(self, honey_type: str) -> Optional[str]:
        """
        Generate educational information about a specific type of honey in Georgian.

        Args:
            honey_type: Type of honey in Georgian

        Returns:
            Educational text in Georgian
        """
        try:
            prompt = f"""
მომეცი მოკლე, ინფორმაციული აღწერა {honey_type}-ის შესახებ ქართულ ენაზე.

მოიცავს:
1. რა მცენარიდან მოდის ეს ძმარი
2. მისი უნიკალური თვისებები
3. რა სარგებელი მოაქვს ჯანმრთელობისთვის
4. გემო და არომატი

პასუხი უნდა იყოს 3-4 წინადადება, მარტივი და გასაგები ენით.
"""

            response = self.model.generate_content(prompt)

            if response.text:
                return response.text.strip()
            else:
                return None

        except Exception as e:
            print(f"✗ Error generating honey info: {e}")
            return None

    def improve_text(self, original_text: str, instruction: str) -> Optional[str]:
        """
        Improve or modify existing text based on user instructions.

        Args:
            original_text: The text to improve
            instruction: What to change (e.g., "გახადე უფრო მოკლე", "დაამატე ემოცია")

        Returns:
            Improved text in Georgian
        """
        try:
            prompt = f"""
შეცვალე შემდეგი ტექსტი ამ ინსტრუქციის მიხედვით: "{instruction}"

ორიგინალი ტექსტი:
{original_text}

გაითვალისწინე:
- შეინარჩუნე ქართული ენა
- შეინარჩუნე ძირითადი მესიჯი
- გააუმჯობესე მოთხოვნილი ასპექტი
"""

            response = self.model.generate_content(prompt)

            if response.text:
                return response.text.strip()
            else:
                return None

        except Exception as e:
            print(f"✗ Error improving text: {e}")
            return None


# Example usage and testing
if __name__ == "__main__":
    # This is for testing only - normally called from main.py

    # Get API key from environment
    api_key = os.getenv("GOOGLE_GEMINI_API_KEY")

    if not api_key:
        print("⚠️  Please set GOOGLE_GEMINI_API_KEY environment variable")
        print("Example: export GOOGLE_GEMINI_API_KEY='your-api-key'")
    else:
        # Initialize generator
        generator = TextGenerator(api_key=api_key)

        # Generate a test post
        print("\n" + "=" * 50)
        print("Testing Facebook Post Generation")
        print("=" * 50 + "\n")

        post = generator.generate_facebook_post(
            honey_type="ბროწეულის ძმარი",
            tone="friendly",
            include_emoji=True
        )

        if post:
            print("\n✓ Generated Post:\n")
            print("-" * 50)
            print(post)
            print("-" * 50)
        else:
            print("\n✗ Failed to generate post")

        # Test honey info generation
        print("\n" + "=" * 50)
        print("Testing Honey Info Generation")
        print("=" * 50 + "\n")

        info = generator.generate_honey_info("ბროწეულის ძმარი")

        if info:
            print("\n✓ Generated Info:\n")
            print("-" * 50)
            print(info)
            print("-" * 50)
        else:
            print("\n✗ Failed to generate info")
