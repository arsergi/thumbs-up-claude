#!/usr/bin/env python3
"""
Thumbs Up / Thumbs Down gesture approval for Claude Code.

Run this in a separate terminal while using Claude Code.
Show a thumbs up to approve (sends 'y' + Enter) or
thumbs down to deny (sends 'n' + Enter) permission prompts.
"""

import sys
import time
import argparse
from pathlib import Path

import cv2
import mediapipe as mp
from mediapipe.tasks import python as mp_python
from mediapipe.tasks.python import vision
from pynput.keyboard import Controller, Key

MODEL_PATH = str(Path(__file__).parent / "gesture_recognizer.task")

THUMB_UP_GESTURE = "Thumb_Up"
THUMB_DOWN_GESTURE = "Thumb_Down"

GREEN = (0, 200, 0)
RED = (0, 0, 220)
WHITE = (255, 255, 255)
GRAY = (60, 60, 60)
YELLOW = (0, 220, 255)

keyboard = Controller()


def send_approval():
    keyboard.press("y")
    keyboard.release("y")
    keyboard.press(Key.enter)
    keyboard.release(Key.enter)


def send_denial():
    keyboard.press("n")
    keyboard.release("n")
    keyboard.press(Key.enter)
    keyboard.release(Key.enter)


def draw_status(frame, gesture_name, confidence, cooldown_remaining):
    h, w = frame.shape[:2]
    overlay = frame.copy()

    if gesture_name == THUMB_UP_GESTURE:
        color = GREEN
        label = "APPROVED"
        icon = "👍"
    elif gesture_name == THUMB_DOWN_GESTURE:
        color = RED
        label = "DENIED"
        icon = "👎"
    else:
        color = GRAY
        label = "Waiting..."
        icon = ""

    cv2.rectangle(overlay, (0, h - 60), (w, h), color, -1)
    cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)

    text = f"{label}"
    if confidence > 0:
        text += f"  ({confidence:.0%})"

    cv2.putText(frame, text, (15, h - 22),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, WHITE, 2)

    if cooldown_remaining > 0:
        cd_text = f"Cooldown: {cooldown_remaining:.1f}s"
        cv2.putText(frame, cd_text, (w - 200, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, YELLOW, 2)

    cv2.putText(frame, "thumbs-up | q to quit", (10, 25),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, WHITE, 1)


def main():
    parser = argparse.ArgumentParser(
        description="Gesture-based approval for Claude Code")
    parser.add_argument("--confidence", type=float, default=0.7,
                        help="Min confidence to trigger (0-1, default: 0.7)")
    parser.add_argument("--cooldown", type=float, default=2.0,
                        help="Seconds between triggers (default: 2.0)")
    parser.add_argument("--camera", type=int, default=0,
                        help="Camera index (default: 0)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Show detections without sending keypresses")
    args = parser.parse_args()

    cap = cv2.VideoCapture(args.camera)
    if not cap.isOpened():
        print("Error: Could not open camera", file=sys.stderr)
        sys.exit(1)

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    latest_result = {"gesture": None, "confidence": 0.0}

    def on_result(result, image, timestamp_ms):
        if result.gestures and len(result.gestures) > 0:
            top = result.gestures[0][0]
            latest_result["gesture"] = top.category_name
            latest_result["confidence"] = top.score
        else:
            latest_result["gesture"] = None
            latest_result["confidence"] = 0.0

    options = vision.GestureRecognizerOptions(
        base_options=mp_python.BaseOptions(model_asset_path=MODEL_PATH),
        running_mode=vision.RunningMode.LIVE_STREAM,
        num_hands=1,
        min_hand_detection_confidence=0.5,
        min_tracking_confidence=0.5,
        result_callback=on_result,
    )

    recognizer = vision.GestureRecognizer.create_from_options(options)

    last_trigger_time = 0
    active_gesture = None
    active_confidence = 0.0
    gesture_display_until = 0

    print("=" * 45)
    print("  👍 Thumbs Up / Down for Claude Code 👎")
    print("=" * 45)
    print(f"  Confidence threshold: {args.confidence:.0%}")
    print(f"  Cooldown: {args.cooldown}s")
    if args.dry_run:
        print("  Mode: DRY RUN (no keypresses sent)")
    print()
    print("  Show thumbs up to approve, down to deny.")
    print("  Press 'q' in the camera window to quit.")
    print("=" * 45)

    frame_timestamp = 0

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            frame = cv2.flip(frame, 1)

            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)

            frame_timestamp += 33
            recognizer.recognize_async(mp_image, frame_timestamp)

            now = time.time()
            cooldown_remaining = max(0, args.cooldown - (now - last_trigger_time))

            gesture = latest_result["gesture"]
            confidence = latest_result["confidence"]

            if (gesture in (THUMB_UP_GESTURE, THUMB_DOWN_GESTURE)
                    and confidence >= args.confidence
                    and cooldown_remaining == 0):

                last_trigger_time = now
                active_gesture = gesture
                active_confidence = confidence
                gesture_display_until = now + 1.0

                if gesture == THUMB_UP_GESTURE:
                    action = "APPROVE (y)"
                    if not args.dry_run:
                        send_approval()
                else:
                    action = "DENY (n)"
                    if not args.dry_run:
                        send_denial()

                prefix = "[DRY RUN] " if args.dry_run else ""
                print(f"  {prefix}{action} — confidence: {confidence:.0%}")

            if now < gesture_display_until:
                draw_status(frame, active_gesture, active_confidence,
                            cooldown_remaining)
            else:
                draw_status(frame, None, 0, cooldown_remaining)

            cv2.imshow("thumbs-up", frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    except KeyboardInterrupt:
        print("\nStopped.")
    finally:
        recognizer.close()
        cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
