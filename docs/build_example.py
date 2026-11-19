"""Rebuild all synthetic SOC 2 example artifacts, including the PDF."""
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
SKILL=ROOT/'skills/soc2-engineering-guardian'
sys.path.insert(0,str(SKILL/'scripts'))
from common import load
from render_report import render
from export_tasks import export
assessment=load(SKILL/'assets/assessment-example.json')
render(assessment,Path(__file__).parent/'example',True)
export(assessment,Path(__file__).parent/'example')
print('Rebuilt synthetic SOC 2 reports and tasks')
