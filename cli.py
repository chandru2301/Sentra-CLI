"""CLI entry point for ai-safety."""
import sys
import argparse
from risk_engine import RiskEngine
from report import generate_report
from exit_codes import get_exit_code


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="AI Safety - Analyze git diffs for PR safety"
    )
    parser.add_argument(
        "command",
        choices=["scan"],
        help="Command to execute"
    )
    parser.add_argument(
        "--base",
        default="main",
        help="Base branch to compare against (default: main)"
    )
    parser.add_argument(
        "--fail-on",
        choices=["high", "medium", "low"],
        help="Exit with code 2 if risk is at or above this level"
    )
    
    args = parser.parse_args()
    
    if args.command == "scan":
        try:
            engine = RiskEngine(base_branch=args.base)
            result = engine.analyze()
            
            # Generate and print report
            report = generate_report(result)
            print(report)
            
            # Determine exit code
            risk_level = result["risk"]
            exit_code = get_exit_code(risk_level)
            
            # Override exit code if --fail-on is specified
            if args.fail_on:
                fail_mapping = {"high": "HIGH", "medium": "MEDIUM", "low": "LOW"}
                fail_level = fail_mapping[args.fail_on]
                risk_mapping = {"LOW": 0, "MEDIUM": 1, "HIGH": 2}
                
                if risk_mapping[risk_level] >= risk_mapping[fail_level]:
                    exit_code = 2
            
            sys.exit(exit_code)
            
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    main()

