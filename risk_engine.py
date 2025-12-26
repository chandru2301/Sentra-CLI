"""Risk engine that aggregates all rule checks."""
from typing import Dict, List
from diff_reader import DiffReader
from rules.sensitive_files import check_sensitive_files
from rules.cross_service import check_cross_service
from rules.infra_changes import check_infra_changes
from rules.large_diffs import check_large_diffs
from rules.test_coverage import check_test_coverage


class RiskEngine:
    """Main engine that runs all safety rules."""
    
    def __init__(self, base_branch: str = "main"):
        self.diff_reader = DiffReader(base_branch)
        self.rules = [
            ("Sensitive Files", check_sensitive_files),
            ("Cross-Service Changes", check_cross_service),
            ("Infrastructure Changes", check_infra_changes),
            ("Large Diffs", check_large_diffs),
            ("Test Coverage", check_test_coverage),
        ]
    
    def analyze(self) -> Dict:
        """Run all rules and aggregate results."""
        # Get diff data
        diff_text = self.diff_reader.get_diff()
        diff_data = self.diff_reader.parse_diff(diff_text)
        changed_files = list(diff_data.keys())
        
        if not changed_files:
            return {
                "risk": "LOW",
                "reasons": ["No changes detected"],
                "affected_areas": [],
                "recommendation": "Allow merge",
                "rule_results": []
            }
        
        # Run all rules
        rule_results = []
        all_reasons = []
        affected_areas = set()
        
        for rule_name, rule_func in self.rules:
            result = rule_func(changed_files, diff_data)
            rule_results.append({
                "name": rule_name,
                **result
            })
            
            if result["triggered"]:
                all_reasons.append(result["reason"])
                
                # Extract affected areas from file paths
                for filepath in result.get("files", [])[:5]:  # Limit to avoid noise
                    parts = filepath.split('/')
                    if len(parts) > 1:
                        # Try to identify service/area from path
                        for part in parts:
                            part_lower = part.lower()
                            if any(keyword in part_lower for keyword in ['auth', 'gateway', 'service', 'api', 'config', 'identity']):
                                affected_areas.add(part)
        
        # Calculate overall risk
        risk_levels = {"LOW": 0, "MEDIUM": 1, "HIGH": 2}
        max_risk = "LOW"
        max_risk_value = 0
        
        for result in rule_results:
            if result["triggered"]:
                risk_value = risk_levels.get(result["risk"], 0)
                if risk_value > max_risk_value:
                    max_risk_value = risk_value
                    max_risk = result["risk"]
        
        # Determine recommendation
        if max_risk == "HIGH":
            recommendation = "Block merge"
        elif max_risk == "MEDIUM":
            recommendation = "Require manual review"
        else:
            recommendation = "Allow merge"
        
        return {
            "risk": max_risk,
            "reasons": all_reasons if all_reasons else ["No issues detected"],
            "affected_areas": sorted(list(affected_areas))[:10],  # Limit to top 10
            "recommendation": recommendation,
            "rule_results": rule_results,
            "changed_files_count": len(changed_files)
        }

