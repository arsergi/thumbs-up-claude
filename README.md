How to use it

  1. Open a separate terminal and run:
  ./run.sh
  2. Use Claude Code in your main terminal (keep it focused)
  3. When a permission prompt appears, show a thumbs up (sends y + Enter) or thumbs down (sends n + Enter) to your
  camera
  4. Press q in the camera window to quit

  Options

  ┌──────────────┬─────────┬───────────────────────────────────────────────────────────────┐
  │     Flag     │ Default │                         What it does                          │
  ├──────────────┼─────────┼───────────────────────────────────────────────────────────────┤
  │ --dry-run    │ off     │ Show detections without sending keypresses (good for testing) │
  ├──────────────┼─────────┼───────────────────────────────────────────────────────────────┤
  │ --confidence │ 0.7     │ Min confidence threshold (0-1)                                │
  ├──────────────┼─────────┼───────────────────────────────────────────────────────────────┤
  │ --cooldown   │ 2.0     │ Seconds between triggers to avoid accidental repeats          │
  ├──────────────┼─────────┼───────────────────────────────────────────────────────────────┤
  │ --camera     │ 0       │ Camera index if you have multiple                             │
  └──────────────┴─────────┴───────────────────────────────────────────────────────────────┘
