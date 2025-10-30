#!/usr/bin/env python3
"""
Onboard Guide Script

This script helps onboard new implementation guides into the correct folder structure.
It prompts for metadata and automatically organizes the file according to conventions.

Usage:
    python scripts/onboard_guide.py path/to/your-guide.md
"""

import argparse
import pathlib
import shutil
import re
from datetime import datetime

import frontmatter

# --- Configuration ---
GUIDES_ROOT = pathlib.Path(__file__).parent.parent / "guides"
DIVISIONS = ["se", "exd", "pm", "qa"]
MATURITY_LEVELS = [
    "foundational-1",
    "introduction-1", "introduction-2",
    "growth-1", "growth-2",
    "maturity-1", "maturity-2",
    "decline-1", "decline-2",
]


def slugify(text):
    """Convert text to a URL-friendly slug."""
    text = text.lower()
    text = re.sub(r'[\s_]+', '-', text)  # Replace spaces and underscores with hyphens
    text = re.sub(r'[^\w-]', '', text)   # Remove non-alphanumeric characters except hyphens
    return text.strip('-')


def prompt_for_choice(prompt_text, choices):
    """Generic function to prompt user to select from a list of choices."""
    print(prompt_text)
    for i, choice in enumerate(choices, 1):
        print(f"  {i}. {choice}")

    while True:
        try:
            selection = int(input(f"Enter number (1-{len(choices)}): "))
            if 1 <= selection <= len(choices):
                return choices[selection - 1]
            else:
                print("Invalid number. Please try again.")
        except ValueError:
            print("Invalid input. Please enter a number.")


def add_frontmatter(file_path, title, division, maturity):
    """Add or update frontmatter in the Markdown file."""
    try:
        # Try to load existing frontmatter
        post = frontmatter.load(file_path)
    except:
        # If file doesn't exist or has no frontmatter, create new
        post = frontmatter.Post("")
        with open(file_path, 'r') as f:
            post.content = f.read()
    
    # Update metadata (preserve existing, add new)
    post.metadata['title'] = title
    post.metadata['division'] = division
    post.metadata['maturity'] = maturity
    post.metadata['created_at'] = datetime.now().isoformat()
    # Note: No source_url - this marks it as a local-only guide
    
    return post


def main():
    parser = argparse.ArgumentParser(
        description="Onboard a new Markdown guide into the correct folder structure."
    )
    parser.add_argument(
        "md_file",
        type=pathlib.Path,
        help="Path to the Markdown file to onboard."
    )
    args = parser.parse_args()

    if not args.md_file.exists() or not args.md_file.is_file():
        print(f"❌ Error: File not found at '{args.md_file}'")
        return

    print("=" * 60)
    print("📚 Onboarding New Implementation Guide")
    print("=" * 60)

    # 1. Get Guide Title
    default_title = args.md_file.stem.replace('-', ' ').replace('_', ' ').title()
    title = input(f"\n📝 Enter the guide title [{default_title}]: ") or default_title

    # 2. Get Division
    division = prompt_for_choice("\n🏢 Select the division for this guide:", DIVISIONS)

    # 3. Get Maturity Level
    maturity = prompt_for_choice("\n📊 Select the maturity level for this guide:", MATURITY_LEVELS)

    # 4. Construct the path
    slug = slugify(title)
    folder_name = f"{slug}---{maturity}"
    target_dir = GUIDES_ROOT / division / folder_name
    target_file = target_dir / "index.md"

    print("\n" + "=" * 60)
    print("📋 Summary")
    print("=" * 60)
    print(f"  Title:       {title}")
    print(f"  Division:    {division}")
    print(f"  Maturity:    {maturity}")
    print(f"  Folder:      {folder_name}")
    print(f"  Target Path: {target_dir.relative_to(GUIDES_ROOT.parent)}")
    print("=" * 60)

    confirm = input("\n✅ Proceed with creating this structure? (y/n): ").lower()
    if confirm != 'y':
        print("❌ Operation cancelled.")
        return

    # 5. Create directory and prepare file with frontmatter
    try:
        target_dir.mkdir(parents=True, exist_ok=True)
        
        # Add frontmatter to the file
        post = add_frontmatter(args.md_file, title, division, maturity)
        
        # Write to target location
        with open(target_file, 'wb') as f:
            frontmatter.dump(post, f)
        
        # Remove original file if different location
        if args.md_file.resolve() != target_file.resolve():
            args.md_file.unlink()
        
        print(f"\n✅ Success! Guide onboarded to:")
        print(f"   {target_file.relative_to(GUIDES_ROOT.parent)}")
        print("\n💡 Next steps:")
        print("   1. Review the file and make any necessary edits")
        print("   2. Commit the new guide: git add guides/ && git commit -m 'docs: add [guide-name]'")
        print("   3. Push to GitHub: git push origin main")
        print("   4. The content pipeline will automatically update the search index")
        
    except Exception as e:
        print(f"\n❌ Error: Could not create guide. {e}")


if __name__ == "__main__":
    main()
