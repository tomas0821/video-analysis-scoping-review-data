"""
The coding form of the scoping review "Video analysis as a pedagogical tool in physics education":
the answer lists, the screening and charting fields, and the coding guide given to every coder.
Imported by the workbook builder and by the analysis scripts, so the form is defined in one place.
"""
import re

LISTS = {
    "YN": ["Yes", "No"],
    "Decision": ["Include", "Exclude"],
    "Exclusion": ["Not physics education", "No video-based motion analysis", "Neither criterion",
                  "Literature review", "Not a primary article", "Duplicate", "File is not the paper", "Other"],
    "Topic": ["Mechanics", "Oscillations & Waves", "Electromagnetism", "Optics", "Thermodynamics", "Fluids",
              "Modern & Nuclear Physics", "Astronomy", "Other"],
    "Subtopic": ["Kinematics & Free Fall", "Projectile Motion", "Dynamics & Forces", "Circular & Rotational Motion",
                 "Collisions & Momentum", "Energy Conservation", "Friction & Drag", "Gravitation & Orbital Motion",
                 "Other / Mixed Mechanics"],
    "Software": ["Tracker", "Logger Pro", "COACH", "Viana", "VideoPoint", "Vernier Video Physics", "MATLAB",
                 "Python / OpenCV", "Other", "Not stated"],
    "Hardware": ["Smartphone", "Tablet", "Webcam", "Digital camera", "High-speed camera", "Other", "Not stated"],
    "Setting": ["Lab", "Classroom", "Online / home", "Outdoor", "Other", "Not stated"],
    "Subject": ["Real-world objects", "Standard lab equipment", "Student-produced", "Archival / professional footage",
                "Other"],
    "PaperType": ["Activity description", "Implementation report", "Empirical study with students",
                  "Accuracy or methods study", "Other"],
    "Aim": ["Conceptual understanding", "Graphs and representations", "Measurement and lab skills", "Modelling",
            "Inquiry and research skills", "Engagement and motivation", "Other", "Not stated"],
    "Implemented": ["Proposed only", "Used with students", "Unclear"],
    "Role": ["Record own video", "Analyse provided video", "Watch demonstration", "None (authors only)", "Unclear"],
    "Uncertainty": ["None", "Qualitative", "Quantitative"],
    "Language": ["English", "Portuguese", "Spanish", "Indonesian", "Other"],
    "Design": ["One-group pre/post", "Comparison group (non-randomised)", "Randomised comparison", "Qualitative",
               "Survey only", "Other"],
    "Comparison": ["None", "Traditional instruction or lab", "Sensors or probeware", "Simulation", "Other"],
    "SampleLevel": ["Middle school", "High school", "Undergraduate intro", "Undergraduate", "Pre-service teachers",
                    "In-service teachers", "Mixed", "Not stated"],
    "Outcome": ["Conceptual understanding", "Graph interpretation", "Lab or inquiry skills", "Problem solving",
                "Attitudes, motivation or engagement", "Other"],
    "Instrument": ["Standardised test", "Author-made test", "Questionnaire or survey", "Interview or observation",
                   "Grades or student work"],
    "Result": ["Positive", "Null", "Mixed", "Negative", "Not reported"],
    "Duration": ["Single session", "Several sessions", "Whole course or semester", "Not stated"],
}

# (header, list name or None for free entry, width, block)
SCREEN_COLS = [
    ("Physics education?", "YN", 11, "code"), ("Video-based motion analysis?", "YN", 13, "code"),
    ("Decision", "Decision", 10, "code"), ("Exclusion reason", "Exclusion", 20, "code"),
    ("Screened on", None, 11, "code"), ("Notes", None, 30, "code"),
]
CHART_COLS = [
    # core form
    ("Physics topic", "Topic", 16, "core"), ("Mechanics subtopic", "Subtopic", 18, "core"),
    ("Several topics?", "YN", 9, "core"), ("Software (main)", "Software", 14, "core"),
    ("Software (other / additional)", None, 18, "core"), ("Recording hardware", "Hardware", 14, "core"),
    ("Middle school", "YN", 8, "core"), ("High school", "YN", 8, "core"), ("Undergraduate intro", "YN", 10, "core"),
    ("Undergraduate advanced", "YN", 11, "core"), ("Teacher education", "YN", 9, "core"),
    ("Level not stated", "YN", 9, "core"), ("Setting", "Setting", 12, "core"), ("Video subject", "Subject", 16, "core"),
    ("Author countries", None, 16, "core"), ("Paper type", "PaperType", 20, "core"),
    ("Stated aim (main)", "Aim", 18, "core"), ("Stated aim (second)", "Aim", 18, "core"),
    # block A
    ("Implemented with students?", "Implemented", 14, "A"), ("Students (n)", None, 8, "A"),
    ("Students' role", "Role", 16, "A"), ("Frame rate", None, 10, "A"), ("Calibration described?", "YN", 10, "A"),
    ("Uncertainty analysis", "Uncertainty", 12, "A"), ("Checked against accepted/theoretical value?", "YN", 12, "A"),
    ("Checked against other instrument?", "YN", 11, "A"), ("Checked against simulation/model?", "YN", 11, "A"),
    ("Model building?", "YN", 9, "A"), ("Materials shared?", "YN", 9, "A"), ("Remote/home context?", "YN", 9, "A"),
    ("Language", "Language", 11, "A"),
    # block B
    ("B: Design", "Design", 18, "B"), ("B: Comparison condition", "Comparison", 16, "B"), ("B: Sample (n)", None, 8, "B"),
    ("B: Sample level", "SampleLevel", 14, "B"), ("B: Outcome (main)", "Outcome", 18, "B"),
    ("B: Outcome (second)", "Outcome", 18, "B"), ("B: Instrument (main)", "Instrument", 16, "B"),
    ("B: Instrument names", None, 14, "B"), ("B: Result", "Result", 10, "B"), ("B: Effect size", None, 14, "B"),
    ("B: Duration", "Duration", 14, "B"),
    ("Charting notes", None, 30, "note"),
]


def clean(t):
    t = re.sub(r"[{}]", "", t or "")
    t = re.sub(r"\\['`^\"~]", "", t)
    return re.sub(r"\s+", " ", t).strip()


def first_author(authors):
    names = [a.strip() for a in re.split(r"\s+and\s+", authors or "") if a.strip()]
    if not names:
        return ""
    sur = names[0].split(",")[0].strip()
    return sur if len(names) == 1 else (f"{sur} and {names[1].split(',')[0].strip()}" if len(names) == 2
                                        else f"{sur} et al.")


def guide_text():
    return [
        ("Manual screening and charting — video-based motion analysis in physics education (scoping review)", True),
        ("", False),
        ("Workflow", True),
        ("1. Each author codes in their own copy of this workbook (coding_TR.xlsx, coding_EAN.xlsx), without looking at the other copy.", False),
        ("2. Calibration first: filter the Screening sheet on 'Calibration = Yes' (40 records), code them, compare with the other coder, discuss and sharpen the rules below. Then code the rest.", False),
        ("3. Screening sheet: answer the two questions for every record; Decision = Include only if both are Yes. 'Screened on' = Full text or Title/abstract (use the full text whenever a file is linked or you can obtain one).", False),
        ("4. Charting sheet: fill only for records you include on full text. Rows turn grey when your Screening decision is Exclude. Block B (purple) only for papers whose Paper type is 'Empirical study with students'.", False),
        ("5. When both copies are complete, they are compared with each other and with the AI coding of the same records (kept outside these workbooks). Agreement (Cohen's kappa) is computed and every disagreement is resolved by discussion.", False),
        ("Full texts: records without a PDF on disk have a slot 'Add PDF here' = fulltexts/R###.pdf. Save the PDF in manual_coding/fulltexts/ under that name and the link works (see pdfs_needed.xlsx for the prioritised list).", False),
        ("6. Blind coding: this workbook holds no AI or draft values. While coding, do not consult the AI coding, the earlier draft files or the manuscript's tables of included studies.", False),
        ("", False),
        ("Eligibility (both must hold)", True),
        ("Physics education = Yes if the paper concerns physics teaching, learning or education: labs for students, experiments designed or presented for teaching, curricula, teacher education, or experimental physics with pedagogical intent (e.g. an experiment presented for students or instructors in a physics-teaching journal). No for pure research, engineering or industry, sports science, biomechanics or clinical work without a physics-teaching purpose.", False),
        ("Video-based motion analysis = Yes if quantitative data are read from successive frames of a camera video: an object tracked frame by frame (manually or automatically: Tracker, Logger Pro, Viana, Python/OpenCV...), timing by counting frames, or another quantity that changes over time read frame by frame (e.g. a meter display or a brightness). No if video is only watched, recorded or coded qualitatively (classroom recordings, demonstration or instructional videos, video clips as teaching media). Smartphone sensors alone do not count.", False),
        ("Decision rules: (1) single-photograph test: if one photograph would have given the same data, it does not count (still photographs, paused frames of a static set-up, distances or angles measured on a static scene); (2) papers where video analysis is only part of the work are included if camera video is actually analysed (not merely recommended or shown); (3) a stated pedagogical purpose counts as physics-education intent even without students; (4) literature reviews are excluded (they do not themselves use video analysis); (5) camera test: the video must be filmed with an ordinary camera, so computer animations, simulations, screen recordings and depth or infrared sensors (Kinect, Intel RealSense) do not count.", False),
        ("", False),
        ("Charting — core fields (green)", True),
        ("Physics topic: the topic of the main video-analysed activity. Pendulums and springs are Oscillations & Waves even when used to measure g or energy; a conical pendulum is circular motion; a falling or rolling body is Mechanics; Brownian motion is Modern & Nuclear Physics; granular flow is Fluids. Several activities: code the dominant one and set 'Several topics' = Yes only if the activities span more than one physics topic (several mechanics subtopics alone = No); no dominant topic = Other.", False),
        ("Mechanics subtopic (mechanics papers only): Kinematics & Free Fall / Projectile / Dynamics & Forces (Newton's laws, Atwood machines, inclined planes) / Circular & Rotational (incl. rolling, moment of inertia) / Collisions & Momentum / Energy Conservation / Friction & Drag (incl. terminal velocity) / Gravitation & Orbital / Other-Mixed (only if none fits or several are equally central).", False),
        ("Educational level: Yes in every column the paper states (the intended or the actual level); do not infer a level from the country, the curriculum or the content. 'Level not stated' = Yes when the paper names no level. Paper type: Activity description (authors' own measurements, no student data) / Implementation report (run with real students, at most informal impressions) / Empirical study with students (systematic data on students: tests, questionnaires, interviews, performance) / Accuracy or methods study (main aim is the measurement technique itself) / Other. Stated aim = the goal the authors state, not what was measured.", False),
        ("", False),
        ("Block A (orange) — every included full text", True),
        ("Implemented with students: 'Used with students' only if real students actually did or saw the activity. Students' role: what students do with the video ('None (authors only)' for proposed activities analysed only by the authors, unless the paper prescribes a student role). Frame rate: value with unit (e.g. 240 fps) or 'Not reported'. Calibration described: how the length scale was set (reference of known length, calibration stick, grid) or perspective/lens correction. Uncertainty: Quantitative = numerical uncertainties (±, error bars, SD, fit uncertainties, % error vs reference); Qualitative = error sources discussed in words only. Checked against: accepted or theoretical value (including a prediction from a closed-form formula) / other instrument (sensors, photogates, motion detectors) / simulation or model (a computational simulation or a model of the motion solved numerically, not a closed-form formula). Model building = a dynamical or computational model of the motion is built and compared with the data (fitting a function does not count). Materials shared = videos, data, worksheets or code made available ('available from the authors' does not count). Remote context = designed for or used in remote/online/home learning.", False),
        ("", False),
        ("Block B (purple) — empirical studies with students only", True),
        ("Design: One-group pre/post / Comparison group (non-randomised) / Randomised comparison / Qualitative / Survey only (opinions or attitudes, no learning test) / Other. Comparison condition: what the video-analysis group was compared with. Sample: total participants analysed. Outcome: what was measured. Instrument: standardised test (name it: FCI, TUG-K, FMCE...) / author-made test / questionnaire / interview or observation / grades or student work. Result: direction of the main reported effect for the video-analysis condition (Negative = the video-analysis condition did worse than the comparison, or the outcome declined). Effect size: value and type if reported (e.g. Hake gain 0.42). Duration: single session / several sessions / whole course.", False),
        ("", False),
        ("Colour key: blue = record information (do not edit); yellow = screening; green = core charting; orange = block A; purple = block B.", False),
    ]
