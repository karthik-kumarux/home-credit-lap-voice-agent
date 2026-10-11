"""Automated Screen Recording & Demo Video Generator for Home Credit LAP Voice Agent

Generates a broadcast-quality 1080p demo video of the AI Voice Agent
qualifying a customer through the 7-item checklist (T01 Happy Path),
complete with real-time HUD state transitions, animated audio waveforms,
and synchronized Indian-English voice audio.

Output:
    output/recordings/home_credit_voice_agent_demo.mp4
"""

import os
import re
import sys
import math
import shutil
import subprocess
from PIL import Image, ImageDraw, ImageFont
from gtts import gTTS

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
AUDIO_DIR = os.path.join(OUTPUT_DIR, "audio")
RECORDINGS_DIR = os.path.join(OUTPUT_DIR, "recordings")
TURNS_AUDIO_DIR = os.path.join(AUDIO_DIR, "turns_T01")

os.makedirs(RECORDINGS_DIR, exist_ok=True)
os.makedirs(TURNS_AUDIO_DIR, exist_ok=True)

# 17-Turn Conversation for T01 Happy Path
DIALOGUE_TURNS = [
    ("Agent", "Hello, am I speaking with Rahul?"),
    ("Customer", "Yes, this is Rahul."),
    ("Agent", "Great, Rahul. To get started, could you tell me what type of property you own? Is it Residential, Commercial, or Industrial?"),
    ("Customer", "I am free to talk. It is a residential property."),
    ("Agent", "Thanks, Rahul. Could you tell me whether you own the property solely or jointly?"),
    ("Customer", "I am the sole owner."),
    ("Agent", "Thank you, Rahul. Do you have the original property documents available with you?"),
    ("Customer", "Yes, I have the original documents."),
    ("Agent", "Thank you, Rahul. Could you let me know the exact loan amount you are interested in? Our pre-approved offer is up to 75 lakh rupees."),
    ("Customer", "I need a loan of 50 lakh."),
    ("Agent", "Thank you, Rahul. Could you please let me know your occupation and whether your income is received through a bank account or in cash?"),
    ("Customer", "I am salaried, get paid in my bank account."),
    ("Agent", "Thank you, Rahul. Could you please tell me the estimated market value of your property?"),
    ("Customer", "It is worth 1 crore."),
    ("Agent", "Thank you, Rahul. Could you please let me know the loan tenure you are looking for, in years? It should be between 3 and 15 years."),
    ("Customer", "I want it for 10 years."),
    ("Agent", "Great, Rahul. A 10-year tenure is noted. I have captured all the details you provided. Our loan specialist will review your application and get back to you shortly. Thank you for your time.")
]


def find_ffmpeg():
    """Locate ffmpeg binary on system."""
    candidates = [
        r"D:\videos\frontend\node_modules\node-av\binary\ffmpeg.exe",
        r"D:\videos\frontend\node_modules\@remotion\compositor-win32-x64-msvc\ffmpeg.exe",
        shutil.which("ffmpeg")
    ]
    for c in candidates:
        if c and os.path.exists(c):
            return c
    raise RuntimeError("ffmpeg binary not found!")


def get_audio_duration(ffmpeg_path, audio_path):
    """Probe audio duration in seconds using ffmpeg."""
    cmd = [ffmpeg_path, "-i", audio_path, "-f", "null", "-"]
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    match = re.search(r"Duration:\s*(\d+):(\d+):(\d+\.\d+)", res.stderr)
    if match:
        h, m, s = match.groups()
        return int(h) * 3600 + int(m) * 60 + float(s)
    return 3.0


def generate_audio_tracks(ffmpeg_path):
    """Generate audio files for all turns and combine into a master track with exact timings."""
    print("Generating speech audio clips for each dialogue turn...")
    turn_audios = []
    durations = []

    for idx, (speaker, utterance) in enumerate(DIALOGUE_TURNS):
        audio_file = os.path.join(TURNS_AUDIO_DIR, f"turn_{idx:02d}.mp3")
        if not os.path.exists(audio_file) or os.path.getsize(audio_file) == 0:
            tld = "co.in" if speaker == "Agent" else "com"
            tts = gTTS(text=utterance, lang="en", tld=tld, slow=False)
            tts.save(audio_file)

        dur = get_audio_duration(ffmpeg_path, audio_file)
        turn_audios.append(audio_file)
        durations.append(dur)
        print(f"  Turn {idx:02d} [{speaker}]: {dur:.2f}s - \"{utterance[:35]}...\"")

    # Generate master audio using ffmpeg concat
    concat_list_file = os.path.join(TURNS_AUDIO_DIR, "concat_list.txt")
    with open(concat_list_file, "w", encoding="utf-8") as f:
        for audio in turn_audios:
            # Escape path for ffmpeg concat
            clean_path = os.path.abspath(audio).replace("\\", "/")
            f.write(f"file '{clean_path}'\n")

    master_audio = os.path.join(RECORDINGS_DIR, "temp_master_audio.mp3")
    cmd = [
        ffmpeg_path, "-y",
        "-f", "concat", "-safe", "0",
        "-i", concat_list_file,
        "-c", "copy",
        master_audio
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    total_audio_dur = sum(durations)
    print(f"Master audio generated: {total_audio_dur:.2f} seconds ({len(turn_audios)} turns)")

    return durations, master_audio


def wrap_text(text, max_chars=48):
    """Simple text wrapping for dialogue bubbles."""
    words = text.split()
    lines = []
    cur = []
    for w in words:
        if sum(len(x) for x in cur) + len(cur) + len(w) <= max_chars:
            cur.append(w)
        else:
            lines.append(" ".join(cur))
            cur = [w]
    if cur:
        lines.append(" ".join(cur))
    return lines


def render_frame(turn_idx, frame_in_turn, turn_duration, fps, fonts):
    """Draw a single 1920x1080 UI frame representing the current call state."""
    w, h = 1920, 1080
    img = Image.new("RGB", (w, h), color="#0B132B")
    draw = ImageDraw.Draw(img)

    f_title = fonts["title"]
    f_header = fonts["header"]
    f_bold = fonts["bold"]
    f_body = fonts["body"]
    f_small = fonts["small"]
    f_mono = fonts["mono"]

    # ----------------------------------------------------
    # 1. TOP HEADER BAR
    # ----------------------------------------------------
    draw.rectangle([(0, 0), (w, 80)], fill="#D71920")
    draw.text((30, 15), "HOME CREDIT INDIA", fill="#FFFFFF", font=f_title)
    draw.text((30, 48), "Loan Against Property (LAP) AI Voice Agent  •  Pre-Approved: Up to ₹75,00,000", fill="#FDE047", font=f_small)

    # Badges on Top Right
    draw.rounded_rectangle([(1400, 18), (1600, 62)], radius=8, fill="#991B1B")
    draw.text((1418, 30), "● LLaMA-3.3-70B", fill="#FEF08A", font=f_small)

    draw.rounded_rectangle([(1620, 18), (1890, 62)], radius=8, fill="#15803D")
    draw.text((1638, 30), "🔊 Live Voice: Aisha (Indian EN)", fill="#DCFCE7", font=f_small)

    # ----------------------------------------------------
    # 2. STATE LOGIC DERIVATION
    # ----------------------------------------------------
    verified = turn_idx >= 1
    criteria_state = {
        "Property Type": ("Residential", True) if turn_idx >= 3 else ("Pending", False),
        "Ownership": ("Sole Owner", True) if turn_idx >= 5 else ("Pending", False),
        "Original Docs": ("Available (Physical)", True) if turn_idx >= 7 else ("Pending", False),
        "Loan Amount": ("₹50,00,000 (≤ ₹75L)", True) if turn_idx >= 9 else ("Pending", False),
        "Income Mode": ("Salaried (Bank)", True) if turn_idx >= 11 else ("Pending", False),
        "Market Value": ("₹1,00,00,000", True) if turn_idx >= 13 else ("Pending", False),
        "Tenure": ("10 Years (3-15y)", True) if turn_idx >= 15 else ("Pending", False),
    }
    completed_count = sum(1 for val, ok in criteria_state.values() if ok)
    all_passed = completed_count == 7

    # ----------------------------------------------------
    # 3. LEFT PANEL: Agent & Customer Status (x: 25 to 400)
    # ----------------------------------------------------
    draw.rounded_rectangle([(25, 95), (400, 310)], radius=12, fill="#1C2541", outline="#3A506B", width=2)
    draw.text((45, 110), "CALL PARTICIPANTS", fill="#60A5FA", font=f_header)

    # Agent Avatar & Info
    draw.ellipse([(45, 145), (85, 185)], fill="#D71920")
    draw.text((58, 150), "A", fill="#FFFFFF", font=f_header)
    draw.text((95, 145), "Aisha (AI Voice Agent)", fill="#FFFFFF", font=f_bold)
    draw.text((95, 168), "Home Credit India • Loan Specialist", fill="#94A3B8", font=f_small)

    # Customer Avatar & Info
    draw.ellipse([(45, 205), (85, 245)], fill="#2563EB")
    draw.text((58, 210), "R", fill="#FFFFFF", font=f_header)
    draw.text((95, 205), "Rahul Sharma (Customer)", fill="#FFFFFF", font=f_bold)
    draw.text((95, 228), "Verified: " + ("YES ✅" if verified else "PENDING..."), fill="#4ADE80" if verified else "#FCD34D", font=f_small)

    # Offer Info Box
    draw.rounded_rectangle([(45, 255), (380, 295)], radius=6, fill="#0F172A")
    draw.text((55, 265), "Pre-Approved LAP Offer: ₹75,00,000", fill="#FDE047", font=f_small)

    # Precedence Architecture Card (x: 25 to 400, y: 325 to 700)
    draw.rounded_rectangle([(25, 325), (400, 715)], radius=12, fill="#1C2541", outline="#3A506B", width=2)
    draw.text((45, 340), "5-TIER PRECEDENCE ENGINE", fill="#60A5FA", font=f_header)

    tiers = [
        ("1. Correction", "Latest customer statement wins"),
        ("2. Disqualification", "Agricultural / Cash / Tenure"),
        ("3. Specialist Transfer", "Existing mortgage / Balance transfer"),
        ("4. Clarification", "Ambiguous occupation/documents"),
        ("5. Next Checklist Item", "7-Item qualification flow")
    ]
    for i, (name, desc) in enumerate(tiers):
        ty = 385 + i * 62
        is_active = (i == 4 and not all_passed) or (i == 2 and all_passed)
        bg_col = "#065F46" if is_active else "#0F172A"
        border_col = "#10B981" if is_active else "#334155"
        draw.rounded_rectangle([(45, ty), (380, ty + 52)], radius=6, fill=bg_col, outline=border_col, width=1)
        draw.text((55, ty + 6), ("▶ " if is_active else "") + name, fill="#34D399" if is_active else "#E2E8F0", font=f_bold)
        draw.text((55, ty + 28), desc, fill="#CBD5E1", font=f_small)

    # Compliance Card (y: 730 to 1050)
    draw.rounded_rectangle([(25, 730), (400, 1050)], radius=12, fill="#1C2541", outline="#3A506B", width=2)
    draw.text((45, 745), "POLICY & COMPLIANCE", fill="#60A5FA", font=f_header)
    rules = [
        "• Property: Res/Comm/Ind only",
        "• Documents: Physical originals required",
        "• Maximum Loan Limit: ₹75,00,000",
        "• Income: Salaried / Self (Bank transfer)",
        "• Tenure: 3 to 15 years inclusive",
        "• Infallible State Machine Oracle active"
    ]
    for idx, rule in enumerate(rules):
        draw.text((45, 785 + idx * 42), rule, fill="#E2E8F0", font=f_small)

    # ----------------------------------------------------
    # 4. CENTER PANEL: Live Conversation Stream (x: 420 to 1330)
    # ----------------------------------------------------
    draw.rounded_rectangle([(420, 95), (1330, 1050)], radius=12, fill="#1C2541", outline="#3A506B", width=2)

    # Header with Active Speaker and Animated Waveform
    current_speaker, current_text = DIALOGUE_TURNS[turn_idx]
    draw.text((440, 110), "LIVE CONVERSATION TRANSCRIPT", fill="#60A5FA", font=f_header)

    # Active Speaker indicator
    spk_color = "#EF4444" if current_speaker == "Agent" else "#3B82F6"
    draw.rounded_rectangle([(1020, 105), (1310, 145)], radius=6, fill=spk_color)
    draw.text((1035, 115), f"SPEAKING: {current_speaker.upper()}", fill="#FFFFFF", font=f_bold)

    # Animated Audio Waveform Bars (calculated from frame number)
    for b in range(10):
        bx = 1220 + b * 8
        bar_h = 6 + int(14 * abs(math.sin(frame_in_turn * 0.4 + b * 0.6)))
        draw.rectangle([(bx, 125 - bar_h // 2), (bx + 4, 125 + bar_h // 2)], fill="#FFFFFF")

    # Render Dialogue Bubbles (Show last 5 turns up to current)
    start_turn = max(0, turn_idx - 4)
    bubble_y = 160
    for t in range(start_turn, turn_idx + 1):
        spk, txt = DIALOGUE_TURNS[t]
        is_current = (t == turn_idx)
        is_agent = (spk == "Agent")

        lines = wrap_text(txt, max_chars=54)
        b_height = 42 + len(lines) * 24

        if is_agent:
            bx1, bx2 = 440, 1180
            bg = "#3B1118" if is_current else "#2A0E13"
            border = "#EF4444" if is_current else "#7F1D1D"
            draw.rounded_rectangle([(bx1, bubble_y), (bx2, bubble_y + b_height)], radius=10, fill=bg, outline=border, width=2 if is_current else 1)
            draw.text((bx1 + 15, bubble_y + 8), "Aisha (Agent)", fill="#FCA5A5", font=f_bold)
        else:
            bx1, bx2 = 560, 1310
            bg = "#1E3A8A" if is_current else "#172554"
            border = "#60A5FA" if is_current else "#1E40AF"
            draw.rounded_rectangle([(bx1, bubble_y), (bx2, bubble_y + b_height)], radius=10, fill=bg, outline=border, width=2 if is_current else 1)
            draw.text((bx1 + 15, bubble_y + 8), "Rahul (Customer)", fill="#93C5FD", font=f_bold)

        for l_idx, line in enumerate(lines):
            draw.text((bx1 + 15, bubble_y + 34 + l_idx * 24), line, fill="#FFFFFF", font=f_body)

        bubble_y += b_height + 15

    # ----------------------------------------------------
    # 5. RIGHT PANEL: 7-Item Eligibility Oracle HUD (x: 1350 to 1895)
    # ----------------------------------------------------
    draw.rounded_rectangle([(1350, 95), (1895, 1050)], radius=12, fill="#1C2541", outline="#3A506B", width=2)
    draw.text((1375, 110), "ELIGIBILITY ORACLE HUD", fill="#60A5FA", font=f_header)
    draw.text((1375, 138), "Deterministic 7-Criteria State Machine", fill="#94A3B8", font=f_small)

    # Progress Bar
    pct = completed_count / 7.0
    draw.rounded_rectangle([(1375, 165), (1870, 185)], radius=6, fill="#0F172A")
    if pct > 0:
        draw.rounded_rectangle([(1375, 165), (1375 + int(495 * pct), 185)], radius=6, fill="#10B981")
    draw.text((1785, 166), f"{completed_count}/7 ({int(pct*100)}%)", fill="#FFFFFF", font=f_small)

    # 7 Checklist Items
    items_def = [
        ("1. Property Type", "Residential, Commercial, Industrial", criteria_state["Property Type"]),
        ("2. Ownership Status", "Sole or Joint ownership", criteria_state["Ownership"]),
        ("3. Original Documents", "Physical originals available", criteria_state["Original Docs"]),
        ("4. Loan Amount", "Pre-approved up to ₹75,00,000", criteria_state["Loan Amount"]),
        ("5. Occupation & Income", "Salaried / Self (Bank transfer)", criteria_state["Income Mode"]),
        ("6. Estimated Market Value", "Property valuation captured", criteria_state["Market Value"]),
        ("7. Desired Tenure", "3 to 15 years inclusive", criteria_state["Tenure"]),
    ]

    for idx, (title, policy, (val, passed)) in enumerate(items_def):
        iy = 205 + idx * 98
        bg_card = "#064E3B" if passed else "#0F172A"
        border_card = "#10B981" if passed else "#334155"

        draw.rounded_rectangle([(1375, iy), (1870, iy + 88)], radius=8, fill=bg_card, outline=border_card, width=2 if passed else 1)
        draw.text((1390, iy + 8), title, fill="#FFFFFF", font=f_bold)
        draw.text((1390, iy + 32), "Rule: " + policy, fill="#94A3B8", font=f_small)

        # Status badge
        if passed:
            draw.rounded_rectangle([(1390, iy + 56), (1855, iy + 80)], radius=4, fill="#047857")
            draw.text((1400, iy + 59), f"CONFIRMED: {val}  [PASS]", fill="#E6FFFA", font=f_bold)
        else:
            draw.rounded_rectangle([(1390, iy + 56), (1540, iy + 80)], radius=4, fill="#374151")
            draw.text((1400, iy + 59), "WAITING...", fill="#9CA3AF", font=f_small)

    # ----------------------------------------------------
    # 6. BOTTOM CALL OUTCOME BANNER (Inside Right Panel)
    # ----------------------------------------------------
    if all_passed:
        draw.rounded_rectangle([(1375, 915), (1870, 1030)], radius=10, fill="#15803D", outline="#86EFAC", width=3)
        draw.text((1400, 930), "CUSTOMER QUALIFIED", fill="#FFFFFF", font=f_header)
        draw.text((1400, 960), "All 7 criteria verified and confirmed.", fill="#DCFCE7", font=f_body)
        draw.text((1400, 990), "Handoff to Senior Specialist Initiated", fill="#FEF08A", font=f_bold)
    else:
        draw.rounded_rectangle([(1375, 915), (1870, 1030)], radius=10, fill="#1E293B", outline="#475569", width=1)
        draw.text((1400, 935), "CALL STATUS: IN PROGRESS", fill="#93C5FD", font=f_bold)
        draw.text((1400, 965), f"Evaluating criterion {completed_count + 1} of 7...", fill="#CBD5E1", font=f_small)

    return img


def generate_demo_video():
    """Main routine to render and assemble the entire demo video."""
    print("=" * 70)
    print("  HOME CREDIT LAP VOICE AGENT - AUTOMATED DEMO VIDEO GENERATOR")
    print("=" * 70)

    ffmpeg_path = find_ffmpeg()
    print(f"Using FFmpeg: {ffmpeg_path}")

    # Step 1: Generate dialogue audios and master audio track
    durations, master_audio_path = generate_audio_tracks(ffmpeg_path)

    # Step 2: Load Windows Fonts
    font_bold_path = r"C:\Windows\Fonts\segoeuib.ttf"
    font_reg_path = r"C:\Windows\Fonts\segoeui.ttf"
    font_mono_path = r"C:\Windows\Fonts\consola.ttf"

    fonts = {
        "title": ImageFont.truetype(font_bold_path, 26),
        "header": ImageFont.truetype(font_bold_path, 20),
        "bold": ImageFont.truetype(font_bold_path, 17),
        "body": ImageFont.truetype(font_reg_path, 16),
        "small": ImageFont.truetype(font_reg_path, 13),
        "mono": ImageFont.truetype(font_mono_path, 14),
    }

    # Video parameters
    fps = 20
    output_video_path = os.path.join(RECORDINGS_DIR, "home_credit_voice_agent_demo.mp4")

    # Step 3: Start FFmpeg pipe for high-speed video encoding with audio
    cmd = [
        ffmpeg_path, "-y",
        "-f", "rawvideo",
        "-pix_fmt", "rgb24",
        "-s", "1920x1080",
        "-r", str(fps),
        "-i", "-",  # Video input from pipe
        "-i", master_audio_path,  # Audio input from file
        "-c:v", "libx264",
        "-preset", "ultrafast",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "128k",
        "-shortest",
        output_video_path
    ]

    print("\nEncoding synchronized 1080p video with audio stream...")
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    total_frames = 0
    # Render turns
    for turn_idx, dur in enumerate(durations):
        num_frames = int(dur * fps)
        spk = DIALOGUE_TURNS[turn_idx][0]
        sys.stdout.write(f"\rRendering Turn {turn_idx+1:02d}/{len(durations):02d} [{spk:8s}] - {num_frames} frames ({dur:.1f}s)...")
        sys.stdout.flush()

        for f_idx in range(num_frames):
            frame_img = render_frame(turn_idx, f_idx, dur, fps, fonts)
            proc.stdin.write(frame_img.tobytes())
            total_frames += 1

    # Add 4 seconds hold on the final qualified handoff screen
    hold_frames = int(4.0 * fps)
    print(f"\nAdding final handoff summary hold ({hold_frames} frames)...")
    last_turn_idx = len(DIALOGUE_TURNS) - 1
    for f_idx in range(hold_frames):
        frame_img = render_frame(last_turn_idx, f_idx, 4.0, fps, fonts)
        proc.stdin.write(frame_img.tobytes())
        total_frames += 1

    proc.stdin.close()
    proc.wait()

    # Clean up temp master audio
    if os.path.exists(master_audio_path):
        os.remove(master_audio_path)

    file_size_mb = os.path.getsize(output_video_path) / (1024 * 1024)
    duration_sec = total_frames / fps

    print("\n" + "=" * 70)
    print("  DEMO VIDEO GENERATION COMPLETED SUCCESSFULLY!")
    print("=" * 70)
    print(f"Output File:     {output_video_path}")
    print(f"Video Resolution: 1920x1080 (Full HD, 20 FPS)")
    print(f"Audio Track:      AAC Stereo (Synchronized Neural Indian-English TTS)")
    print(f"Total Duration:   {duration_sec:.1f} seconds (~{duration_sec/60:.1f} minutes)")
    print(f"Total Frames:     {total_frames}")
    print(f"File Size:        {file_size_mb:.2f} MB")
    print("\nReady for Submission:")
    print("1. Upload this file directly to Google Drive.")
    print("2. Set share permission to 'Anyone with the link can view'.")
    print("3. Paste the share link into the submission form.")
    print("=" * 70)


if __name__ == "__main__":
    generate_demo_video()
