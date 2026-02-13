"""
Command-line interface for the v2.0 → v2.1 converter.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Optional

from .converter import convert_v2_to_v21, convert_batch


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Convert Beckn v2.0 payloads to v2.1 format",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Convert a single file
  python -m v2_to_v21_converter.cli convert input.json -o output.json
  
  # Convert with verbose output
  python -m v2_to_v21_converter.cli convert input.json -o output.json -v
  
  # Convert multiple files
  python -m v2_to_v21_converter.cli batch inputs/*.json -o outputs/
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Convert command
    convert_parser = subparsers.add_parser("convert", help="Convert a single v2.0 payload")
    convert_parser.add_argument("input", type=Path, help="Input v2.0 JSON file")
    convert_parser.add_argument("-o", "--output", type=Path, required=True, help="Output v2.1 JSON file")
    convert_parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output with report")
    convert_parser.add_argument("--strict", action="store_true", help="Fail on any warnings")
    convert_parser.add_argument("--report", type=Path, help="Save conversion report to file")
    
    # Batch command
    batch_parser = subparsers.add_parser("batch", help="Convert multiple v2.0 payloads")
    batch_parser.add_argument("inputs", type=Path, nargs="+", help="Input v2.0 JSON files")
    batch_parser.add_argument("-o", "--output-dir", type=Path, required=True, help="Output directory")
    batch_parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    batch_parser.add_argument("--continue-on-error", action="store_true", default=True, help="Continue on errors")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    if args.command == "convert":
        return handle_convert(args)
    elif args.command == "batch":
        return handle_batch(args)


def handle_convert(args):
    """Handle single file conversion"""
    try:
        # Read input
        with open(args.input, 'r') as f:
            v2_payload = json.load(f)
        
        # Convert
        result = convert_v2_to_v21(v2_payload, strict=args.strict)
        
        # Write output
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with open(args.output, 'w') as f:
            json.dump(result.converted_payload, f, indent=2)
        
        # Print report if verbose
        if args.verbose:
            print(result.report.summary())
        else:
            print(f"✓ Converted {args.input} → {args.output}")
            if result.report.warnings:
                print(f"  ⚠ {len(result.report.warnings)} warnings (use -v for details)")
        
        # Save report if requested
        if args.report:
            with open(args.report, 'w') as f:
                json.dump(result.report.to_dict(), f, indent=2)
            print(f"  Report saved to {args.report}")
        
        return 0
    
    except Exception as e:
        print(f"✗ Error: {e}", file=sys.stderr)
        return 1


def handle_batch(args):
    """Handle batch conversion"""
    try:
        # Read all inputs
        payloads = []
        for input_file in args.inputs:
            with open(input_file, 'r') as f:
                payloads.append((input_file, json.load(f)))
        
        # Convert
        print(f"Converting {len(payloads)} files...")
        results = convert_batch([p[1] for p in payloads], args.continue_on_error)
        
        # Write outputs
        args.output_dir.mkdir(parents=True, exist_ok=True)
        
        success_count = 0
        error_count = 0
        
        for (input_file, _), result in zip(payloads, results):
            output_file = args.output_dir / input_file.name
            
            if result.converted_payload:
                with open(output_file, 'w') as f:
                    json.dump(result.converted_payload, f, indent=2)
                success_count += 1
                
                if args.verbose:
                    print(f"\n✓ {input_file.name}")
                    print(result.report.summary())
                else:
                    print(f"✓ {input_file.name} → {output_file.name}")
            else:
                error_count += 1
                print(f"✗ {input_file.name}: Conversion failed", file=sys.stderr)
                if args.verbose:
                    print(result.report.summary())
        
        print(f"\nComplete: {success_count} succeeded, {error_count} failed")
        return 0 if error_count == 0 else 1
    
    except Exception as e:
        print(f"✗ Batch error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
