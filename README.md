# THEY NEVER SLEEP  
**Interactive Map & Work Rhythm Visualization (OpenCV + YOLO)**

## Overview

**They Never Sleep** is an interactive system exploring the invisible rhythm of work in Japan.  
Observing workers leaving at 4 AM, last trains departing near midnight, and offices lit until dawn revealed a **constant, largely unnoticed temporal pattern**.  

> "Karoshi is the sum of the invisible sacrifices made by workers in order to meet the demands of a relentless and unforgiving society."  
> – Satoshi Kuroda

The project combines **interactive mapping, informative cards, and AI-driven video analysis** to document and visualize these rhythms. Users navigate cities, explore contextual information, and witness patterns of labor across time and space.

---

## Conceptual Framework

This project is rooted in **research-through-practice**, investigating how **human activity, temporality, and space** can be represented interactively.  

Key aims:  

- Highlight **invisible labor patterns** in urban and rural Japan.  
- Merge **qualitative observation with computational analysis**.  
- Design a **minimal, readable interface** that supports exploration without distraction.  
- Create **multimedia fiches** that contextualize each location through images, text, and video.

---

## System Logic

**They Never Sleep** operates through two complementary modules:

1. **Interactive Map**  
   - Displays Japan with city markers filtered by time (`ALL`, `5AM`, `8PM`).  
   - Clicking a city opens a **card**: an informative card presenting notes highlighting local work activity.  
   - Hover effects and toggle buttons provide immediate visual feedback.

2. **Detection HUD**  
   - Uses **YOLOv8** to detect objects in video recordings.  
   - Bounding boxes and confidence labels are optimized for **high readability in dark settings**.  
   - HUD overlays quantify activity (e.g., workers, vehicles) to support analysis of labor rhythms.

These modules allow exploration of both **qualitative context** (cards) and **quantitative patterns** (AI detection).

---

## Visual & Interaction Design

- **Map Navigation:** Click or hover over cities to view corresponding fiches.  
- **Time Toggle:** Filter cities by early morning, night, or all hours.  
- **Cards:** Informative cards to contextualize observed activity.  
- **Video Exploration:** Users can play city-specific videos directly from cards.  
- **Detection HUD:** Semi-transparent, color-coded overlays convey real-time object detection without obscuring content.

The interface prioritizes **clarity, readability, and subtlety**, reflecting the contemplative nature of the project.

---

## Technical Implementation

- **Languages & Libraries:** Python 3, OpenCV, NumPy, Ultralytics YOLOv8.  
- **Video & Image Processing:** Alpha blending, dynamic overlays, interactive UI elements.  
- **Interaction Handling:** Mouse callbacks for city selection, time toggling, and video playback.  
- **YOLO Integration:** Real-time detection with bounding boxes, class labels, and activity counts.  
- **Outputs:** Interactive map interface and processed video with HUD overlays.

---

## Project Structure

<pre><code>
they_never_sleep/
├── japan-map.png
├── references.png
├── cards/
│   └── city-card-time.png
├── font/
├── project.py
├── result/
│   └── city.mp4
├── yolov8s.pt
├── yolo.py
└── README.md
</code></pre>

---

## Research Perspective

**They Never Sleep** investigates labor rhythms through **site-specific observation and computational analysis**:  

1. **Sector Selection:** Choose activity sectors per city (offices, factories, transport hubs).  
2. **Field Recording:** Travel to smaller cities for direct audiovisual documentation.  
3. **AI Analysis:** Process videos with YOLOv8 to detect activity patterns, quantify movement, and extract object-specific insights.  
4. **Cards & Contextualization:** Combine visual and textual information into structured cards for each location.  

This approach combines **qualitative fieldwork and quantitative AI detection**, creating a **multimodal archive of unseen labor patterns**. It enables both **reflective exploration** and **data-driven insight**, supporting further research into urban temporality, overwork, and social rhythms.
