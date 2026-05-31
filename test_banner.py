#!/usr/bin/env python3
"""Test script to display the QbitShield SDK installation banner."""

import sys

QBITSHIELD_BANNER = """
 ██████╗ ██████╗ ██╗████████╗███████╗██╗  ██╗██╗███████╗██╗     ██████╗ 
██╔═══██╗██╔══██╗██║╚══██╔══╝██╔════╝██║  ██║██║██╔════╝██║     ██╔══██╗
██║   ██║██████╔╝██║   ██║   ███████╗███████║██║█████╗  ██║     ██║  ██║
██║▄▄ ██║██╔══██╗██║   ██║   ╚════██║██╔══██║██║██╔══╝  ██║     ██║  ██║
╚██████╔╝██████╔╝██║   ██║   ███████║██║  ██║██║███████╗███████╗██████╔╝
 ╚══▀▀═╝ ╚═════╝ ╚═╝   ╚═╝   ╚══════╝╚═╝  ╚═╝╚═╝╚══════╝╚══════╝╚═════╝ 

                          P Y T H O N   S D K   v 0 . 1 . 0
"""

def print_banner():
    """Print the QbitShield banner."""
    try:
        print(QBITSHIELD_BANNER, file=sys.stderr, flush=True)
    except (AttributeError, OSError):
        # Fallback to stdout if stderr fails
        try:
            print(QBITSHIELD_BANNER, flush=True)
        except:
            pass

if __name__ == "__main__":
    print_banner()
    print("\n✅ This is the banner that appears during SDK installation!")
    print("   Run: cd qbitshield-sdk && pip install -e .")
    print("   (The banner should appear during installation)\n")
