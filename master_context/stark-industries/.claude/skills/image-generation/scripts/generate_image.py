#!/usr/bin/env python3
"""
Image Generation Script using Google's Gemini/Imagen API.

This is the core image generation script that wraps Google's generative AI APIs.
It supports both Gemini multimodal models and dedicated Imagen models.

Features:
- Text-to-image generation
- Image editing with input images (single or multiple)
- Multi-turn conversational refinement

Usage:
    # New image generation
    python generate_image.py --prompt "A cat in space" --output /tmp/cat.png

    # Edit existing image
    python generate_image.py --prompt "Make it blue" --output /tmp/cat_blue.png --input-image /tmp/cat.png

    # Combine multiple images
    python generate_image.py --prompt "Merge these into one scene" --output /tmp/merged.png \
        --input-image /tmp/image1.png --input-image /tmp/image2.png
"""

import argparse
import io
import os
import sys
from pathlib import Path
from typing import Optional, List


def is_imagen_model(model: str) -> bool:
    """Check if model is an Imagen model (uses generate_images API)."""
    return model.startswith("imagen-")


def load_input_images(image_paths: List[str]) -> List:
    """
    Load input images from file paths.

    Args:
        image_paths: List of file paths to images

    Returns:
        List of PIL Image objects
    """
    from PIL import Image

    images = []
    for path in image_paths:
        if not os.path.exists(path):
            print(f"WARNING: Input image not found: {path}", file=sys.stderr)
            continue
        try:
            img = Image.open(path)
            images.append(img)
            print(f"Loaded input image: {path} ({img.size[0]}x{img.size[1]})", file=sys.stderr)
        except Exception as e:
            print(f"WARNING: Failed to load image {path}: {e}", file=sys.stderr)

    return images


def generate_with_gemini(
    client,
    model: str,
    prompt: str,
    aspect_ratio: Optional[str],
    image_size: str = "2K",
    input_images: Optional[List] = None
):
    """
    Generate or edit image using Gemini multimodal API.

    Args:
        client: Gemini API client
        model: Model name (e.g., "gemini-2.5-flash-image")
        prompt: Text prompt for generation or editing instructions
        aspect_ratio: Output aspect ratio
        image_size: Output resolution (1K, 2K, 4K)
        input_images: Optional list of PIL Image objects for editing

    Returns:
        PIL Image or None
    """
    from google.genai import types
    from PIL import Image

    config_kwargs = {"response_modalities": ["TEXT", "IMAGE"]}

    # Try to configure image settings if ImageConfig is available
    try:
        image_config_kwargs = {}
        if aspect_ratio:
            image_config_kwargs["aspect_ratio"] = aspect_ratio
        if image_size:
            image_config_kwargs["image_size"] = image_size
        if image_config_kwargs:
            config_kwargs["image_config"] = types.ImageConfig(**image_config_kwargs)
    except (AttributeError, TypeError) as e:
        # ImageConfig may not be available in this version of the API
        print(f"Note: ImageConfig not available, using default settings: {e}", file=sys.stderr)

    # Build contents: text prompt + optional input images
    # Gemini expects: [prompt, image1, image2, ...] or just prompt
    if input_images:
        # For editing: include input images with the prompt
        contents = [prompt] + input_images
        print(f"Editing mode: {len(input_images)} input image(s) + prompt", file=sys.stderr)
    else:
        # For new generation: just the prompt
        contents = prompt
        print("Generation mode: text prompt only", file=sys.stderr)

    try:
        response = client.models.generate_content(
            model=model,
            contents=contents,
            config=types.GenerateContentConfig(**config_kwargs)
        )
    except Exception as e:
        # Some models don't support certain config options - retry with minimal config
        if ("aspect ratio" in str(e).lower() or "image_size" in str(e).lower()) and "image_config" in config_kwargs:
            print(f"Note: Model doesn't support some config options, retrying with defaults...", file=sys.stderr)
            del config_kwargs["image_config"]
            response = client.models.generate_content(
                model=model,
                contents=contents,
                config=types.GenerateContentConfig(**config_kwargs)
            )
        else:
            raise

    for part in response.candidates[0].content.parts:
        if part.inline_data is not None:
            return Image.open(io.BytesIO(part.inline_data.data))
        elif part.text is not None:
            print(f"Model response: {part.text}", file=sys.stderr)

    return None


def generate_with_imagen(client, model: str, prompt: str, aspect_ratio: str):
    """Generate image using Imagen dedicated API."""
    from google.genai import types

    response = client.models.generate_images(
        model=model,
        prompt=prompt,
        config=types.GenerateImagesConfig(
            number_of_images=1,
            aspect_ratio=aspect_ratio,
            include_rai_reason=True
        )
    )

    if response.generated_images:
        return response.generated_images[0].image

    return None


def main():
    parser = argparse.ArgumentParser(
        description="Generate or edit images using Google's Gemini/Imagen API"
    )
    parser.add_argument("--prompt", required=True, help="Text description or editing instructions")
    parser.add_argument("--output", required=True, help="Output file path")
    parser.add_argument(
        "--input-image",
        action="append",
        dest="input_images",
        default=[],
        help="Input image(s) for editing. Can be specified multiple times. "
             "Max 3 for Gemini 2.5 Flash, max 14 for Gemini 3 Pro."
    )
    parser.add_argument(
        "--model",
        default=os.getenv("GOOGLE_IMAGE_MODEL", "gemini-2.0-flash-preview-image-generation"),
        help="Model ID (default from GOOGLE_IMAGE_MODEL env or gemini-2.0-flash-preview-image-generation aka Nano Banana Pro)"
    )
    parser.add_argument(
        "--image-size",
        default="2K",
        choices=["1K", "2K", "4K"],
        help="Image resolution (default: 2K). 4K for highest quality."
    )
    parser.add_argument(
        "--aspect-ratio",
        default="16:9",
        choices=["1:1", "16:9", "9:16", "4:3", "3:4", "3:2", "2:3", "4:5", "5:4", "21:9"],
        help="Aspect ratio (default: 16:9)"
    )
    args = parser.parse_args()

    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("ERROR: GOOGLE_API_KEY environment variable not set", file=sys.stderr)
        sys.exit(1)

    try:
        from google import genai
    except ImportError as e:
        print(f"ERROR: Missing required package: {e}", file=sys.stderr)
        print("Install with: pip install google-genai Pillow", file=sys.stderr)
        sys.exit(1)

    # Load input images if provided
    input_images = None
    if args.input_images:
        input_images = load_input_images(args.input_images)
        if not input_images:
            print("WARNING: No valid input images loaded, proceeding with generation mode", file=sys.stderr)
            input_images = None

    mode = "editing" if input_images else "generation"
    print(f"Mode: {mode} | Model: {args.model}", file=sys.stderr)

    try:
        client = genai.Client(api_key=api_key)

        if is_imagen_model(args.model):
            if input_images:
                print("WARNING: Imagen models don't support image editing, ignoring input images", file=sys.stderr)
            image = generate_with_imagen(client, args.model, args.prompt, args.aspect_ratio)
        else:
            image = generate_with_gemini(
                client,
                args.model,
                args.prompt,
                args.aspect_ratio,
                args.image_size,
                input_images=input_images
            )

        if image is None:
            print("ERROR: No image was generated", file=sys.stderr)
            sys.exit(1)

        output_dir = os.path.dirname(args.output)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)

        image.save(args.output)
        print(f"SUCCESS: Image saved to {args.output}", file=sys.stderr)

    except Exception as e:
        print(f"ERROR: Failed to generate image: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
