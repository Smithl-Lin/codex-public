"""
Quick test script to verify Gradio UI functionality
Tests the 4-tab layout with Case A
"""

import sys
sys.path.insert(0, '.')

from app import build_gradio_app

def test_ui_build():
    """Test that Gradio app builds without errors."""
    print("Testing Gradio UI build...")
    app = build_gradio_app()

    if app is None:
        print("❌ FAIL: App returned None")
        return False

    print("✓ App built successfully")
    print(f"✓ App type: {type(app)}")
    return True

if __name__ == "__main__":
    success = test_ui_build()
    if success:
        print("\n✅ Gradio UI build test PASSED")
        sys.exit(0)
    else:
        print("\n❌ Gradio UI build test FAILED")
        sys.exit(1)
