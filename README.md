# Admit Card Generator v2.0

Generates professional, print-ready exam admit cards as PNG images from a CSV of student records. Each card includes a student info panel, a full subject/date/time schedule table, a validity stamp, and a scannable QR code for verification.

---

## Screenshots

<img width="1200" height="735" alt="sample_admit_card" src="https://github.com/user-attachments/assets/cdb812d2-34b5-4b1d-aa40-f69b67b801d8" />

---

## Quick Demo (2 minutes)

**1. Install dependencies**

```bash
pip install pillow qrcode requests
```

> Poppins and DejaVu fonts must be available on your system. On Ubuntu/Debian:
> ```bash
> sudo apt install fonts-dejavu fonts-google-fonts
> ```
> On other systems, update the `FONT_DIR` path near the top of `admit_card.py` to point at your `.ttf` files.

**2. Create a minimal test CSV** — save this as `students.csv`:

```csv
Name,Branch,Registration No.,Course,Subjects,Subject Codes,Dates,Photo Link,Year,Semester,Time
Jane Doe,Computer Science,CS2024001,B.Tech,"Data Structures,Algorithms,OS","CS301,CS302,CS303","Nov 10 2024,Nov 12 2024,Nov 14 2024",,2nd,2024-25,10:00 AM - 01:00 PM
```

**3. Run it**

```bash
python admit_card.py
```

Output cards land in `images/output/` by default, one PNG per student.

---

## Full Usage

```
python admit_card.py [--csv FILE] [--out DIR]
```

| Flag | Default | Description |
|------|---------|-------------|
| `--csv` | `students.csv` | Path to your input CSV file |
| `--out` | `images/output` | Directory where PNGs are saved |

**Examples**

```bash
# Use default students.csv, output to images/output/
python admit_card.py

# Custom CSV and output folder
python admit_card.py --csv data/batch_spring_2025.csv --out results/spring_2025/

# Quick test with the provided sample
python admit_card.py --csv sample_students.csv --out demo_output/
```

Progress is printed for every student. Failures are reported per-record without stopping the rest of the batch.

---

## CSV Format

Each row is one student. Column headers must match these names exactly (leading/trailing spaces are stripped automatically):

| Column | Required | Notes |
|--------|----------|-------|
| `Name` | Yes | Full student name; used in the output filename |
| `Registration No.` | Yes | Also accepted as `Enrollment No` |
| `Branch` | Yes | e.g. `Computer Science & Engineering` |
| `Course` | Yes | e.g. `Bachelor of Technology (B.Tech)` |
| `Year` | Yes | e.g. `3rd` |
| `Semester` | Yes | e.g. `2024-25` |
| `Subjects` | Yes | Comma-separated list, **quoted if it contains commas**: `"Data Structures,OS,Networks"` |
| `Subject Codes` | Yes | Comma-separated, same order as Subjects: `"CS301,CS302,CS303"` |
| `Dates` | Yes | Comma-separated, same order as Subjects: `"Nov 10 2024,Nov 12 2024,Nov 14 2024"` |
| `Time` | Yes | Shared exam time for all subjects: `10:00 AM - 01:00 PM` |
| `Photo Link` | No | Direct URL or Google Drive share link to student photo. Blank = silhouette placeholder |
| `Session` | No | e.g. `2024-25`. Defaults to `2024-25` if omitted |

**Important:** Subjects, Subject Codes, and Dates must have the same number of entries and be in the same order — row 1 of each maps to the same exam.

### Sample rows

```csv
Name,Branch,Registration No.,Course,Subjects,Subject Codes,Dates,Photo Link,Year,Semester,Time
Arjun Sharma,Computer Science & Engineering,CS2024001,Bachelor of Technology (B.Tech),"Data Structures,Operating Systems,Database Management,Computer Networks,Software Engineering","CS301,CS302,CS303,CS304,CS305","Nov 15 2024,Nov 17 2024,Nov 19 2024,Nov 21 2024,Nov 23 2024",,3rd,2024-25,10:00 AM - 01:00 PM
Priya Patel,Electronics & Communication,EC2024042,Bachelor of Technology (B.Tech),"Signals & Systems,Digital Electronics,Microprocessors,Communication Theory","EC201,EC202,EC203,EC204","Nov 14 2024,Nov 16 2024,Nov 18 2024,Nov 20 2024",,2nd,2024-25,02:00 PM - 05:00 PM
```

---

## Output Files

Cards are saved as:

```
AdmitCard_<Name>_<RegistrationNo>.png
```

For example: `AdmitCard_Arjun Sharma_CS2024001.png`

The image dimensions scale dynamically — taller cards are produced for students with more subjects, shorter ones for fewer. All cards are 1200 px wide at 150 DPI, suitable for A4 printing.

---

## What's on Each Card

```
┌──────────────────────────────────────────────────────┐
│  ABC University of Technology        Session: 2024-25 │  ← Navy header
│              ADMIT CARD                               │
├──────────────────────────────────────────────────────┤
│  Name:         Arjun Sharma    Year:  3rd     [ photo]│  ← Info panel
│  Enrollment:   CS2024001       Sem:   2024-25         │
│  Branch:       CS & Engg       Time:  10AM-1PM        │
│  Course:       B.Tech                                 │
├──────────────────────────────────────────────────────┤
│  Subject          Code    Exam Date      Exam Time    │  ← Subject table
│  Data Structures  CS301   Nov 15 2024   10AM-1PM      │
│  Operating Sys.   CS302   Nov 17 2024   10AM-1PM      │
│  ...                                                  │
├──────────────────────────────────────────────────────┤
│  [VALID] 09 Jun 2026   Controller of Exams   [QR]    │  ← Footer
└──────────────────────────────────────────────────────┘
```

The QR code encodes `ADMIT|<enrollment>|<name>|<semester>` and can be scanned to verify authenticity. A unique card ID (truncated SHA-256 hash of enrollment + name) is printed beneath it.

**Real output example:**

<img width="1200" height="735" alt="sample_admit_card" src="https://github.com/user-attachments/assets/0810f059-48b1-4bcd-a43f-c3a230df6ec7" />

---

## Customising the Card

All visual constants live near the top of `admit_card.py` under `# CONFIG`. Common things to change:

**University name** — find this line and update the string:
```python
draw_text_centered(draw, CARD_WIDTH // 2, 14, "ABC University of Technology", ...)
```

**Colour scheme** — edit the palette block:
```python
COLOR_NAVY  = (13, 47, 95)    # Header and table header background
COLOR_GOLD  = (192, 155, 73)  # Accent lines and "ADMIT CARD" text
```

**Fonts** — update `FONT_DIR` and the four `FONT_SANS_*` / `FONT_SERIF_*` paths if your fonts live elsewhere.

**Card width** — change `CARD_WIDTH = 1200`. Height is always computed automatically.

---

## Troubleshooting

**`IOError: cannot open font`**
The Poppins or DejaVu fonts aren't found at the default path. Either install them (see Quick Demo step 1) or update `FONT_DIR` in `admit_card.py` to wherever your `.ttf` files live. The script falls back to PIL's built-in bitmap font if a face fails to load, so cards will still generate — just with uglier text.

**`[!] Photo download failed`**
The photo URL is unreachable or requires authentication. The card still generates with a silhouette placeholder. For Google Drive photos, make sure the share link is set to "Anyone with the link can view."

**Subjects/dates don't line up**
Check that the `Subjects`, `Subject Codes`, and `Dates` columns have the same number of comma-separated entries for that student row.

**Output directory not created**
The script creates the output directory automatically. If it fails, check that the parent path exists and you have write permission.
