"""Automated Screen Recorder for Home Credit LAP Voice Agent Demo

This script records your screen while interacting with the Streamlit
Voice Agent (or running a Scenario Replay), producing a high-quality .mp4 video
saved to output/recordings/ ready for Google Drive submission.

Usage:
    python scripts/record_screen.py [--duration SECONDS] [--output FILENAME]

Example:
    python scripts/record_screen.py --duration 60
    (Records for 60 seconds or until Ctrl+C is pressed)
"""

import os
import sys
import time
import argparse
import webbrowser
import numpy as np
from PIL import ImageGrab
import cv2

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RECORDINGS_DIR = os.path.join(BASE_DIR, "output", "recordings")
os.makedirs(RECORDINGS_DIR, exist_ok=True)


def record_screen(duration_sec=60, output_name="home_credit_voice_agent_demo.mp4", open_browser=True):
    output_path = os.path.join(RECORDINGS_DIR, output_name)

    print("=" * 65)
    print("  HOME CREDIT LAP VOICE AGENT - AUTOMATED SCREEN RECORDER")
    print("=" * 65)
    print(f"Target file: {output_path}")
    print(f"Duration:    {duration_sec} seconds (Press Ctrl+C anytime to stop early)")

    if open_browser:
        print("\nOpening Streamlit app in your default browser (http://localhost:8501)...")
        try:
            webbrowser.open("http://localhost:8501")
        except Exception:
            pass

    # Grab one frame to determine display resolution
    first_frame = ImageGrab.grab()
    screen_w, screen_h = first_frame.size
    print(f"Detected screen resolution: {screen_w}x{screen_h}")

    # Prepare VideoWriter (20 FPS, mp4v codec)
    fps = 20.0
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(output_path, fourcc, fps, (screen_w, screen_h))

    # Countdown so the user can bring the browser to front
    print("\nStarting recording in:")
    for i in range(3, 0, -1):
        print(f"  {i}...")
        time.sleep(1)
    print(">> RECORDING STARTED! <<")
    print("   Switch to your browser, trigger 'Scenario Replay' or speak.")
    print("   Press Ctrl+C in this terminal when finished.\n")

    start_time = time.time()
    frame_count = 0
    target_frame_interval = 1.0 / fps

    try:
        while True:
            elapsed = time.time() - start_time
            if duration_sec > 0 and elapsed >= duration_sec:
                print("\nReached target duration limit.")
                break

            loop_start = time.time()

            # Capture frame
            img = ImageGrab.grab()
            img_np = np.array(img)
            # PIL returns RGB, OpenCV expects BGR
            frame_bgr = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)
            writer.write(frame_bgr)
            frame_count += 1

            # Progress feedback every 5 seconds
            if frame_count % (int(fps) * 5) == 0:
                sys.stdout.write(f"\rRecording in progress... [{int(elapsed)}s / {duration_sec}s | {frame_count} frames]")
                sys.stdout.flush()

            # Maintain frame rate timing
            compute_time = time.time() - loop_start
            sleep_time = target_frame_interval - compute_time
            if sleep_time > 0:
                time.sleep(sleep_time)

    except KeyboardInterrupt:
        print("\n\nRecording stopped manually by user (Ctrl+C).")
    finally:
        writer.release()

    total_time = max(time.time() - start_time, 0.1)
    file_size_mb = os.path.getsize(output_path) / (1024 * 1024) if os.path.exists(output_path) else 0

    print("\n" + "=" * 65)
    print("  RECORDING COMPLETED SUCCESSFULLY!")
    print("=" * 65)
    print(f"Saved to:   {output_path}")
    print(f"Duration:   {total_time:.1f} seconds")
    print(f"Frames:     {frame_count}")
    print(f"File size:  {file_size_mb:.2f} MB")
    print("\nNext step for submission:")
    print("1. Upload this file to your Google Drive.")
    print("2. Set sharing permissions to 'Anyone with the link can view'.")
    print("3. Paste the share link into the assignment submission form.")
    print("=" * 65)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Automated Screen Recorder for Home Credit LAP Demo")
    parser.add_argument("--duration", type=int, default=60, help="Recording duration in seconds (default: 60)")
    parser.add_argument("--output", type=str, default="home_credit_voice_agent_demo.mp4", help="Output filename")
    parser.add_argument("--no-browser", action="store_true", help="Do not automatically launch browser")

    args = parser.parse_args()
    record_screen(duration_sec=args.duration, output_name=args.output, open_browser=not args.no_browser)
