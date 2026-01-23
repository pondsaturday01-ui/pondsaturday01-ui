"""
organizer.py - File Organizer Script
Sorts files into categorized folders based on file extensions.
"""

import os
import shutil
from pathlib import Path

# ============================================================================
# CONFIGURATION - File Categories
# ============================================================================
CATEGORIES = {
    "Images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".heic", ".webp", ".ico", ".tiff"],
    "Videos": [".mp4", ".mov", ".avi", ".mkv", ".webm", ".flv", ".wmv", ".m4v"],
    "Documents": [".pdf", ".doc", ".docx", ".txt", ".xls", ".xlsx", ".ppt", ".pptx", ".csv", ".odt", ".rtf"],
    "Audio": [".mp3", ".wav", ".flac", ".m4a", ".aac", ".ogg", ".wma"],
    "Archives": [".zip", ".rar", ".7z", ".tar", ".gz", ".iso", ".bz2"],
    "Programs": [".exe", ".msi", ".bat", ".apk", ".dmg", ".sh"],
    "Code": [".py", ".js", ".html", ".css", ".java", ".cpp", ".c", ".h", ".json", ".xml", ".yaml", ".yml", ".md"],
}

# Files to skip (never move these)
SKIP_FILES = {"organizer.py", "desktop.ini", "thumbs.db"}


def get_category(extension: str) -> str:
    """Get category name for a file extension."""
    ext_lower = extension.lower()
    for category, extensions in CATEGORIES.items():
        if ext_lower in extensions:
            return category
    return "Others"


def get_unique_path(dest_folder: Path, filename: str) -> Path:
    """Get a unique path to avoid overwriting existing files."""
    dest_path = dest_folder / filename
    if not dest_path.exists():
        return dest_path

    # File exists, add number suffix
    name = Path(filename).stem
    ext = Path(filename).suffix
    counter = 1
    while True:
        new_name = f"{name}_{counter}{ext}"
        new_path = dest_folder / new_name
        if not new_path.exists():
            return new_path
        counter += 1


def organize_folder(target_dir: str = None):
    """
    Organize files in the target directory into categorized folders.
    
    Args:
        target_dir: Directory to organize. Defaults to current directory.
    """
    if target_dir is None:
        target_dir = os.getcwd()
    
    target_path = Path(target_dir).resolve()
    
    if not target_path.exists():
        print(f"❌ Error: Directory '{target_path}' does not exist.")
        return
    
    if not target_path.is_dir():
        print(f"❌ Error: '{target_path}' is not a directory.")
        return
    
    print(f"\n📂 Organizing files in: {target_path}\n")
    print("-" * 50)
    
    moved_count = 0
    skipped_count = 0
    error_count = 0
    
    # Get all files in the directory (not subdirectories)
    for item in target_path.iterdir():
        # Skip directories
        if item.is_dir():
            continue
        
        filename = item.name
        
        # Skip special files
        if filename.lower() in {f.lower() for f in SKIP_FILES}:
            print(f"⏭️  Skipped: {filename} (protected file)")
            skipped_count += 1
            continue
        
        # Skip hidden files (starting with .)
        if filename.startswith("."):
            print(f"⏭️  Skipped: {filename} (hidden file)")
            skipped_count += 1
            continue
        
        # Get file extension and category
        extension = item.suffix
        if not extension:
            category = "Others"
        else:
            category = get_category(extension)
        
        # Create category folder
        category_folder = target_path / category
        category_folder.mkdir(exist_ok=True)
        
        # Get unique destination path
        dest_path = get_unique_path(category_folder, filename)
        
        # Move the file
        try:
            shutil.move(str(item), str(dest_path))
            print(f"✅ Moved: {filename} → {category}/{dest_path.name}")
            moved_count += 1
        except Exception as e:
            print(f"❌ Error moving {filename}: {e}")
            error_count += 1
    
    # Summary
    print("-" * 50)
    print(f"\n📊 Summary:")
    print(f"   ✅ Moved:   {moved_count} files")
    print(f"   ⏭️  Skipped: {skipped_count} files")
    if error_count > 0:
        print(f"   ❌ Errors:  {error_count} files")
    print(f"\n✨ Done! Your files are now organized.\n")


def main():
    """Main entry point."""
    import sys
    
    if len(sys.argv) > 1:
        # User provided a directory path
        target = sys.argv[1]
    else:
        # Ask user for directory or use current
        print("\n" + "=" * 50)
        print("   📁 FILE ORGANIZER")
        print("=" * 50)
        print("\nThis script will organize files into folders like:")
        print("  Images, Videos, Documents, Audio, Archives, etc.\n")
        
        user_input = input("Enter folder path (or press Enter for current folder): ").strip()
        target = user_input if user_input else None
    
    organize_folder(target)


if __name__ == "__main__":
    main()
