#!/usr/bin/env python3
"""
Onboard Guide Script

This script helps onboard new implementation guides into the correct folder structure.
It prompts for metadata and automatically organizes files according to conventions.

Usage:
    python scripts/onboard_guide.py path/to/your-guide.md
    python scripts/onboard_guide.py path/to/directory/with/guides/
    python scripts/onboard_guide.py ~/code/additional/staging
"""

import argparse
import pathlib
import shutil
import re
from datetime import datetime
import hashlib

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


def get_file_hash(file_path):
    """Calculate MD5 hash of file content for change detection."""
    hasher = hashlib.md5()
    with open(file_path, 'rb') as f:
        hasher.update(f.read())
    return hasher.hexdigest()


def slugify(text):
    """Convert text to a URL-friendly slug."""
    text = text.lower()
    text = re.sub(r'[\s_]+', '-', text)
    text = re.sub(r'[^\w-]', '', text)
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


def add_frontmatter(file_path, title, division, maturity, is_update=False):
    """Add or update frontmatter in the Markdown file."""
    try:
        post = frontmatter.load(file_path)
    except:
        post = frontmatter.Post("")
        with open(file_path, 'r') as f:
            post.content = f.read()
    
    # Update metadata
    post.metadata['title'] = title
    post.metadata['division'] = division
    post.metadata['maturity'] = maturity
    
    if is_update:
        post.metadata['updated_at'] = datetime.now().isoformat()
    else:
        post.metadata['created_at'] = datetime.now().isoformat()
    
    # Calculate content hash for change detection
    post.metadata['content_hash'] = hashlib.md5(post.content.encode()).hexdigest()
    
    # Note: No source_url - this marks it as a local-only guide
    
    return post


def check_existing_guide(target_file, source_file):
    """Check if guide exists and determine if update is needed."""
    if not target_file.exists():
        return "new"
    
    # Load existing guide
    existing_post = frontmatter.load(target_file)
    existing_hash = existing_post.metadata.get('content_hash', '')
    
    # Calculate hash of source file
    with open(source_file, 'r') as f:
        source_content = f.read()
        # Try to extract content without frontmatter
        try:
            source_post = frontmatter.loads(source_content)
            source_hash = hashlib.md5(source_post.content.encode()).hexdigest()
        except:
            source_hash = hashlib.md5(source_content.encode()).hexdigest()
    
    if existing_hash == source_hash:
        return "skip"  # Content hasn't changed
    else:
        return "update"  # Content has changed


def process_single_file(md_file, force=False):
    """Process a single markdown file."""
    print("=" * 60)
    print("📚 Onboarding New Implementation Guide")
    print("=" * 60)

    # 1. Get Guide Title
    default_title = md_file.stem.replace('-', ' ').replace('_', ' ').title()
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

    # 5. Check if guide already exists
    action = check_existing_guide(target_file, md_file)
    
    if action == "skip" and not force:
        print(f"\n⏭️  Guide already exists with identical content:")
        print(f"   {target_file.relative_to(GUIDES_ROOT.parent)}")
        print("\n💡 Use --force to update anyway")
        return False
    
    print("\n" + "=" * 60)
    print("📋 Summary")
    print("=" * 60)
    print(f"  Action:      {'🆕 New' if action == 'new' else '🔄 Update'}")
    print(f"  Title:       {title}")
    print(f"  Division:    {division}")
    print(f"  Maturity:    {maturity}")
    print(f"  Folder:      {folder_name}")
    print(f"  Target Path: {target_dir.relative_to(GUIDES_ROOT.parent)}")
    print("=" * 60)

    confirm = input(f"\n✅ Proceed with {'creating' if action == 'new' else 'updating'} this guide? (y/n): ").lower()
    if confirm != 'y':
        print("❌ Operation cancelled.")
        return False

    # 6. Create directory and prepare file with frontmatter
    try:
        target_dir.mkdir(parents=True, exist_ok=True)
        
        # Add frontmatter to the file
        is_update = (action == "update")
        post = add_frontmatter(md_file, title, division, maturity, is_update)
        
        # Write to target location
        with open(target_file, 'wb') as f:
            frontmatter.dump(post, f)
        
        # Remove original file if different location
        if md_file.resolve() != target_file.resolve():
            md_file.unlink()
        
        action_verb = "updated" if is_update else "onboarded"
        print(f"\n✅ Success! Guide {action_verb} at:")
        print(f"   {target_file.relative_to(GUIDES_ROOT.parent)}")
        return True
        
    except Exception as e:
        print(f"\n❌ Error: Could not create guide. {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Onboard Markdown guides into the correct folder structure."
    )
    parser.add_argument(
        "path",
        type=pathlib.Path,
        help="Path to the Markdown file or directory containing Markdown files to onboard."
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force update even if content hasn't changed"
    )
    args = parser.parse_args()

    if not args.path.exists():
        print(f"❌ Error: Path not found at '{args.path}'")
        return

    # Collect markdown files
    md_files = []
    if args.path.is_file():
        if args.path.suffix.lower() == '.md':
            md_files = [args.path]
        else:
            print(f"❌ Error: File '{args.path}' is not a Markdown file")
            return
    elif args.path.is_dir():
        md_files = list(args.path.glob("*.md"))
        if not md_files:
            print(f"❌ No Markdown files found in directory '{args.path}'")
            return
    else:
        print(f"❌ Error: '{args.path}' is neither a file nor a directory")
        return

    print(f"🔍 Found {len(md_files)} Markdown file(s) to process:")
    for md_file in md_files:
        print(f"   📄 {md_file.name}")
    
    if len(md_files) > 1:
        confirm = input(f"\n✅ Process all {len(md_files)} files? (y/n): ").lower()
        if confirm != 'y':
            print("❌ Operation cancelled.")
            return

    # Process each file
    successful = 0
    skipped = 0
    
    for i, md_file in enumerate(md_files, 1):
        print(f"\n{'='*20} Processing {i}/{len(md_files)}: {md_file.name} {'='*20}")
        
        success = process_single_file(md_file, args.force)
        if success:
            successful += 1
        else:
            skipped += 1

    # Summary
    print(f"\n{'='*60}")
    print("📊 Processing Summary")
    print(f"{'='*60}")
    print(f"  ✅ Successfully onboarded: {successful}")
    print(f"  ⏭️  Skipped: {skipped}")
    print(f"  📁 Total processed: {len(md_files)}")
    
    if successful > 0:
        print(f"\n💡 Next steps:")
        print(f"   1. Review the onboarded files")
        print(f"   2. Commit the new guides: git add guides/ && git commit -m 'docs: add {successful} implementation guides'")
        print(f"   3. Push to GitHub: git push origin main")
        print(f"   4. The content pipeline will automatically update the search index")


if __name__ == "__main__":
    main()
