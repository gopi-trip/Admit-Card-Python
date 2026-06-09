import csv
import os
import sys
import hashlib
import argparse
import traceback
import io
from pathlib import Path
from datetime import datetime

import qrcode
import requests
from PIL import Image, ImageDraw, ImageFont, ImageFilter

CARD_WIDTH  = 1200
FOOTER_FIXED_H = 120   

COLOR_NAVY       = (13, 47, 95)     
COLOR_GOLD       = (192, 155, 73)    
COLOR_LIGHT_BLUE = (235, 242, 252)  
COLOR_TABLE_EVEN = (248, 250, 255)  
COLOR_TABLE_ODD  = (255, 255, 255) 
COLOR_TABLE_HEAD = (13, 47, 95)    
COLOR_BORDER     = (180, 195, 220)   
COLOR_TEXT_DARK  = (20, 30, 50)    
COLOR_TEXT_MID   = (80, 95, 115)   
COLOR_WHITE      = (255, 255, 255)
COLOR_VALID_BG   = (220, 240, 220)  
COLOR_VALID_TEXT = (30, 110, 50)
COLOR_WARN       = (200, 60, 60)     

FONT_DIR = Path("/usr/share/fonts/truetype")
FONT_SANS_REG    = str(FONT_DIR / "google-fonts/Poppins-Regular.ttf")
FONT_SANS_MED    = str(FONT_DIR / "google-fonts/Poppins-Medium.ttf")
FONT_SANS_BOLD   = str(FONT_DIR / "google-fonts/Poppins-Bold.ttf")
FONT_SANS_LIGHT  = str(FONT_DIR / "google-fonts/Poppins-Light.ttf")
FONT_SERIF_REG   = str(FONT_DIR / "dejavu/DejaVuSerif.ttf")
FONT_SERIF_BOLD  = str(FONT_DIR / "dejavu/DejaVuSerif-Bold.ttf")
FONT_MONO        = str(FONT_DIR / "dejavu/DejaVuSansMono.ttf")

_font_cache: dict = {}

def font(path: str, size: int) -> ImageFont.FreeTypeFont:
    key = (path, size)
    if key not in _font_cache:
        try:
            _font_cache[key] = ImageFont.truetype(path, size)
        except (IOError, OSError):
            _font_cache[key] = ImageFont.load_default()
    return _font_cache[key]

def draw_rounded_rect(draw: ImageDraw.Draw, xy, radius=12, fill=None, outline=None, width=1):
    """Draw a rectangle with rounded corners."""
    x0, y0, x1, y1 = xy
    r = radius
    draw.rounded_rectangle([x0, y0, x1, y1], radius=r, fill=fill, outline=outline, width=width)


def text_bbox_width(draw: ImageDraw.Draw, text: str, fnt) -> int:
    bb = draw.textbbox((0, 0), text, font=fnt)
    return bb[2] - bb[0]


def draw_text_centered(draw: ImageDraw.Draw, cx: int, y: int, text: str, fnt, fill):
    w = text_bbox_width(draw, text, fnt)
    draw.text((cx - w // 2, y), text, font=fnt, fill=fill)


def draw_label_value(draw: ImageDraw.Draw, x: int, y: int,
                     label: str, value: str,
                     label_fnt, value_fnt,
                     label_color, value_color) -> int:
    """Draw a label: value pair, returns ending x position."""
    draw.text((x, y), label, font=label_fnt, fill=label_color)
    lw = text_bbox_width(draw, label, label_fnt)
    draw.text((x + lw + 4, y), value, font=value_fnt, fill=value_color)
    return x + lw + 4 + text_bbox_width(draw, value, value_fnt)

def load_photo(url: str, size=(160, 195)) -> Image.Image:
    """
    Load a photo from URL (Google Drive or direct).
    Returns a resized, border-framed image.
    Falls back to a placeholder if download fails.
    """
    img = None

    if url and url.strip():
        try:
            
            if "drive.google.com" in url:
                file_id = None
                for part in url.split("/"):
                    if len(part) == 33 or (part.startswith("1") and len(part) > 25):
                        file_id = part
                        break
                if "id=" in url:
                    file_id = url.split("id=")[-1].split("&")[0]
                if file_id:
                    url = f"https://drive.google.com/uc?export=download&id={file_id}"

            headers = {"User-Agent": "Mozilla/5.0"}
            resp = requests.get(url, timeout=10, headers=headers)
            resp.raise_for_status()
            img = Image.open(io.BytesIO(resp.content)).convert("RGBA")
        except Exception as e:
            print(f"    [!] Photo download failed: {e}")

    if img is None:
       
        img = Image.new("RGBA", (200, 250), (210, 220, 235, 255))
        draw = ImageDraw.Draw(img)
        # Head circle
        draw.ellipse([60, 20, 140, 100], fill=(150, 165, 185, 255))
        # Body
        draw.ellipse([30, 95, 170, 220], fill=(150, 165, 185, 255))
        draw.text((15, 225), "No Photo", font=ImageFont.load_default(), fill=(120, 130, 150))

   
    img = img.convert("RGB")
    target_w, target_h = size
    orig_w, orig_h = img.size
    scale = max(target_w / orig_w, target_h / orig_h)
    new_w = int(orig_w * scale)
    new_h = int(orig_h * scale)
    img = img.resize((new_w, new_h), Image.LANCZOS)
    left = (new_w - target_w) // 2
    top  = (new_h - target_h) // 2
    img = img.crop((left, top, left + target_w, top + target_h))

   
    framed = Image.new("RGB", (target_w + 4, target_h + 4), COLOR_GOLD)
    framed.paste(img, (2, 2))
    return framed

def make_qr(data: str, size=110) -> Image.Image:
    """Generate a QR code image for verification data."""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=4,
        border=2,
    )
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color=COLOR_NAVY, back_color="white").convert("RGB")
    return img.resize((size, size), Image.LANCZOS)

def draw_admit_card(student: dict) -> Image.Image:

    HEADER_H    = 110
    INFO_H      = 195
    INFO_GAP    = 14
    TH_H        = 44
    ROW_H       = 42
    FOOTER_H    = 120
    PAD         = 14

    n_subjects  = len(student["subjects"])
    TABLE_H     = TH_H + ROW_H * max(n_subjects, 1)
    CARD_HEIGHT = HEADER_H + PAD + INFO_H + PAD + TABLE_H + PAD + FOOTER_H + PAD

    canvas = Image.new("RGB", (CARD_WIDTH, CARD_HEIGHT), COLOR_WHITE)
    draw   = ImageDraw.Draw(canvas)

    subjects      = student["subjects"]
    subject_codes = student["subject_codes"]
    dates         = student["dates"]
    draw.rectangle([(0, 0), (CARD_WIDTH, HEADER_H)], fill=COLOR_NAVY)

    draw.rectangle([(0, HEADER_H - 5), (CARD_WIDTH, HEADER_H)], fill=COLOR_GOLD)

    univ_fnt = font(FONT_SERIF_BOLD, 32)
    draw_text_centered(draw, CARD_WIDTH // 2, 14, "ABC University of Technology",
                       univ_fnt, COLOR_WHITE)

    draw.line([(CARD_WIDTH // 2 - 200, 55), (CARD_WIDTH // 2 + 200, 55)],
              fill=COLOR_GOLD, width=1)

    admit_fnt = font(FONT_SANS_BOLD, 20)
    draw_text_centered(draw, CARD_WIDTH // 2, 62, "ADMIT CARD", admit_fnt, COLOR_GOLD)

    session_fnt  = font(FONT_SANS_REG, 13)
    session_text = f"Session: {student.get('session', '2024-25')}"
    draw.text((CARD_WIDTH - 250, 18), session_text, font=session_fnt, fill=(180, 200, 235))
    exam_text = f"End Semester Examination"
    draw.text((CARD_WIDTH - 250, 40), exam_text, font=session_fnt, fill=(180, 200, 235))
    sem_text = f"Semester {student.get('semester', '')}"
    draw.text((CARD_WIDTH - 250, 62), sem_text, font=session_fnt, fill=COLOR_GOLD)

    INFO_Y      = HEADER_H + 14
    INFO_H      = 195
    INFO_X      = 16
    INFO_W      = CARD_WIDTH - 32
    PHOTO_W     = 166
    PHOTO_H     = 195

    draw_rounded_rect(draw, (INFO_X, INFO_Y, INFO_X + INFO_W, INFO_Y + INFO_H),
                      radius=10, fill=COLOR_LIGHT_BLUE, outline=COLOR_BORDER, width=1)

    photo_x = CARD_WIDTH - INFO_X - PHOTO_W - 14
    photo_y = INFO_Y + 10
    photo   = load_photo(student.get("photo_url", ""), size=(PHOTO_W - 4, PHOTO_H - 20))
    canvas.paste(photo, (photo_x, photo_y))

    lbl_fnt  = font(FONT_SANS_MED,  15)
    val_fnt  = font(FONT_SANS_BOLD, 16)
    meta_fnt = font(FONT_SANS_REG,  14)
    lbl_col  = COLOR_TEXT_MID
    val_col  = COLOR_TEXT_DARK

    LEFT_X = INFO_X + 22
    RIGHT_X = INFO_X + INFO_W // 2 + 10

    fields_left = [
        ("Name",          student.get("name", "—")),
        ("Enrollment No", student.get("enrollment", "—")),
        ("Branch",        student.get("branch", "—")),
        ("Course",        student.get("course", "—")),
    ]
    fields_right = [
        ("Year",      student.get("year", "—")),
        ("Semester",  student.get("semester", "—") + " Semester"),
        ("Exam Time", student.get("time", "—")),
    ]

    y = INFO_Y + 22
    for label, value in fields_left:
        draw.text((LEFT_X, y), label + ":", font=lbl_fnt, fill=lbl_col)
        draw.text((LEFT_X, y + 20), value, font=val_fnt, fill=val_col)
        y += 46

    y = INFO_Y + 22
    for label, value in fields_right:
        draw.text((RIGHT_X, y), label + ":", font=lbl_fnt, fill=lbl_col)
        draw.text((RIGHT_X, y + 20), value, font=val_fnt, fill=val_col)
        y += 46

    TABLE_Y    = INFO_Y + INFO_H + 14
    TABLE_X    = INFO_X
    TABLE_W    = INFO_W
    ROW_H      = 42
    TH_H       = 44

    col_widths = [
        int(TABLE_W * 0.38),   
        int(TABLE_W * 0.15),  
        int(TABLE_W * 0.23), 
        int(TABLE_W * 0.24), 
    ]

    col_widths[-1] = TABLE_W - sum(col_widths[:-1])

    col_labels  = ["Subject", "Code", "Exam Date", "Exam Time"]
    col_aligns  = ["left", "center", "center", "center"]

    TH_Y = TABLE_Y
    draw.rectangle([(TABLE_X, TH_Y), (TABLE_X + TABLE_W, TH_Y + TH_H)],
                   fill=COLOR_TABLE_HEAD)

    draw.line([(TABLE_X, TH_Y + TH_H - 2), (TABLE_X + TABLE_W, TH_Y + TH_H - 2)],
              fill=COLOR_GOLD, width=2)

    th_fnt = font(FONT_SANS_BOLD, 16)
    cx = TABLE_X
    for i, (label, w) in enumerate(zip(col_labels, col_widths)):
        col_cx = cx + w // 2
        draw_text_centered(draw, col_cx, TH_Y + (TH_H - 22) // 2, label, th_fnt, COLOR_WHITE)
        if i < len(col_labels) - 1:
            draw.line([(cx + w, TH_Y + 6), (cx + w, TH_Y + TH_H - 6)],
                      fill=(100, 130, 170), width=1)
        cx += w

    cell_fnt   = font(FONT_SANS_REG,  15)
    cell_bold  = font(FONT_SANS_MED,  15)
    mono_fnt   = font(FONT_MONO,      15)

    row_y = TH_Y + TH_H
    for idx in range(n_subjects):
        row_bg = COLOR_TABLE_EVEN if idx % 2 == 0 else COLOR_TABLE_ODD
        row_x  = TABLE_X

        draw.rectangle([(row_x, row_y), (row_x + TABLE_W, row_y + ROW_H)],
                       fill=row_bg)

        draw.line([(row_x, row_y + ROW_H - 1), (row_x + TABLE_W, row_y + ROW_H - 1)],
                  fill=COLOR_BORDER, width=1)

        row_data = [
            subjects[idx]        if idx < len(subjects)      else "—",
            subject_codes[idx]   if idx < len(subject_codes) else "—",
            dates[idx]           if idx < len(dates)          else "—",
            student.get("time", "—"),
        ]
        row_fonts  = [cell_bold, mono_fnt, cell_fnt, cell_fnt]

        cx = row_x
        for col_i, (val, w, align, rfnt) in enumerate(zip(row_data, col_widths, col_aligns, row_fonts)):
            text_y = row_y + (ROW_H - 20) // 2
            padding = 14
            if align == "center":
                draw_text_centered(draw, cx + w // 2, text_y, val, rfnt, COLOR_TEXT_DARK)
            else:
                draw.text((cx + padding, text_y), val, font=rfnt, fill=COLOR_TEXT_DARK)

            if col_i < len(col_widths) - 1:
                draw.line([(cx + w, row_y + 6), (cx + w, row_y + ROW_H - 6)],
                          fill=COLOR_BORDER, width=1)
            cx += w

        row_y += ROW_H

    TABLE_BOTTOM = row_y
    draw.rectangle([(TABLE_X, TABLE_Y), (TABLE_X + TABLE_W, TABLE_BOTTOM)],
                   outline=COLOR_BORDER, width=1)

    FOOTER_Y = TABLE_BOTTOM + 14
    FOOTER_H = CARD_HEIGHT - FOOTER_Y - 10

    stamp_x = INFO_X + 20
    stamp_y = FOOTER_Y + 8
    stamp_w, stamp_h = 220, 46
    draw_rounded_rect(draw, (stamp_x, stamp_y, stamp_x + stamp_w, stamp_y + stamp_h),
                      radius=8, fill=COLOR_VALID_BG, outline=COLOR_VALID_TEXT, width=1)
    draw.text((stamp_x + 14, stamp_y + 6),  "[ VALID ]  ADMIT CARD",
              font=font(FONT_SANS_BOLD, 13), fill=COLOR_VALID_TEXT)
    draw.text((stamp_x + 14, stamp_y + 26), f"Generated: {datetime.now().strftime('%d %b %Y')}",
              font=font(FONT_SANS_REG, 12),  fill=COLOR_VALID_TEXT)

    sig_x = CARD_WIDTH // 2 - 120
    sig_y = FOOTER_Y + 6
    draw.line([(sig_x, sig_y + 28), (sig_x + 240, sig_y + 28)], fill=COLOR_BORDER, width=1)
    draw_text_centered(draw, sig_x + 120, sig_y + 32,
                       "Controller of Examinations",
                       font(FONT_SANS_REG, 13), COLOR_TEXT_MID)
    draw_text_centered(draw, sig_x + 120, sig_y + 8,
                       "ABC University of Technology",
                       font(FONT_SANS_MED, 13), COLOR_TEXT_DARK)

    qr_data = f"ADMIT|{student.get('enrollment','?')}|{student.get('name','?')}|{student.get('semester','?')}"
    qr_img  = make_qr(qr_data, size=90)
    qr_x    = CARD_WIDTH - INFO_X - 100
    qr_y    = FOOTER_Y + 4
    canvas.paste(qr_img, (qr_x, qr_y))
    draw.text((qr_x, qr_y + 94), "Scan to verify",
              font=font(FONT_SANS_REG, 11), fill=COLOR_TEXT_MID)

    card_hash = hashlib.sha256(
        f"{student.get('enrollment','')}_{student.get('name','')}".encode()
    ).hexdigest()[:12].upper()
    draw.text((qr_x - 20, qr_y + 108),
              f"ID: {card_hash}",
              font=font(FONT_MONO, 10), fill=COLOR_TEXT_MID)

    draw.rectangle([(0, CARD_HEIGHT - 8), (CARD_WIDTH, CARD_HEIGHT)], fill=COLOR_NAVY)
    draw.rectangle([(0, CARD_HEIGHT - 11), (CARD_WIDTH, CARD_HEIGHT - 8)], fill=COLOR_GOLD)

    draw.rectangle([(1, 1), (CARD_WIDTH - 2, CARD_HEIGHT - 2)],
                   outline=COLOR_NAVY, width=2)

    return canvas

def parse_csv(csv_path: str) -> list[dict]:
    """
    Read CSV and return list of student dicts.
    Expected columns (case-insensitive, flexible naming):
        Name, Branch, Registration No., Course, Subjects, Subject Codes,
        Dates, Photo Link, Year, Semester, Time
    """
    students = []
    with open(csv_path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        # Normalise header names
        for row in reader:
            row = {k.strip(): v.strip() for k, v in row.items()}
            subjects      = [s.strip() for s in row.get("Subjects", "").split(",") if s.strip()]
            subject_codes = [c.strip() for c in row.get("Subject Codes", "").split(",") if c.strip()]
            dates         = [d.strip() for d in row.get("Dates", "").split(",") if d.strip()]
            students.append({
                "name":        row.get("Name", "Unknown"),
                "branch":      row.get("Branch", "—"),
                "enrollment":  row.get("Registration No.", row.get("Enrollment No", "—")),
                "course":      row.get("Course", "—"),
                "year":        row.get("Year", "—"),
                "semester":    row.get("Semester", "—"),
                "session":     row.get("Session", row.get("Academic Session", "2024–25")),
                "time":        row.get("Time", "—"),
                "photo_url":   row.get("Photo Link", row.get("Photo URL", "")),
                "subjects":      subjects,
                "subject_codes": subject_codes,
                "dates":         dates,
            })
    return students

def main():
    parser = argparse.ArgumentParser(description="Generate professional exam admit cards.")
    parser.add_argument("--csv",  default="students.csv",  help="Input CSV file path")
    parser.add_argument("--out",  default="images/output", help="Output directory")
    args = parser.parse_args()

    csv_path   = args.csv
    output_dir = Path(args.out)
    output_dir.mkdir(parents=True, exist_ok=True)

    if not Path(csv_path).exists():
        print(f"Error: CSV file '{csv_path}' not found.")
        sys.exit(1)

    print(f"Reading students from: {csv_path}")
    students = parse_csv(csv_path)
    print(f"Found {len(students)} student record(s).\n")

    success, failed = 0, 0
    for i, student in enumerate(students, 1):
        name       = student.get("name", f"student_{i}")
        enrollment = student.get("enrollment", f"unknown_{i}")
        safe_name  = "".join(c if c.isalnum() or c in "_ -" else "_" for c in name)
        out_path   = output_dir / f"AdmitCard_{safe_name}_{enrollment}.png"

        print(f"  [{i}/{len(students)}] Generating: {name} ({enrollment})")
        try:
            card = draw_admit_card(student)
            card.save(str(out_path), format="PNG", dpi=(150, 150))
            print(f"    ✓ Saved → {out_path}")
            success += 1
        except Exception:
            print(f"    ✗ FAILED for {name}:")
            traceback.print_exc()
            failed += 1

    print(f"\n{'─'*50}")
    print(f"Done. {success} generated, {failed} failed.")
    print(f"Output directory: {output_dir.resolve()}")


if __name__ == "__main__":
    main()
