"""
Image Generator using Google Vertex AI (Imagen)
================================================
This module handles image generation using Google Cloud's Vertex AI Imagen model.
Supports generating high-quality, realistic product photos for organic honey marketing.
"""

import os
import base64
from typing import Optional
from google.cloud import aiplatform
from google.cloud.aiplatform.gapic.schema import predict
from vertexai.preview.vision_models import ImageGenerationModel


class ImageGenerator:
    """Generates images using Google Vertex AI Imagen model."""

    def __init__(self, project_id: str, location: str = "us-central1"):
        """
        Initialize the Image Generator.

        Args:
            project_id: Google Cloud Project ID
            location: GCP region (default: us-central1)
        """
        self.project_id = project_id
        self.location = location

        # Initialize Vertex AI
        aiplatform.init(project=project_id, location=location)

        print(f"✓ Image Generator initialized (Project: {project_id}, Location: {location})")

    def generate_honey_product_image(
        self,
        prompt: str,
        negative_prompt: str = "low quality, blurry, distorted, text, watermark",
        number_of_images: int = 1,
        output_path: str = "generated_image.png"
    ) -> Optional[str]:
        """
        Generate a product image using Imagen.

        Args:
            prompt: Text description of the desired image (in English)
            negative_prompt: What to avoid in the image
            number_of_images: Number of images to generate (default: 1)
            output_path: Where to save the generated image

        Returns:
            Path to the saved image file, or None if generation failed
        """
        try:
            # Load the Imagen model
            model = ImageGenerationModel.from_pretrained("imagegeneration@006")

            # Generate images
            print(f"🎨 Generating image with prompt: {prompt[:100]}...")

            response = model.generate_images(
                prompt=prompt,
                negative_prompt=negative_prompt,
                number_of_images=number_of_images,
                aspect_ratio="1:1",  # Square format for social media
                safety_filter_level="block_some",
                person_generation="allow_adult",
            )

            # Save the first generated image
            if response.images:
                image = response.images[0]

                # Save to file
                image.save(location=output_path, include_generation_parameters=False)

                print(f"✓ Image saved to: {output_path}")
                return output_path
            else:
                print("✗ No images were generated")
                return None

        except Exception as e:
            print(f"✗ Error generating image: {e}")
            return None

    def generate_honey_marketing_image(self, honey_type: str = "ბროწეულის ძმარი") -> Optional[str]:
        """
        Generate a marketing image specifically for honey products.

        Args:
            honey_type: Type of honey in Georgian (e.g., "ბროწეულის ძმარი")

        Returns:
            Path to the saved image file
        """
        # Create a detailed prompt in English (Imagen works best with English)
        prompt = f"""
        Professional product photography: A glass jar of organic golden honey on a rustic wooden table,
        natural sunlight streaming through a window, warm tones, honey dripping from wooden dipper,
        wildflowers in soft focus background, high resolution, commercial quality, appetizing,
        premium organic product, clean aesthetic, no text, no labels
        """

        negative_prompt = """
        low quality, blurry, distorted, text overlay, watermark, logo, brand name,
        artificial lighting, plastic, modern kitchen, cluttered background,
        oversaturated colors, cartoon, illustration
        """

        output_path = f"honey_product_{honey_type.replace(' ', '_')}.png"

        return self.generate_honey_product_image(
            prompt=prompt.strip(),
            negative_prompt=negative_prompt.strip(),
            output_path=output_path
        )


# Example usage and testing
if __name__ == "__main__":
    # This is for testing only - normally called from main.py

    # Get credentials from environment
    project_id = os.getenv("GOOGLE_CLOUD_PROJECT")

    if not project_id:
        print("⚠️  Please set GOOGLE_CLOUD_PROJECT environment variable")
        print("Example: export GOOGLE_CLOUD_PROJECT='your-project-id'")
    else:
        # Initialize generator
        generator = ImageGenerator(project_id=project_id)

        # Generate a test image
        result = generator.generate_honey_marketing_image("ბროწეულის ძმარი")

        if result:
            print(f"\n✓ Success! Image generated: {result}")
        else:
            print("\n✗ Failed to generate image")
