"""
NutriBot — Export PPTX to 150-second MP4 video
Uses PowerPoint COM automation (Office 16).

20 slides × 7 seconds each = 140s base + 1s title + 1s summary = ~150s
PowerPoint's CreateVideo requires integer seconds.
We use 8s per slide for the default (fallback), but rely on per-slide
AdvanceTime=7.5s set on SlideShowTransition (PPT honours those).
"""

import os
import sys
import time
import comtypes.client

BASE_DIR  = os.path.dirname(os.path.abspath(__file__))
PPTX_PATH = os.path.join(BASE_DIR, "NutriBot_IBM_Granite_Presentation.pptx")
MP4_PATH  = os.path.join(BASE_DIR, "NutriBot_IBM_Granite_Video.mp4")

# 20 slides × 7.5s = 150s.  CreateVideo needs int → use 8 as fallback default
# (actual timing comes from slide AdvanceTime set below)
SECONDS_PER_SLIDE_FLOAT = 7.5
SECONDS_PER_SLIDE_INT   = 8      # integer for COM call
SLIDE_COUNT             = 20

print("=" * 60)
print("  NutriBot -- PPTX to MP4 Exporter (150 seconds)")
print(f"  {SLIDE_COUNT} slides × {SECONDS_PER_SLIDE_FLOAT}s = 150s")
print("=" * 60)

if not os.path.isfile(PPTX_PATH):
    print(f"ERROR: PPTX not found: {PPTX_PATH}")
    sys.exit(1)

# Remove stale output if present
if os.path.isfile(MP4_PATH):
    os.remove(MP4_PATH)
    print("Removed existing MP4.")

print(f"\n[1/4] Opening: {os.path.basename(PPTX_PATH)}")
ppt_app = comtypes.client.CreateObject("PowerPoint.Application")
ppt_app.Visible = 1

presentation = ppt_app.Presentations.Open(
    PPTX_PATH,
    ReadOnly=False,
    Untitled=False,
    WithWindow=True,
)
actual_count = presentation.Slides.Count
print(f"    Slides found: {actual_count}")

print(f"\n[2/4] Setting per-slide advance timing ({SECONDS_PER_SLIDE_FLOAT}s)...")
for i in range(1, actual_count + 1):
    t = presentation.Slides(i).SlideShowTransition
    t.AdvanceOnTime = True
    t.AdvanceTime   = SECONDS_PER_SLIDE_FLOAT   # float OK on the transition object
    t.EntryEffect   = 0      # ppEffectNone — no transition effect
    t.Duration      = 0.0

presentation.Save()
print("    Timings set and PPTX saved.")

# ── Export via CreateVideo ─────────────────────────────────────────────────────
# Signature: CreateVideo(FileName, UseTimingsAndNarrations, DefaultSlideDuration,
#                        VertResolution, FramesPerSecond, Quality)
# All numeric args must be integers.
print(f"\n[3/4] Exporting to MP4 (720p, 30fps)...")
print(f"    Target: {MP4_PATH}")

try:
    presentation.CreateVideo(
        MP4_PATH,               # FileName
        True,                   # UseTimingsAndNarrations — honour AdvanceTime
        SECONDS_PER_SLIDE_INT,  # DefaultSlideDuration (int) — fallback only
        720,                    # VertResolution (height px)
        30,                     # FramesPerSecond
        85,                     # Quality
    )
    print("    CreateVideo() call accepted.")
except Exception as exc:
    print(f"    CreateVideo() note: {exc}")

# ── Poll for completion ────────────────────────────────────────────────────────
print("\n    Waiting for PowerPoint render engine...")
prev_size   = -1
stable_hits = 0
wait_secs   = 0

for _ in range(300):      # max 10 minutes
    time.sleep(2)
    wait_secs += 2

    if os.path.isfile(MP4_PATH):
        sz = os.path.getsize(MP4_PATH)
        if sz > 100_000:                      # > 100 KB = real content
            if sz == prev_size:
                stable_hits += 1
                if stable_hits >= 3:          # size stable 3× in a row → done
                    print(f"\n    Render done: {wait_secs}s elapsed, {sz/1_048_576:.1f} MB")
                    break
            else:
                stable_hits = 0
            prev_size = sz
            if wait_secs % 10 == 0:
                print(f"    {wait_secs}s... {sz/1_048_576:.1f} MB")
    else:
        if wait_secs % 15 == 0:
            print(f"    {wait_secs}s — file not yet created...")

print("\n[4/4] Closing PowerPoint...")
try:
    presentation.Close()
    ppt_app.Quit()
    print("    PowerPoint closed.")
except Exception:
    pass

# ── Report ─────────────────────────────────────────────────────────────────────
if os.path.isfile(MP4_PATH) and os.path.getsize(MP4_PATH) > 100_000:
    sz_mb = os.path.getsize(MP4_PATH) / 1_048_576
    print("\n" + "=" * 60)
    print("  VIDEO EXPORT COMPLETE")
    print(f"  File     : {MP4_PATH}")
    print(f"  Size     : {sz_mb:.1f} MB")
    print(f"  Duration : ~150 seconds (20 slides x 7.5s)")
    print("=" * 60)
else:
    print("\nERROR: MP4 not created or too small.")
    sys.exit(1)
