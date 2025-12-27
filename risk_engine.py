"""Risk engine that aggregates all rule checks."""
from typing import Dict, List
from diff_reader import DiffReader
from rules.sensitive_files import check_sensitive_files
from rules.cross_service import check_cross_service
from rules.infra_changes import check_infra_changes
from rules.large_diffs import check_large_diffs
from rules.test_coverage import check_test_coverage
from ai_escalator import ai_escalate, is_ai_enabled


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
    
    def analyze(self, policy: Dict = None) -> Dict:
        """Run all rules and aggregate results."""
        # Get diff data
        diff_text = self.diff_reader.get_diff()
        diff_data = self.diff_reader.parse_diff(diff_text)
        changed_files = list(diff_data.keys())
        
        if not changed_files:
            return {
                "rules": [],
                "affected_areas": [],
                "changed_files_count": 0,
                "base_branch": self.diff_reader.base_branch,
                "ai_escalation_enabled": is_ai_enabled(),
                "policy": policy
            }
        
        # Run all rules
        rule_results = []
        affected_areas = set()
        
        for rule_name, rule_func in self.rules:
            result = rule_func(changed_files, diff_data)
            rule_results.append(result)
            
            if result["triggered"]:
                # Extract affected areas from file paths
                for filepath in result.get("files", [])[:5]:  # Limit to avoid noise
                    parts = filepath.split('/')
                    if len(parts) > 1:
                        # Try to identify service/area from path
                        for part in parts:
                            part_lower = part.lower()
                            if any(keyword in part_lower for keyword in ['auth', 'gateway', 'service', 'api', 'config', 'identity']):
                                affected_areas.add(part)
        
        # Apply AI escalation ONLY to MEDIUM severity rules
        # Hard cap to prevent cost explosions (max 5 escalations per scan)
        MAX_AI_ESCALATIONS = 5
        ai_escalation_count = 0
        
        for rule in rule_results:
            if rule["triggered"] and rule["severity"] == "MEDIUM":
                if ai_escalation_count >= MAX_AI_ESCALATIONS:
                    break
                escalation = ai_escalate(rule["message"])
                
                if escalation:
                    rule["severity"] = escalation
                    rule["ai_escalated"] = True
                ai_escalation_count += 1
        
        return {
            "rules": rule_results,
            "affected_areas": sorted(list(affected_areas))[:10],  # Limit to top 10
            "changed_files_count": len(changed_files),
            "base_branch": self.diff_reader.base_branch,
            "ai_escalation_enabled": is_ai_enabled(),
            "policy": policy
        }

