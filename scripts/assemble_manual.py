#!/usr/bin/env python3
"""
assemble_manual.py
------------------
Compiles the complete 100-Question Defense & Architecture Manual
from modular section generators.
"""

from pathlib import Path
from scripts.manual_sections.part1_architecture import get_part1
from scripts.manual_sections.part2_questions_1_to_25 import get_part2_1
from scripts.manual_sections.part2_questions_26_to_50 import get_part2_2
from scripts.manual_sections.part2_questions_51_to_75 import get_part2_3
from scripts.manual_sections.part2_questions_76_to_100 import get_part2_4
from scripts.manual_sections.part3_roadmap import get_part3

REPO_TARGET = Path("/home/tanmay/.gemini/antigravity-cli/scratch/satquery-ai/TECHNICAL_ARCHITECTURE_AND_DEFENSE_MANUAL.md")
BRAIN_TARGET = Path("/home/tanmay/.gemini/antigravity-cli/brain/3a189ecd-c0f2-43ff-8f0b-c2cdb7d49934/technical_architecture_and_defense_manual.md")

def assemble():
    print("Gathering sections...")
    p1 = get_part1()
    p2_1 = get_part2_1()
    p2_2 = get_part2_2()
    p2_3 = get_part2_3()
    p2_4 = get_part2_4()
    p3 = get_part3()
    
    full_doc = "\n\n".join([p1, p2_1, p2_2, p2_3, p2_4, p3])
    
    print(f"Total compiled document size: {len(full_doc):,} characters ({len(full_doc.split()):,} words)")
    
    REPO_TARGET.write_text(full_doc, encoding="utf-8")
    print(f"Written to repo target: {REPO_TARGET}")
    
    BRAIN_TARGET.parent.mkdir(parents=True, exist_ok=True)
    BRAIN_TARGET.write_text(full_doc, encoding="utf-8")
    print(f"Written to brain artifact target: {BRAIN_TARGET}")

if __name__ == "__main__":
    assemble()
