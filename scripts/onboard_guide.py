#!/usr/bin/env python3
"""
Onboard Guide Script

This script helps onboard new implementation guides into the correct folder structure.
It analyzes files, suggests metadata, and allows batch processing with intelligent defaults.

Usage:
    python scripts/onboard_guide.py path/to/your-guide.md
    python scripts/onboard_guide.py path/to/directory/with/guides/
    python scripts/onboard_guide.py ~/code/additional/staging

Features:
    - Batch division and maturity selection for entire directory
    - Intelligent title detection based on filename cleanup
    - Preview table showing all presumed values before processing
    - Interactive editing of titles before processing
    - Single approval step for entire batch
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


def analyze_file(md_file, division, maturity):
    """Analyze a file and determine presumed metadata."""
    # Generate presumed title from filename
    presumed_title = md_file.stem.replace('-', ' ').replace('_', ' ').title()
    
    return {
        'title': presumed_title,
        'division': division,  # Use the batch division
        'maturity': maturity   # Use the batch maturity
    }


def display_analysis_table(file_analyses):
    """Display a table of file analyses."""
    print(f"\n{'='*80}")
    print("📊 File Analysis & Presumed Metadata")
    print(f"{'='*80}")
    print(f"{'#':<3} {'File':<25} {'Title':<25} {'Div':<4} {'Maturity':<15}")
    print(f"{'-'*80}")
    
    for i, (md_file, analysis) in enumerate(file_analyses.items(), 1):
        print(f"{i:<3} {md_file.name:<25} {analysis['title'][:24]:<25} {analysis['division']:<4} {analysis['maturity']:<15}")


def edit_analysis_interactive(file_analyses):
    """Allow user to edit the analyses interactively."""
    print(f"\n💡 You can edit any presumed values:")
    print("   - Enter file number to edit that file's metadata")
    print("   - Enter 'done' to proceed with current values")
    print("   - Enter 'show' to display the table again")
    
    while True:
        choice = input(f"\nEdit file # (1-{len(file_analyses)}) or 'done': ").strip().lower()
        
        if choice == 'done':
            break
        elif choice == 'show':
            display_analysis_table(file_analyses)
            continue
            
        try:
            file_idx = int(choice) - 1
            if 0 <= file_idx < len(file_analyses):
                file_list = list(file_analyses.keys())
                md_file = file_list[file_idx]
                analysis = file_analyses[md_file]
                
                print(f"\n� Editing: {md_file.name}")
                
                # Edit title
                new_title = input(f"Title [{analysis['title']}]: ").strip()
                if new_title:
                    analysis['title'] = new_title
                
                # Edit division
                print("\nDivisions:")
                for i, div in enumerate(DIVISIONS, 1):
                    marker = "�" if div == analysis['division'] else "  "
                    print(f"  {marker} {i}. {div}")
                
                div_choice = input(f"Division (1-{len(DIVISIONS)}) [{DIVISIONS.index(analysis['division'])+1}]: ").strip()
                if div_choice and div_choice.isdigit():
                    div_idx = int(div_choice) - 1
                    if 0 <= div_idx < len(DIVISIONS):
                        analysis['division'] = DIVISIONS[div_idx]
                
                # Edit maturity
                print("\nMaturity Levels:")
                for i, mat in enumerate(MATURITY_LEVELS, 1):
                    marker = "👉" if mat == analysis['maturity'] else "  "
                    print(f"  {marker} {i}. {mat}")
                
                mat_choice = input(f"Maturity (1-{len(MATURITY_LEVELS)}) [{MATURITY_LEVELS.index(analysis['maturity'])+1}]: ").strip()
                if mat_choice and mat_choice.isdigit():
                    mat_idx = int(mat_choice) - 1
                    if 0 <= mat_idx < len(MATURITY_LEVELS):
                        analysis['maturity'] = MATURITY_LEVELS[mat_idx]
                
                print(f"✅ Updated {md_file.name}")
                display_analysis_table(file_analyses)
            else:
                print("❌ Invalid file number")
        except ValueError:
            print("❌ Please enter a valid number or 'done'")


def process_files_batch(file_analyses, force=False):
    """Process all files with their confirmed metadata."""
    successful = 0
    skipped = 0
    
    for i, (md_file, analysis) in enumerate(file_analyses.items(), 1):
        print(f"\n{'='*20} Processing {i}/{len(file_analyses)}: {md_file.name} {'='*20}")
        
        # Construct the path
        slug = slugify(analysis['title'])
        folder_name = f"{slug}---{analysis['maturity']}"
        target_dir = GUIDES_ROOT / analysis['division'] / folder_name
        target_file = target_dir / "index.md"

        # Check if guide already exists
        action = check_existing_guide(target_file, md_file)
        
        if action == "skip" and not force:
            print(f"⏭️  Guide already exists with identical content:")
            print(f"   {target_file.relative_to(GUIDES_ROOT.parent)}")
            skipped += 1
            continue
        
        print(f"{'🆕 Creating' if action == 'new' else '🔄 Updating'}: {analysis['title']}")
        print(f"   Target: {target_dir.relative_to(GUIDES_ROOT.parent)}")

        try:
            target_dir.mkdir(parents=True, exist_ok=True)
            
            # Add frontmatter to the file
            is_update = (action == "update")
            post = add_frontmatter(md_file, analysis['title'], analysis['division'], analysis['maturity'], is_update)
            
            # Write to target location
            with open(target_file, 'wb') as f:
                frontmatter.dump(post, f)
            
            # Remove original file if different location
            if md_file.resolve() != target_file.resolve():
                md_file.unlink()
            
            print(f"✅ Success!")
            successful += 1
            
        except Exception as e:
            print(f"❌ Error: Could not create guide. {e}")
            skipped += 1

    return successful, skipped


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

    # Ask for division once for the entire batch
    if len(md_files) == 1:
        print(f"\n🏢 Select the division for this guide:")
    else:
        print(f"\n🏢 Select the division for all {len(md_files)} guides:")
    
    for i, div in enumerate(DIVISIONS, 1):
        print(f"  {i}. {div}")
    
    while True:
        try:
            div_choice = int(input(f"Enter number (1-{len(DIVISIONS)}): "))
            if 1 <= div_choice <= len(DIVISIONS):
                batch_division = DIVISIONS[div_choice - 1]
                break
            else:
                print("Invalid number. Please try again.")
        except ValueError:
            print("Invalid input. Please enter a number.")

    # Ask for maturity once for the entire batch
    if len(md_files) == 1:
        print(f"\n📊 Select the maturity level for this guide:")
    else:
        print(f"\n📊 Select the maturity level for all {len(md_files)} guides:")
    
    for i, mat in enumerate(MATURITY_LEVELS, 1):
        print(f"  {i}. {mat}")
    
    while True:
        try:
            mat_choice = int(input(f"Enter number (1-{len(MATURITY_LEVELS)}): "))
            if 1 <= mat_choice <= len(MATURITY_LEVELS):
                batch_maturity = MATURITY_LEVELS[mat_choice - 1]
                break
            else:
                print("Invalid number. Please try again.")
        except ValueError:
            print("Invalid input. Please enter a number.")

    # Analyze all files and generate presumed metadata
    print(f"\n🤖 Generating presumed titles for division '{batch_division}', maturity '{batch_maturity}'...")
    file_analyses = {}
    for md_file in md_files:
        file_analyses[md_file] = analyze_file(md_file, batch_division, batch_maturity)

    # Display analysis table
    display_analysis_table(file_analyses)
    
    # Ask for confirmation or edits
    print(f"\n✅ Proceed with these values?")
    print("   'y' = Yes, process all files with current metadata")
    print("   'e' = Edit metadata for specific files")
    print("   'n' = Cancel operation")
    
    choice = input("Your choice (y/e/n): ").strip().lower()
    
    if choice == 'n':
        print("❌ Operation cancelled.")
        return
    elif choice == 'e':
        edit_analysis_interactive(file_analyses)
        print(f"\n📋 Final metadata:")
        display_analysis_table(file_analyses)
        
        final_confirm = input(f"\n✅ Process all {len(md_files)} files with this metadata? (y/n): ").lower()
        if final_confirm != 'y':
            print("❌ Operation cancelled.")
            return
    elif choice != 'y':
        print("❌ Invalid choice. Operation cancelled.")
        return

    # Process all files
    print(f"\n{'='*60}")
    print("🚀 Processing Files")
    print(f"{'='*60}")
    
    successful, skipped = process_files_batch(file_analyses, args.force)

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
