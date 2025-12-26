"""Generate formatted safety report."""
from typing import Dict


def generate_report(analysis_result: Dict) -> str:
    """Generate formatted report string."""
    risk = analysis_result["risk"]
    reasons = analysis_result["reasons"]
    affected_areas = analysis_result["affected_areas"]
    recommendation = analysis_result["recommendation"]
    
    report = []
    report.append("AI SAFETY REPORT")
    report.append("=" * 16)
    report.append("")
    report.append(f"Overall Risk: {risk}")
    report.append("")
    
    if reasons:
        report.append("Reasons:")
        for reason in reasons:
            report.append(f"- {reason}")
        report.append("")
    
    if affected_areas:
        report.append("Affected Areas:")
        for area in affected_areas:
            report.append(f"- {area}")
        report.append("")
    
    report.append("Recommendation:")
    if recommendation == "Block merge":
        report.append("[X] Block merge")
        report.append("Manual review required.")
    elif recommendation == "Require manual review":
        report.append("[!] Require manual review")
    else:
        report.append("[OK] Allow merge")
    
    return "\n".join(report)

