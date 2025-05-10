#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test dependencies for deepwiki-to-md
"""

import sys


def test_imports():
    """Test that all necessary dependencies can be imported."""
    dependencies = [
        "playwright",
        "bs4",  # BeautifulSoup4
        "markdownify",
    ]

    success = True
    print("Checking dependencies:")

    for dep in dependencies:
        try:
            __import__(dep)
            print(f"✅ {dep}: Successfully imported")
        except ImportError as e:
            print(f"❌ {dep}: FAILED - {e}")
            success = False

    return success


if __name__ == "__main__":
    print("Testing dependencies for deepwiki-to-md...")
    success = test_imports()

    if success:
        print("\nAll dependencies are available.")
        sys.exit(0)
    else:
        print("\nSome dependencies are missing. Please install them with:")
        print("pip install playwright beautifulsoup4 markdownify")
        print("And then run: playwright install")
        sys.exit(1)
