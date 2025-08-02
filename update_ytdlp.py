#!/usr/bin/env python3
"""
yt-dlp Update Script
This script helps update yt-dlp to fix SSL certificate issues.
"""

import subprocess
import sys
import os

def update_ytdlp():
    """Update yt-dlp to the latest version."""
    print("🔄 Updating yt-dlp...")
    
    try:
        # Update yt-dlp
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", "--upgrade", "yt-dlp"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ yt-dlp updated successfully!")
            
            # Show the new version
            version_result = subprocess.run([
                sys.executable, "-m", "pip", "show", "yt-dlp"
            ], capture_output=True, text=True)
            
            if version_result.returncode == 0:
                for line in version_result.stdout.split('\n'):
                    if line.startswith('Version:'):
                        print(f"📦 New version: {line.split(':')[1].strip()}")
                        break
        else:
            print(f"❌ Failed to update yt-dlp:")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ Error updating yt-dlp: {e}")
        return False
    
    return True

def check_ytdlp_version():
    """Check the current yt-dlp version."""
    try:
        result = subprocess.run([
            sys.executable, "-m", "pip", "show", "yt-dlp"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            for line in result.stdout.split('\n'):
                if line.startswith('Version:'):
                    version = line.split(':')[1].strip()
                    print(f"📦 Current yt-dlp version: {version}")
                    return version
        else:
            print("❌ Could not determine yt-dlp version")
            return None
            
    except Exception as e:
        print(f"❌ Error checking yt-dlp version: {e}")
        return None

def main():
    """Main function."""
    print("🎵 yt-dlp Update Script")
    print("=======================")
    
    # Check current version
    current_version = check_ytdlp_version()
    
    if current_version:
        print(f"\nCurrent version: {current_version}")
    
    # Ask user if they want to update
    response = input("\nDo you want to update yt-dlp? (y/N): ").strip().lower()
    
    if response in ['y', 'yes']:
        if update_ytdlp():
            print("\n✅ Update completed successfully!")
            print("🎵 You can now try playing music again.")
        else:
            print("\n❌ Update failed. Please try manually:")
            print("pip install --upgrade yt-dlp")
    else:
        print("\n⏭️ Update cancelled.")
    
    print("\n💡 If you still have SSL issues after updating:")
    print("1. Try playing a different song")
    print("2. Check your internet connection")
    print("3. The bot has been configured to bypass SSL verification")
    print("4. Use the /fixmusic command in Discord (admin only)")

if __name__ == "__main__":
    main() 