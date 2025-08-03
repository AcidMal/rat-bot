#!/usr/bin/env python3
"""
YouTube Cookies Setup Utility for Discord Bot
This script helps you set up cookies for yt-dlp to bypass YouTube restrictions.
"""

import os
import sys
import shutil
from pathlib import Path

def print_header():
    print("=" * 60)
    print("🍪 YouTube Cookies Setup for Discord Bot")
    print("=" * 60)
    print()

def print_instructions():
    print("📋 How to extract YouTube cookies:")
    print()
    print("Method 1: Using Browser Extension (Recommended)")
    print("1. Install 'Get cookies.txt LOCALLY' extension in your browser")
    print("2. Go to youtube.com and log in")
    print("3. Click the extension and download cookies.txt")
    print("4. Save it as 'cookies.txt' in your bot directory")
    print()
    print("Method 2: Using yt-dlp (Advanced)")
    print("1. Run: yt-dlp --cookies-from-browser chrome --print-json")
    print("2. This will show you the cookies format")
    print()
    print("Method 3: Manual Export")
    print("1. Use browser dev tools to export cookies")
    print("2. Save in Netscape cookie format")
    print()

def check_cookies():
    """Check if cookies file exists and is valid"""
    cookies_paths = [
        'cookies.txt',
        '/rat-bot/cookies.txt',
        os.path.expanduser('~/cookies.txt'),
        'data/cookies.txt'
    ]
    
    found_cookies = []
    for path in cookies_paths:
        if os.path.exists(path):
            try:
                with open(path, 'r') as f:
                    content = f.read().strip()
                    if content and not content.startswith('#'):
                        # Basic validation - should have youtube.com entries
                        if 'youtube.com' in content:
                            found_cookies.append(path)
                        else:
                            print(f"⚠️  Found {path} but it doesn't contain YouTube cookies")
                    elif content.startswith('# Netscape HTTP Cookie File'):
                        # Empty but valid format
                        print(f"📁 Found empty cookies file: {path}")
                    else:
                        print(f"❌ Invalid cookies format: {path}")
            except Exception as e:
                print(f"❌ Error reading {path}: {e}")
    
    return found_cookies

def setup_cookies():
    """Interactive cookies setup"""
    print_header()
    
    # Check existing cookies
    existing_cookies = check_cookies()
    
    if existing_cookies:
        print("✅ Found existing cookies:")
        for cookie_path in existing_cookies:
            print(f"   📄 {cookie_path}")
        print()
        
        choice = input("Do you want to replace existing cookies? (y/N): ").lower().strip()
        if choice != 'y':
            print("✅ Using existing cookies.")
            return True
    
    print_instructions()
    
    # Ask user for cookies file location
    print("📂 Where is your cookies.txt file?")
    source_path = input("Enter full path to your cookies.txt file: ").strip()
    
    if not source_path:
        print("❌ No path provided.")
        return False
    
    # Expand user path
    source_path = os.path.expanduser(source_path)
    
    if not os.path.exists(source_path):
        print(f"❌ File not found: {source_path}")
        return False
    
    # Choose destination
    print("\n📁 Where should we place the cookies file?")
    print("1. Bot directory (./cookies.txt) - Recommended")
    print("2. Data directory (./data/cookies.txt)")
    print("3. Home directory (~/cookies.txt)")
    print("4. Custom path")
    
    choice = input("Choose option (1-4): ").strip()
    
    if choice == '1':
        dest_path = 'cookies.txt'
    elif choice == '2':
        os.makedirs('data', exist_ok=True)
        dest_path = 'data/cookies.txt'
    elif choice == '3':
        dest_path = os.path.expanduser('~/cookies.txt')
    elif choice == '4':
        dest_path = input("Enter destination path: ").strip()
        dest_path = os.path.expanduser(dest_path)
    else:
        print("❌ Invalid choice.")
        return False
    
    # Copy cookies file
    try:
        shutil.copy2(source_path, dest_path)
        print(f"✅ Cookies copied to: {dest_path}")
        
        # Verify the copied file
        with open(dest_path, 'r') as f:
            content = f.read()
            if 'youtube.com' in content:
                print("✅ Cookies file contains YouTube entries.")
            else:
                print("⚠️  Warning: Cookies file doesn't contain YouTube entries.")
        
        return True
        
    except Exception as e:
        print(f"❌ Error copying cookies: {e}")
        return False

def test_cookies():
    """Test cookies with yt-dlp"""
    print("\n🧪 Testing cookies with yt-dlp...")
    
    try:
        import yt_dlp
        
        cookies_paths = [
            'cookies.txt',
            '/rat-bot/cookies.txt',
            os.path.expanduser('~/cookies.txt'),
            'data/cookies.txt'
        ]
        
        cookies_file = None
        for path in cookies_paths:
            if os.path.exists(path):
                cookies_file = path
                break
        
        if not cookies_file:
            print("❌ No cookies file found for testing.")
            return False
        
        print(f"🔍 Testing with cookies: {cookies_file}")
        
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'cookiefile': cookies_file,
            'extract_flat': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Test with a simple search
            info = ydl.extract_info("ytsearch1:test", download=False)
            if info and 'entries' in info and info['entries']:
                print("✅ Cookies test successful! YouTube access is working.")
                return True
            else:
                print("⚠️  Cookies test inconclusive.")
                return False
                
    except ImportError:
        print("❌ yt-dlp not installed. Run: pip install yt-dlp")
        return False
    except Exception as e:
        print(f"❌ Cookies test failed: {e}")
        return False

def main():
    if len(sys.argv) > 1 and sys.argv[1] == '--test':
        test_cookies()
        return
    
    success = setup_cookies()
    
    if success:
        print("\n" + "=" * 60)
        print("🎉 Cookies setup complete!")
        print()
        print("🎵 Your bot now has enhanced YouTube access:")
        print("   • Age-restricted videos")
        print("   • Region-locked content")
        print("   • Better rate limiting")
        print()
        print("💡 Usage:")
        print("   • Regular: !play song name")
        print("   • YouTube: !play yt:song name")
        print()
        print("🔧 Test cookies: python setup_cookies.py --test")
        print("=" * 60)
    else:
        print("\n❌ Cookies setup failed. Please try again.")
        sys.exit(1)

if __name__ == "__main__":
    main()