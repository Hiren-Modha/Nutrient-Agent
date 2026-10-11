"""
NutriBot — Add Voiceover to MP4
Pipeline:
  1. Generate per-slide narration MP3s using Google TTS (gTTS)
  2. Concatenate all narrations into one audio track (ffmpeg)
  3. Pad / trim audio to exactly 150 seconds to match video
  4. Merge audio track into the existing MP4 (ffmpeg)
  5. Output: NutriBot_IBM_Granite_Video_Voiceover.mp4
"""

import os
import sys
import subprocess
import tempfile
import shutil

import imageio_ffmpeg
from gtts import gTTS

# ── Paths ──────────────────────────────────────────────────────────────────────
BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
INPUT_MP4  = os.path.join(BASE_DIR, "NutriBot_IBM_Granite_Video.mp4")
OUTPUT_MP4 = os.path.join(BASE_DIR, "NutriBot_IBM_Granite_Video_Voiceover.mp4")
FFMPEG     = imageio_ffmpeg.get_ffmpeg_exe()

VIDEO_DURATION   = 150.0   # seconds  (20 slides × 7.5 s)
SECONDS_PER_SLIDE = 7.5
SLIDE_COUNT       = 20

# ── Per-slide narration scripts ────────────────────────────────────────────────
# Each string is read aloud for one slide (~7.5 seconds of speech).
NARRATIONS = [
    # Slide 1 — Title
    "Welcome to NutriBot — an Agentic AI application powered by IBM Granite, "
    "designed to generate personalized nutrition plans using the power of IBM watsonx dot ai.",

    # Slide 2 — Agenda
    "In this presentation, we will cover the project overview, problem statement, "
    "Agentic AI lifecycle, IBM Granite integration, the web application, sample plans, "
    "AI ethics, and the GitHub deployment.",

    # Slide 3 — Project Overview
    "NutriBot is a full-stack web application that collects user profiles, "
    "calls IBM Granite to generate evidence-based meal plans, and saves each plan "
    "as a structured Markdown file — all in under three seconds.",

    # Slide 4 — Problem Statement
    "Millions of people lack access to affordable, personalized nutrition advice. "
    "Generic plans ignore medical conditions like diabetes and hypertension. "
    "NutriBot solves this with AI-powered, medically-aware recommendations available "
    "free, twenty-four-seven.",

    # Slide 5 — Agentic AI SDLC
    "NutriBot follows all six phases of the Agentic AI software development lifecycle: "
    "Requirements, Design, Development, Guardrails, Validation, and Output with Feedback — "
    "each phase implemented directly in code, not just documented.",

    # Slide 6 — System Architecture
    "The system uses a layered architecture. The browser calls a Flask REST API, "
    "which routes requests to either the NutritionAgent or the QueryAgent. "
    "Both agents use the IBM Granite client, which connects to IBM watsonx dot ai "
    "using IAM token authentication.",

    # Slide 7 — IBM Granite Integration
    "The application integrates with ibm slash granite dash thirteen b dash instruct dash v two "
    "on the us-south watsonx dot ai endpoint. "
    "An IBM Cloud API key is exchanged for a bearer token, and the structured prompt "
    "with the HAM system context is sent to the model. "
    "When no credentials are configured, an intelligent rule-based fallback engine "
    "keeps all features fully functional.",

    # Slide 8 — Features & Guardrails
    "AI ethics are enforced through the HAM framework — Helpful, Accurate, and Mindful — "
    "combined with a five-layer safety pipeline that blocks harmful advice, "
    "detects out-of-scope topics, sanitizes outputs, and appends a mandatory medical disclaimer "
    "to every generated plan.",

    # Slide 9 — Web UI
    "The web application features four tabs: Generate Plan, Ask NutriBot, Saved Plans, and About. "
    "It is built with Flask, HTML five, CSS three, and vanilla JavaScript — "
    "no external frontend frameworks required.",

    # Slide 10 — User Profile Wizard
    "Users complete a three-step wizard providing their name, age, weight, height, city, "
    "and country in step one; diet preference, medical history, and allergies in step two; "
    "and health goals in step three. "
    "Every field is validated client-side and server-side before the AI call is made.",

    # Slide 11 — Plan Generation Output
    "Once submitted, the UI shows an animated four-step loading sequence: "
    "validating profile, running safety guardrails, generating with IBM Granite, "
    "and saving to Markdown. "
    "The finished plan appears with Copy, Download, and New Plan action buttons.",

    # Slide 12 — Chat Q&A Agent
    "The Ask NutriBot tab provides a real-time chat interface. "
    "Users can type nutrition questions or click quick-suggestion chips. "
    "The QueryAgent first checks a built-in FAQ dictionary, then falls back to IBM Granite "
    "for novel questions — with all answers safety-screened before display.",

    # Slide 13 — Sample Plan: Priya Sharma
    "Here is a real plan generated for Priya Sharma: thirty-two years old, vegetarian, "
    "with Type Two Diabetes, from Mumbai, India. "
    "Every meal is low glycaemic index and low sodium. "
    "The plan includes oatmeal with chia seeds for breakfast, brown rice with dal for lunch, "
    "and grilled tofu with steamed greens for dinner.",

    # Slide 14 — Sample Plan: Ravi Kumar
    "For Ravi Kumar, forty-five years old, non-vegetarian, with hypertension, from Bangalore — "
    "the DASH diet principles are applied: strict low-sodium meals, potassium-rich foods like "
    "spinach and sweet potato, and limited caffeine. "
    "The plan targets sodium below fifteen hundred milligrams per day.",

    # Slide 15 — Nutritional Targets
    "The daily nutritional targets are dynamically adjusted per user profile. "
    "For a diabetes plan, added sugar is capped at twenty-five grams. "
    "For hypertension, sodium is capped at fifteen hundred milligrams. "
    "IBM Granite embeds these condition-specific targets directly into each meal plan.",

    # Slide 16 — Saved Plans & .md Files
    "Every generated plan is automatically saved as a Markdown file with YAML front-matter "
    "containing the model name, timestamp, user profile metadata, and the full plan text. "
    "Users can browse and reload any saved plan from the Plans History tab.",

    # Slide 17 — GitHub Deployment
    "The complete project is deployed to GitHub at github dot com slash Hiren-Modha "
    "slash Nutrient-Agent. "
    "The repository contains twenty-one files with over twenty-nine hundred lines of code. "
    "Clone the repository, install requirements, and run flask run — or simply double-click "
    "the run underscore nutribot dot bat launcher on Windows.",

    # Slide 18 — AI Ethics & Medical Disclaimer
    "NutriBot applies IBM AI ethics principles: transparency, fairness, explainability, "
    "robustness, privacy, and accountability. "
    "A mandatory medical disclaimer is automatically appended to every plan, reminding users "
    "that the content is for informational purposes only and does not replace professional "
    "medical advice.",

    # Slide 19 — Technology Stack
    "The technology stack includes IBM Granite on watsonx dot ai for the AI layer, "
    "Python and Flask for the backend, vanilla HTML, CSS, and JavaScript for the frontend, "
    "and Git and GitHub for deployment. "
    "Software design patterns used include multi-agent architecture, strategy, facade, "
    "and decorator patterns.",

    # Slide 20 — Summary
    "In summary, NutriBot successfully delivers IBM Granite-powered personalized nutrition plans "
    "with full AI ethics compliance, a responsive web interface, automatic Markdown file export, "
    "real-time chat, and live GitHub deployment. "
    "Thank you for watching this demonstration of the NutriBot IBM Granite Nutrition Agentic AI.",
]

assert len(NARRATIONS) == SLIDE_COUNT, f"Expected {SLIDE_COUNT} narrations, got {len(NARRATIONS)}"


def run(cmd, label=""):
    """Run a subprocess command, print output, raise on error."""
    print(f"  >> {label or ' '.join(cmd[:4])}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"  STDERR: {result.stderr[-400:]}")
        raise RuntimeError(f"Command failed (rc={result.returncode}): {' '.join(cmd[:6])}")
    return result


def main():
    print("=" * 62)
    print("  NutriBot - Add Voiceover to MP4")
    print(f"  {SLIDE_COUNT} slides x {SECONDS_PER_SLIDE}s = {VIDEO_DURATION}s")
    print("=" * 62)

    if not os.path.isfile(INPUT_MP4):
        print(f"ERROR: Input video not found: {INPUT_MP4}")
        sys.exit(1)

    tmp = tempfile.mkdtemp(prefix="nutribot_vo_")
    print(f"\nWorking directory: {tmp}")

    try:
        # ── Step 1: Generate per-slide MP3s via gTTS ──────────────────────────
        print(f"\n[1/4] Generating {SLIDE_COUNT} voiceover clips with Google TTS...")
        mp3_files = []
        for idx, text in enumerate(NARRATIONS, start=1):
            mp3_path = os.path.join(tmp, f"slide_{idx:02d}.mp3")
            tts = gTTS(text=text, lang="en", slow=False)
            tts.save(mp3_path)
            sz = os.path.getsize(mp3_path)
            print(f"  Slide {idx:02d}: {sz:,} bytes — OK")
            mp3_files.append(mp3_path)

        # ── Step 2: Convert each MP3 to WAV 44100 Hz stereo ──────────────────
        print(f"\n[2/4] Converting MP3 clips to WAV (44100 Hz stereo)...")
        wav_files = []
        for mp3 in mp3_files:
            wav = mp3.replace(".mp3", ".wav")
            run([FFMPEG, "-y", "-i", mp3,
                 "-ar", "44100", "-ac", "2", wav],
                label=f"mp3-wav {os.path.basename(mp3)}")
            wav_files.append(wav)

        # ── Step 3: Build concat list & merge all WAVs ────────────────────────
        print(f"\n[3/4] Concatenating {len(wav_files)} audio clips...")
        concat_list = os.path.join(tmp, "concat.txt")
        with open(concat_list, "w") as f:
            for wav in wav_files:
                f.write(f"file '{wav}'\n")

        raw_audio = os.path.join(tmp, "raw_voiceover.wav")
        run([FFMPEG, "-y", "-f", "concat", "-safe", "0",
             "-i", concat_list,
             "-ar", "44100", "-ac", "2",
             raw_audio], label="concat WAVs")

        # Get actual audio duration
        probe = subprocess.run(
            [FFMPEG, "-i", raw_audio],
            capture_output=True, text=True
        )
        probe_out = probe.stderr
        dur_line  = [l for l in probe_out.splitlines() if "Duration" in l]
        raw_dur_str = dur_line[0].split("Duration:")[1].split(",")[0].strip() if dur_line else "unknown"
        print(f"  Raw audio duration: {raw_dur_str}")

        # ── Step 4: Pad/trim audio to exactly VIDEO_DURATION seconds ──────────
        print(f"\n     Adjusting audio to exactly {VIDEO_DURATION}s...")
        padded_audio = os.path.join(tmp, "voiceover_padded.aac")
        run([FFMPEG, "-y", "-i", raw_audio,
             "-t", str(VIDEO_DURATION),          # trim if longer
             "-af", f"apad=whole_dur={VIDEO_DURATION}",  # pad if shorter
             "-ar", "44100", "-ac", "2",
             "-c:a", "aac", "-b:a", "128k",
             padded_audio], label="pad/trim audio - AAC")

        # ── Step 5: Merge audio into the MP4 ─────────────────────────────────
        print(f"\n[4/4] Merging voiceover into video...")
        print(f"  Input : {INPUT_MP4}")
        print(f"  Output: {OUTPUT_MP4}")

        run([FFMPEG, "-y",
             "-i", INPUT_MP4,
             "-i", padded_audio,
             "-c:v", "copy",          # copy video stream (no re-encode)
             "-c:a", "aac",
             "-b:a", "128k",
             "-map", "0:v:0",         # take video from input 0
             "-map", "1:a:0",         # take audio from input 1
             "-shortest",
             OUTPUT_MP4], label="merge video+audio")

        # ── Verify output ──────────────────────────────────────────────────────
        if os.path.isfile(OUTPUT_MP4):
            sz = os.path.getsize(OUTPUT_MP4) / 1_048_576
            print(f"\n  Output size: {sz:.1f} MB")
        else:
            raise RuntimeError("Output MP4 was not created.")

    finally:
        shutil.rmtree(tmp, ignore_errors=True)
        print(f"  Temp files cleaned up.")

    print("\n" + "=" * 62)
    print("  VOICEOVER ADDED SUCCESSFULLY")
    print(f"  File    : {OUTPUT_MP4}")
    print(f"  Duration: {VIDEO_DURATION}s (150 seconds / 2 min 30 sec)")
    print(f"  Voice   : Google TTS (en, natural female voice)")
    print(f"  Slides  : {SLIDE_COUNT} narrations")
    print("=" * 62)


if __name__ == "__main__":
    main()
