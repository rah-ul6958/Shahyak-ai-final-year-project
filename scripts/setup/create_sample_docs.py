#!/usr/bin/env python3
"""
Create sample NDMA protocol documents for testing the RAG pipeline.
These are simplified versions of actual NDMA guidelines.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "backend"))

import fitz  # PyMuPDF


SAMPLE_DOCUMENTS = [
    {
        "filename": "NDMA_Flood_Protocol_2019.pdf",
        "title": "NDMA Flood Response Protocol 2019",
        "content": """
NATIONAL DISASTER MANAGEMENT AUTHORITY
FLOOD RESPONSE PROTOCOL 2019

Chapter 1: General Flood Safety Guidelines

1.1 Pre-Flood Preparedness
- Keep emergency supplies ready: water, food, medications, flashlight, batteries
- Know your evacuation routes and nearest shelter locations
- Keep important documents in waterproof containers
- Install flood warnings and stay alert to weather updates
- Maintain a family emergency communication plan

1.2 During Flood Warning
- Move to higher ground immediately when warned
- Do not wait for instructions to evacuate if water is rising
- Avoid walking through flowing water - 6 inches can knock you down
- Do not drive through flooded roads - 2 feet of water can sweep away vehicles
- Stay away from bridges over fast-moving water

1.3 During Flood
- If trapped in a building, go to the highest floor, not the attic
- Signal for help if needed: whistle, flashlight, bright cloth
- Do not touch electrical equipment if wet or standing in water
- Avoid contact with floodwater - it may be contaminated
- Do not return to flooded areas until authorities declare safe

Chapter 2: Flood First Aid

2.1 Drowning Response
- Call emergency services immediately
- Begin CPR if person is not breathing
- Do not attempt rescue in swift water without proper equipment
- Use reaching or throwing aids from safe locations

2.2 Waterborne Disease Prevention
- Use only bottled or boiled water for drinking
- Wash hands frequently with soap and clean water
- Report any symptoms of diarrhea, vomiting, or fever
- Dispose of dead animals and waste properly

Chapter 3: Uttarakhand Specific Guidelines

3.1 Flash Flood Areas
- Chamoli, Rudraprayag, and Uttarkashi districts are high-risk zones
- River valleys and steep terrain increase flash flood risk
- Monsoon season (June-September) requires extra vigilance
- Stay alert for sudden water level rises in rivers

3.2 Evacuation Procedures
- Follow designated evacuation routes marked by SDRF
- Assembly points are at community centers and schools
- Register at shelters for tracking and assistance
- Carry identification and emergency contact information
"""
    },
    {
        "filename": "NDMA_Earthquake_Protocol_2020.pdf",
        "title": "NDMA Earthquake Response Protocol 2020",
        "content": """
NATIONAL DISASTER MANAGEMENT AUTHORITY
EARTHQUAKE RESPONSE PROTOCOL 2020

Chapter 1: Earthquake Safety Guidelines

1.1 Before Earthquake
- Secure heavy furniture and appliances to walls
- Identify safe spots in each room: under sturdy tables, against interior walls
- Keep emergency kit accessible with water, food, first aid
- Know how to shut off gas, water, and electricity
- Practice earthquake drills with family

1.2 During Earthquake - Drop, Cover, Hold On
- DROP to hands and knees to prevent being knocked down
- COVER head and neck under a sturdy table or desk
- HOLD ON to shelter until shaking stops
- If outdoors, move to open area away from buildings
- If driving, pull over, stop, and stay inside vehicle

1.3 After Earthquake
- Check for injuries and provide first aid
- Inspect building for damage before re-entering
- Expect aftershocks - be prepared to take cover
- Do not use damaged elevators
- Report damaged infrastructure to authorities

Chapter 2: Post-Earthquake Response

2.1 Building Safety Assessment
- Check for structural damage: cracks, tilted walls, shifted foundation
- Do not enter severely damaged buildings
- Mark unsafe buildings for demolition
- Use professional assessors for evaluation

2.2 Utilities Safety
- Check for gas leaks - smell or hissing sounds
- If gas leak suspected, open windows, do not use electrical switches
- Report utility damage to authorities
- Do not use water until supply is confirmed safe

Chapter 3: Uttarakhand Earthquake Zone

3.1 Seismic Zone V
- Uttarakhand falls in highest seismic zone (Zone V)
- Chamoli district experienced 6.8 magnitude earthquake in 1999
- Regular tremors are common - stay prepared
- Traditional stone houses are vulnerable to shaking

3.2 Emergency Shelters
- Designated earthquake shelters at community centers
- Open ground assembly points in each district
- Medical teams stationed at district hospitals
- SDRF teams on standby during monsoon season
"""
    },
    {
        "filename": "NDMA_Cyclone_Protocol_2018.pdf",
        "title": "NDMA Cyclone Response Protocol 2018",
        "content": """
NATIONAL DISASTER MANAGEMENT AUTHORITY
CYCLONE RESPONSE PROTOCOL 2018

Chapter 1: Cyclone Preparedness

1.1 Before Cyclone Season
- Identify cyclone shelter locations in your area
- Stock emergency supplies for at least 3 days
- Trim trees and secure loose objects around property
- Know evacuation routes to higher ground
- Keep battery-powered radio for updates

1.2 During Cyclone Warning
- Complete evacuation when ordered by authorities
- Stay away from windows and glass doors
- If in sturdy building, stay on lowest floor, interior room
- If evacuation not possible, go to cyclone shelter immediately
- Keep emergency kit and important documents ready

Chapter 2: During Cyclone

2.1 Safety Measures
- Stay indoors until authorities give all-clear
- Do not go outside during eye of cyclone - winds resume suddenly
- Avoid using candles - use flashlights instead
- Do not touch fallen power lines
- Stay away from flooded areas

2.2 After Cyclone
- Check for injuries and provide first aid
- Report damaged infrastructure
- Do not use contaminated water
- Be aware of landslides in hilly areas

Chapter 3: Odisha Cyclone Response

3.1 Coastal Districts
- Puri, Khordha, and Cuttack are high-risk districts
- Cyclone shelters available at 500m+ elevation
- SDRF teams pre-positioned before cyclone landfall
- Community-based early warning system in place

3.2 Evacuation Protocol
- Follow numbered evacuation routes to shelters
- Carry only essential items and documents
- Register at shelter for tracking
- Do not return until all-clear announcement

Chapter 4: Kerala Monsoon Guidelines

4.1 Southwest Monsoon (June-September)
- Heavy rainfall expected in Western Ghats
- Landslide risk in hilly terrain
- River flooding common in low-lying areas
- Stay alert for red alerts from IMD

4.2 Emergency Contacts
- Kerala SDMA: 1070
- Police: 100
- Fire: 101
- Ambulance: 108
"""
    },
    {
        "filename": "NDMA_Medical_Emergency_Protocol.pdf",
        "title": "NDMA Medical Emergency Response Protocol",
        "content": """
NATIONAL DISASTER MANAGEMENT AUTHORITY
MEDICAL EMERGENCY RESPONSE PROTOCOL

Chapter 1: General Medical Emergency Response

1.1 First Aid Principles
- Ensure scene safety before approaching victim
- Call emergency services immediately for serious injuries
- Do not move person with suspected spinal injury
- Control bleeding with direct pressure
- Keep victim warm and calm

1.2 Cardiac Emergency
- Check for responsiveness and breathing
- Begin CPR immediately if no pulse: 30 compressions, 2 breaths
- Use AED if available
- Continue until emergency services arrive

1.3 Burn Treatment
- Cool burn with running water for 10-20 minutes
- Do not apply ice, butter, or ointments
- Cover with clean, non-stick dressing
- Do not break blisters
- Seek medical attention for large or deep burns

Chapter 2: Disaster-Specific Medical Response

2.1 Crush Injuries
- Do not remove heavy objects from victim
- Provide oxygen if available
- Monitor for shock symptoms
- Prepare for possible cardiac arrest when object removed

2.2 Hypothermia
- Move victim to warm, dry location
- Remove wet clothing
- Warm victim gradually with blankets
- Do not rub extremities
- Provide warm fluids if conscious

2.3 Heat Stroke
- Move victim to cool area immediately
- Cool body with water and fans
- Do not give fluids if unconscious
- Monitor airway and breathing
- Emergency cooling required

Chapter 3: Kerala Medical Infrastructure

3.1 Major Hospitals
- Government Medical College, Thiruvananthapuram: 600 beds
- Amrita Hospital, Kochi: 700 beds
- Medical College, Kozhikode: 500 beds
- AIIMS-like facility at Kottayam

3.2 Emergency Medical Teams
- NDRF medical units pre-positioned
- Mobile medical units for remote areas
- Telemedicine centers in each district
- Blood bank network across state
"""
    },
]


def create_sample_documents():
    """Create sample NDMA PDF documents."""
    docs_dir = Path(__file__).parent.parent.parent / "data" / "ndma_docs"
    docs_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("Creating Sample NDMA Protocol Documents")
    print("=" * 60)

    for doc in SAMPLE_DOCUMENTS:
        pdf_path = docs_dir / doc["filename"]

        # Create PDF
        pdf_document = fitz.open()

        # Add title page
        page = pdf_document.new_page()
        title_rect = fitz.Rect(72, 100, 540, 200)
        page.insert_textbox(
            title_rect,
            doc["title"],
            fontsize=24,
            fontname="helv",
            align=fitz.TEXT_ALIGN_CENTER,
        )

        # Add content pages
        content_lines = doc["content"].strip().split("\n")
        current_page = pdf_document.new_page()
        y_position = 50

        for line in content_lines:
            if y_position > 750:  # Start new page
                current_page = pdf_document.new_page()
                y_position = 50

            # Adjust font size for headers
            if line.strip().startswith(("Chapter", "NDMA", "NATIONAL")):
                fontsize = 14
                fontname = "helv"
            elif line.strip().startswith(("1.", "2.", "3.", "4.")):
                fontsize = 11
                fontname = "helv-Bold"
            else:
                fontsize = 10
                fontname = "helv"

            text_rect = fitz.Rect(72, y_position, 540, y_position + 20)
            try:
                current_page.insert_textbox(
                    text_rect,
                    line,
                    fontsize=fontsize,
                    fontname=fontname,
                )
            except Exception:
                # Fallback: use insert_text with default font
                current_page.insert_text(
                    fitz.Point(72, y_position + 12),
                    line,
                    fontsize=fontsize,
                )
            y_position += 18 if line.strip() else 10

        pdf_document.save(str(pdf_path))
        pdf_document.close()

        print(f"Created: {doc['filename']}")

    print("\n" + "=" * 60)
    print(f"Created {len(SAMPLE_DOCUMENTS)} sample documents in {docs_dir}")
    print("=" * 60)


if __name__ == "__main__":
    create_sample_documents()
