import os
import subprocess

APP_NAME = "LyricVision"
VERSION = "1.0.0"

APP_PATH = f"dist/{APP_NAME}.app"
DMG_NAME = f"{APP_NAME}-{VERSION}.dmg"

def build_dmg():
    if not os.path.exists(APP_PATH):
        print("❌ App not found. Run setup.py first.")
        return

    cmd = [
        "create-dmg",
        "--volname", APP_NAME,
        "--window-size", "600", "400",
        "--icon-size", "100",
        "--app-drop-link", "450", "200",
        DMG_NAME,
        APP_PATH
    ]

    print("📦 Creating DMG...")
    subprocess.run(cmd)
    print(f"✅ DMG created: {DMG_NAME}")

if __name__ == "__main__":
    build_dmg()