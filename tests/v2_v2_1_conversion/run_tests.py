#!/usr/bin/env python3
"""
Test Runner for v2.0 to v2.1 Conversion
Reads test_config.yaml and executes transformation tests with detailed reporting
"""

import sys
import yaml
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Tuple

# Add converter directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts" / "v2.1" / "v2_to_v21_converter"))

from becknVersionTransform import IRITransformer
from becknSemanticTransform import SemanticTransformer


class Colors:
    """ANSI color codes for terminal output"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'


class TestRunner:
    """Test runner for v2 to v2.1 conversion"""
    
    def __init__(self, config_path: str):
        """Initialize test runner with config file"""
        self.config_path = Path(config_path)
        self.base_dir = self.config_path.parent.parent.parent
        self.config = self.load_config()
        self.results = []
        
    def load_config(self) -> Dict[str, Any]:
        """Load test configuration from YAML"""
        with open(self.config_path, 'r') as f:
            return yaml.safe_load(f)
    
    def resolve_path(self, rel_path: str) -> Path:
        """Resolve relative path from project root"""
        return self.base_dir / rel_path
    
    def load_json(self, path: Path) -> Dict[str, Any]:
        """Load JSON file"""
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def deep_compare(self, obj1: Any, obj2: Any, path: str = "root") -> List[Dict[str, Any]]:
        """Deep comparison of two objects, returns list of differences"""
        diffs = []
        
        if type(obj1) != type(obj2):
            diffs.append({
                "path": path,
                "type": "type_mismatch",
                "expected": str(type(obj1).__name__),
                "actual": str(type(obj2).__name__),
                "expected_value": obj1,
                "actual_value": obj2
            })
            return diffs
        
        if isinstance(obj1, dict):
            all_keys = set(obj1.keys()) | set(obj2.keys())
            for key in sorted(all_keys):
                new_path = f"{path}.{key}"
                
                if key not in obj1:
                    diffs.append({
                        "path": new_path,
                        "type": "missing_in_expected",
                        "expected": None,
                        "actual": obj2[key]
                    })
                elif key not in obj2:
                    diffs.append({
                        "path": new_path,
                        "type": "missing_in_actual",
                        "expected": obj1[key],
                        "actual": None
                    })
                else:
                    diffs.extend(self.deep_compare(obj1[key], obj2[key], new_path))
        
        elif isinstance(obj1, list):
            if len(obj1) != len(obj2):
                diffs.append({
                    "path": f"{path}[length]",
                    "type": "length_mismatch",
                    "expected": len(obj1),
                    "actual": len(obj2)
                })
            
            for i in range(min(len(obj1), len(obj2))):
                new_path = f"{path}[{i}]"
                diffs.extend(self.deep_compare(obj1[i], obj2[i], new_path))
        
        else:
            if obj1 != obj2:
                diffs.append({
                    "path": path,
                    "type": "value_mismatch",
                    "expected": obj1,
                    "actual": obj2
                })
        
        return diffs
    
    def validate_fields(self, data: Dict[str, Any], validations: Dict[str, List[Dict]]) -> List[Dict[str, Any]]:
        """Validate specific fields exist in transformed data"""
        validation_results = []
        
        for validation_name, checks in validations.items():
            for check in checks:
                path = check['path']
                required = check.get('required', False)
                field_type = check.get('type')
                
                # Navigate to field
                parts = path.split('.')
                current = data
                found = True
                
                try:
                    for part in parts:
                        current = current[part]
                except (KeyError, TypeError):
                    found = False
                    current = None
                
                validation_results.append({
                    "validation": validation_name,
                    "path": path,
                    "description": check.get('description', ''),
                    "required": required,
                    "found": found,
                    "value": current,
                    "expected_type": field_type,
                    "actual_type": type(current).__name__ if current is not None else None,
                    "passed": found if required else True
                })
        
        return validation_results
    
    def run_transformation(self, scenario: Dict[str, Any]) -> Tuple[Dict[str, Any], List[str], Dict[str, int]]:
        """Run transformation for a scenario"""
        mode = scenario.get('mode', self.config['default_mode'])
        input_path = self.resolve_path(scenario['input'])
        
        # Load input
        input_data = self.load_json(input_path)
        
        # Get ontology files
        ontology = self.config['ontology_files']
        context_file = str(self.resolve_path(ontology['context_jsonld']))
        vocab_file = str(self.resolve_path(ontology['vocab_jsonld']))
        attributes_file = str(self.resolve_path(ontology['attributes_yaml']))
        
        # Transform based on mode
        if mode == "hybrid":
            rules_file = str(self.resolve_path(self.config['transformation_rules']['structural_rules']))
            
            transformer = IRITransformer(
                output_version=self.config['default_output_version'],
                context_file=context_file,
                vocab_file=vocab_file,
                attributes_file=attributes_file,
                structural_rules_file=rules_file
            )
            
            transformed, warnings, stats, applied_rules = transformer.transform_and_validate(input_data)
            if applied_rules:
                stats['applied_structural_rules'] = applied_rules
        
        else:  # semantic mode
            transformer = SemanticTransformer(
                output_version=self.config['default_output_version'],
                context_file=context_file,
                vocab_file=vocab_file,
                attributes_file=attributes_file
            )
            
            transformed, warnings, stats = transformer.transform(input_data)
        
        # Remove metadata if configured
        if not self.config['test_settings'].get('include_metadata', False):
            transformed.pop('_transformation_warnings', None)
            transformed.pop('_transformation_stats', None)
        
        return transformed, warnings, stats
    
    def run_scenario(self, scenario: Dict[str, Any]) -> Dict[str, Any]:
        """Run a single test scenario"""
        print(f"\n{Colors.BOLD}Running: {scenario['name']}{Colors.END}")
        print(f"Description: {scenario['description']}")
        print(f"Mode: {scenario['mode']}")
        
        result = {
            "name": scenario['name'],
            "mode": scenario['mode'],
            "timestamp": datetime.now().isoformat(),
            "passed": False,
            "differences": [],
            "validations": [],
            "warnings": [],
            "stats": {}
        }
        
        try:
            # Run transformation
            print("Transforming...")
            transformed, warnings, stats = self.run_transformation(scenario)
            
            result['warnings'] = warnings
            result['stats'] = stats
            
            # Load expected output
            expected_path = self.resolve_path(scenario['expected'])
            expected_data = self.load_json(expected_path)
            
            # Compare
            print("Comparing with expected output...")
            diffs = self.deep_compare(expected_data, transformed)
            result['differences'] = diffs
            
            # Validate specific fields
            if 'validation_fields' in self.config:
                print("Validating fields...")
                validations = self.validate_fields(transformed, self.config['validation_fields'])
                result['validations'] = validations
            
            # Determine if test passed
            result['passed'] = len(diffs) == 0
            
            # Print results
            if result['passed']:
                print(f"{Colors.GREEN}✓ PASSED{Colors.END}")
            else:
                print(f"{Colors.RED}✗ FAILED - {len(diffs)} differences found{Colors.END}")
                
                # Show first few differences
                for diff in diffs[:5]:
                    print(f"  {Colors.YELLOW}•{Colors.END} {diff['type']} at {diff['path']}")
                
                if len(diffs) > 5:
                    print(f"  ... and {len(diffs) - 5} more differences")
            
            # Print validation results
            if result['validations']:
                failed_validations = [v for v in result['validations'] if not v['passed']]
                if failed_validations:
                    print(f"{Colors.YELLOW}Field Validations:{Colors.END}")
                    for v in failed_validations:
                        print(f"  {Colors.RED}✗{Colors.END} {v['validation']}: {v['description']}")
            
            # Save transformed output
            if self.config['test_settings'].get('output_directory'):
                output_dir = self.resolve_path(self.config['test_settings']['output_directory'])
                output_dir.mkdir(parents=True, exist_ok=True)
                
                output_file = output_dir / f"{scenario['name'].replace(' ', '_')}_output.json"
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(transformed, f, indent=2, ensure_ascii=False)
                
                result['output_file'] = str(output_file)
                print(f"Output saved to: {output_file}")
        
        except Exception as e:
            result['error'] = str(e)
            print(f"{Colors.RED}✗ ERROR: {str(e)}{Colors.END}")
            import traceback
            if self.config['test_settings'].get('verbose'):
                traceback.print_exc()
        
        return result
    
    def generate_report(self):
        """Generate HTML test report"""
        if not self.config['test_settings'].get('generate_diff_report'):
            return
        
        output_dir = self.resolve_path(self.config['test_settings']['output_directory'])
        output_dir.mkdir(parents=True, exist_ok=True)
        
        report_path = output_dir / f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        
        passed_count = sum(1 for r in self.results if r.get('passed'))
        failed_count = len(self.results) - passed_count
        
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>v2 to v2.1 Conversion Test Report</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: #f5f5f5;
        }}
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        h1 {{ color: #333; border-bottom: 3px solid #4CAF50; padding-bottom: 10px; }}
        .summary {{
            background: #e3f2fd;
            padding: 20px;
            border-radius: 5px;
            margin: 20px 0;
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
        }}
        .stat {{
            text-align: center;
        }}
        .stat-value {{
            font-size: 2em;
            font-weight: bold;
        }}
        .stat-label {{
            color: #666;
            margin-top: 5px;
        }}
        .passed {{ color: #4CAF50; }}
        .failed {{ color: #f44336; }}
        .scenario {{
            border: 1px solid #ddd;
            border-radius: 5px;
            margin: 20px 0;
            padding: 20px;
        }}
        .scenario.passed {{
            border-left: 4px solid #4CAF50;
            background: #f1f8f4;
        }}
        .scenario.failed {{
            border-left: 4px solid #f44336;
            background: #fef5f5;
        }}
        .scenario h2 {{
            margin-top: 0;
        }}
        .diff-item {{
            background: #fff3cd;
            border-left: 3px solid #ffc107;
            padding: 10px;
            margin: 10px 0;
            border-radius: 3px;
        }}
        .validation {{
            padding: 10px;
            margin: 5px 0;
            border-radius: 3px;
        }}
        .validation.passed {{
            background: #d4edda;
            border-left: 3px solid #28a745;
        }}
        .validation.failed {{
            background: #f8d7da;
            border-left: 3px solid #dc3545;
        }}
        pre {{
            background: #f4f4f4;
            padding: 10px;
            border-radius: 3px;
            overflow-x: auto;
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }}
        .stat-card {{
            background: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
            border-left: 3px solid #007bff;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🧪 v2 to v2.1 Conversion Test Report</h1>
        
        <div class="summary">
            <div class="stat">
                <div class="stat-value">{len(self.results)}</div>
                <div class="stat-label">Total Tests</div>
            </div>
            <div class="stat">
                <div class="stat-value passed">{passed_count}</div>
                <div class="stat-label">Passed</div>
            </div>
            <div class="stat">
                <div class="stat-value failed">{failed_count}</div>
                <div class="stat-label">Failed</div>
            </div>
            <div class="stat">
                <div class="stat-value">{datetime.now().strftime('%Y-%m-%d %H:%M')}</div>
                <div class="stat-label">Generated</div>
            </div>
        </div>
"""
        
        for result in self.results:
            status = "passed" if result.get('passed') else "failed"
            status_symbol = "✓" if result.get('passed') else "✗"
            
            html += f"""
        <div class="scenario {status}">
            <h2>{status_symbol} {result['name']}</h2>
            <p><strong>Mode:</strong> {result['mode']}</p>
            <p><strong>Timestamp:</strong> {result['timestamp']}</p>
"""
            
            if result.get('error'):
                html += f"""
            <div class="diff-item">
                <strong>Error:</strong><br>
                <pre>{result['error']}</pre>
            </div>
"""
            
            if result.get('differences'):
                html += f"""
            <h3>Differences ({len(result['differences'])})</h3>
"""
                for diff in result['differences'][:20]:  # Show first 20
                    html += f"""
            <div class="diff-item">
                <strong>Path:</strong> {diff['path']}<br>
                <strong>Type:</strong> {diff['type']}<br>
                <strong>Expected:</strong> <code>{json.dumps(diff.get('expected'), ensure_ascii=False)[:200]}</code><br>
                <strong>Actual:</strong> <code>{json.dumps(diff.get('actual'), ensure_ascii=False)[:200]}</code>
            </div>
"""
                if len(result['differences']) > 20:
                    html += f"<p>... and {len(result['differences']) - 20} more differences</p>"
            
            if result.get('validations'):
                html += "<h3>Field Validations</h3>"
                for v in result['validations']:
                    v_status = "passed" if v['passed'] else "failed"
                    v_symbol = "✓" if v['passed'] else "✗"
                    html += f"""
            <div class="validation {v_status}">
                {v_symbol} <strong>{v['validation']}</strong>: {v['description']}<br>
                Path: {v['path']} - Found: {v['found']}
            </div>
"""
            
            if result.get('stats'):
                html += """
            <h3>Transformation Statistics</h3>
            <div class="stats-grid">
"""
                for key, value in result['stats'].items():
                    html += f"""
                <div class="stat-card">
                    <strong>{key.replace('_', ' ').title()}:</strong> {value}
                </div>
"""
                html += """
            </div>
"""
            
            if result.get('warnings'):
                html += f"""
            <h3>Warnings ({len(result['warnings'])})</h3>
            <ul>
"""
                for warning in result['warnings'][:10]:
                    html += f"<li>{warning}</li>"
                if len(result['warnings']) > 10:
                    html += f"<li>... and {len(result['warnings']) - 10} more warnings</li>"
                html += "</ul>"
            
            html += "\n        </div>\n"
        
        html += """
    </div>
</body>
</html>
"""
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(html)
        
        print(f"\n{Colors.BLUE}📊 HTML Report generated: {report_path}{Colors.END}")
    
    def run_all(self):
        """Run all enabled test scenarios"""
        print(f"\n{Colors.BOLD}{'='*60}{Colors.END}")
        print(f"{Colors.BOLD}Beckn Protocol v2 to v2.1 Conversion Tests{Colors.END}")
        print(f"{Colors.BOLD}{'='*60}{Colors.END}")
        
        scenarios = [s for s in self.config.get('test_scenarios', []) if s.get('enabled', True)]
        
        print(f"\nFound {len(scenarios)} enabled test scenario(s)")
        
        for scenario in scenarios:
            result = self.run_scenario(scenario)
            self.results.append(result)
        
        # Summary
        print(f"\n{Colors.BOLD}{'='*60}{Colors.END}")
        print(f"{Colors.BOLD}Test Summary{Colors.END}")
        print(f"{Colors.BOLD}{'='*60}{Colors.END}")
        
        passed = sum(1 for r in self.results if r.get('passed'))
        failed = len(self.results) - passed
        
        print(f"Total: {len(self.results)}")
        print(f"{Colors.GREEN}Passed: {passed}{Colors.END}")
        print(f"{Colors.RED}Failed: {failed}{Colors.END}")
        
        # Generate report
        self.generate_report()
        
        return failed == 0


def main():
    """Main entry point"""
    config_file = Path(__file__).parent / "test_config.yaml"
    
    if not config_file.exists():
        print(f"{Colors.RED}Error: Configuration file not found: {config_file}{Colors.END}")
        sys.exit(1)
    
    runner = TestRunner(str(config_file))
    success = runner.run_all()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
