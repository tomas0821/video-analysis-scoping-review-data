# Coding guide

This is the guide given to every coder, with the answer list of each field. It is generated from `coding_form.py`.

## Manual screening and charting — video-based motion analysis in physics education (scoping review)

## Workflow

1. Each author codes in their own copy of this workbook (coding_TR.xlsx, coding_EAN.xlsx), without looking at the other copy.

2. Calibration first: filter the Screening sheet on 'Calibration = Yes' (40 records), code them, compare with the other coder, discuss and sharpen the rules below. Then code the rest.

3. Screening sheet: answer the two questions for every record; Decision = Include only if both are Yes. 'Screened on' = Full text or Title/abstract (use the full text whenever a file is linked or you can obtain one).

4. Charting sheet: fill only for records you include on full text. Rows turn grey when your Screening decision is Exclude. Block B (purple) only for papers whose Paper type is 'Empirical study with students'.

5. When both copies are complete, they are compared with each other and with the AI coding of the same records (kept outside these workbooks). Agreement (Cohen's kappa) is computed and every disagreement is resolved by discussion.

Full texts: records without a PDF on disk have a slot 'Add PDF here' = fulltexts/R###.pdf. Save the PDF in manual_coding/fulltexts/ under that name and the link works (see pdfs_needed.xlsx for the prioritised list).

6. Blind coding: this workbook holds no AI or draft values. While coding, do not consult the AI coding, the earlier draft files or the manuscript's tables of included studies.

## Eligibility (both must hold)

Physics education = Yes if the paper concerns physics teaching, learning or education: labs for students, experiments designed or presented for teaching, curricula, teacher education, or experimental physics with pedagogical intent (e.g. an experiment presented for students or instructors in a physics-teaching journal). No for pure research, engineering or industry, sports science, biomechanics or clinical work without a physics-teaching purpose.

Video-based motion analysis = Yes if quantitative data are read from successive frames of a camera video: an object tracked frame by frame (manually or automatically: Tracker, Logger Pro, Viana, Python/OpenCV...), timing by counting frames, or another quantity that changes over time read frame by frame (e.g. a meter display or a brightness). No if video is only watched, recorded or coded qualitatively (classroom recordings, demonstration or instructional videos, video clips as teaching media). Smartphone sensors alone do not count.

Decision rules: (1) single-photograph test: if one photograph would have given the same data, it does not count (still photographs, paused frames of a static set-up, distances or angles measured on a static scene); (2) papers where video analysis is only part of the work are included if camera video is actually analysed (not merely recommended or shown); (3) a stated pedagogical purpose counts as physics-education intent even without students; (4) literature reviews are excluded (they do not themselves use video analysis); (5) camera test: the video must be filmed with an ordinary camera, so computer animations, simulations, screen recordings and depth or infrared sensors (Kinect, Intel RealSense) do not count.

## Charting — core fields (green)

Physics topic: the topic of the main video-analysed activity. Pendulums and springs are Oscillations & Waves even when used to measure g or energy; a conical pendulum is circular motion; a falling or rolling body is Mechanics; Brownian motion is Modern & Nuclear Physics; granular flow is Fluids. Several activities: code the dominant one and set 'Several topics' = Yes only if the activities span more than one physics topic (several mechanics subtopics alone = No); no dominant topic = Other.

Mechanics subtopic (mechanics papers only): Kinematics & Free Fall / Projectile / Dynamics & Forces (Newton's laws, Atwood machines, inclined planes) / Circular & Rotational (incl. rolling, moment of inertia) / Collisions & Momentum / Energy Conservation / Friction & Drag (incl. terminal velocity) / Gravitation & Orbital / Other-Mixed (only if none fits or several are equally central).

Educational level: Yes in every column the paper states (the intended or the actual level); do not infer a level from the country, the curriculum or the content. 'Level not stated' = Yes when the paper names no level. Paper type: Activity description (authors' own measurements, no student data) / Implementation report (run with real students, at most informal impressions) / Empirical study with students (systematic data on students: tests, questionnaires, interviews, performance) / Accuracy or methods study (main aim is the measurement technique itself) / Other. Stated aim = the goal the authors state, not what was measured.

## Block A (orange) — every included full text

Implemented with students: 'Used with students' only if real students actually did or saw the activity. Students' role: what students do with the video ('None (authors only)' for proposed activities analysed only by the authors, unless the paper prescribes a student role). Frame rate: value with unit (e.g. 240 fps) or 'Not reported'. Calibration described: how the length scale was set (reference of known length, calibration stick, grid) or perspective/lens correction. Uncertainty: Quantitative = numerical uncertainties (±, error bars, SD, fit uncertainties, % error vs reference); Qualitative = error sources discussed in words only. Checked against: accepted or theoretical value (including a prediction from a closed-form formula) / other instrument (sensors, photogates, motion detectors) / simulation or model (a computational simulation or a model of the motion solved numerically, not a closed-form formula). Model building = a dynamical or computational model of the motion is built and compared with the data (fitting a function does not count). Materials shared = videos, data, worksheets or code made available ('available from the authors' does not count). Remote context = designed for or used in remote/online/home learning.

## Block B (purple) — empirical studies with students only

Design: One-group pre/post / Comparison group (non-randomised) / Randomised comparison / Qualitative / Survey only (opinions or attitudes, no learning test) / Other. Comparison condition: what the video-analysis group was compared with. Sample: total participants analysed. Outcome: what was measured. Instrument: standardised test (name it: FCI, TUG-K, FMCE...) / author-made test / questionnaire / interview or observation / grades or student work. Result: direction of the main reported effect for the video-analysis condition (Negative = the video-analysis condition did worse than the comparison, or the outcome declined). Effect size: value and type if reported (e.g. Hake gain 0.42). Duration: single session / several sessions / whole course.

Colour key: blue = record information (do not edit); yellow = screening; green = core charting; orange = block A; purple = block B.

## Answer lists


### Screening

- **Physics education?**: Yes | No
- **Video-based motion analysis?**: Yes | No
- **Decision**: Include | Exclude
- **Exclusion reason**: Not physics education | No video-based motion analysis | Neither criterion | Literature review | Not a primary article | Duplicate | File is not the paper | Other
- **Screened on**: free text
- **Notes**: free text

### Charting: core

- **Physics topic**: Mechanics | Oscillations & Waves | Electromagnetism | Optics | Thermodynamics | Fluids | Modern & Nuclear Physics | Astronomy | Other
- **Mechanics subtopic**: Kinematics & Free Fall | Projectile Motion | Dynamics & Forces | Circular & Rotational Motion | Collisions & Momentum | Energy Conservation | Friction & Drag | Gravitation & Orbital Motion | Other / Mixed Mechanics
- **Several topics?**: Yes | No
- **Software (main)**: Tracker | Logger Pro | COACH | Viana | VideoPoint | Vernier Video Physics | MATLAB | Python / OpenCV | Other | Not stated
- **Software (other / additional)**: free text
- **Recording hardware**: Smartphone | Tablet | Webcam | Digital camera | High-speed camera | Other | Not stated
- **Middle school**: Yes | No
- **High school**: Yes | No
- **Undergraduate intro**: Yes | No
- **Undergraduate advanced**: Yes | No
- **Teacher education**: Yes | No
- **Level not stated**: Yes | No
- **Setting**: Lab | Classroom | Online / home | Outdoor | Other | Not stated
- **Video subject**: Real-world objects | Standard lab equipment | Student-produced | Archival / professional footage | Other
- **Author countries**: free text
- **Paper type**: Activity description | Implementation report | Empirical study with students | Accuracy or methods study | Other
- **Stated aim (main)**: Conceptual understanding | Graphs and representations | Measurement and lab skills | Modelling | Inquiry and research skills | Engagement and motivation | Other | Not stated
- **Stated aim (second)**: Conceptual understanding | Graphs and representations | Measurement and lab skills | Modelling | Inquiry and research skills | Engagement and motivation | Other | Not stated

### Charting: block A

- **Implemented with students?**: Proposed only | Used with students | Unclear
- **Students (n)**: free text
- **Students' role**: Record own video | Analyse provided video | Watch demonstration | None (authors only) | Unclear
- **Frame rate**: free text
- **Calibration described?**: Yes | No
- **Uncertainty analysis**: None | Qualitative | Quantitative
- **Checked against accepted/theoretical value?**: Yes | No
- **Checked against other instrument?**: Yes | No
- **Checked against simulation/model?**: Yes | No
- **Model building?**: Yes | No
- **Materials shared?**: Yes | No
- **Remote/home context?**: Yes | No
- **Language**: English | Portuguese | Spanish | Indonesian | Other

### Charting: block B (empirical studies with students)

- **B: Design**: One-group pre/post | Comparison group (non-randomised) | Randomised comparison | Qualitative | Survey only | Other
- **B: Comparison condition**: None | Traditional instruction or lab | Sensors or probeware | Simulation | Other
- **B: Sample (n)**: free text
- **B: Sample level**: Middle school | High school | Undergraduate intro | Undergraduate | Pre-service teachers | In-service teachers | Mixed | Not stated
- **B: Outcome (main)**: Conceptual understanding | Graph interpretation | Lab or inquiry skills | Problem solving | Attitudes, motivation or engagement | Other
- **B: Outcome (second)**: Conceptual understanding | Graph interpretation | Lab or inquiry skills | Problem solving | Attitudes, motivation or engagement | Other
- **B: Instrument (main)**: Standardised test | Author-made test | Questionnaire or survey | Interview or observation | Grades or student work
- **B: Instrument names**: free text
- **B: Result**: Positive | Null | Mixed | Negative | Not reported
- **B: Effect size**: free text
- **B: Duration**: Single session | Several sessions | Whole course or semester | Not stated

### Notes

- **Charting notes**: free text
