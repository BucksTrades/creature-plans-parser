import json
import argparse
from pathlib import Path
from typing import Dict, List, Generator
from collections import Counter

class ContentAnalyzer:
    def __init__(self, input_file: Path):
        self.input_file = input_file
        self.content_counter = Counter()
        self.factor_counter = Counter()
    
    def analyze_file(self):
        """Analyze the entire file for unique content and factors"""
        print("Reading and analyzing file...")
        
        with open(self.input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        for thought in data:
            # Count unique content
            self.content_counter[thought["c"].strip()] += 1
            
            # Count unique factors
            for factor in thought["r"]:
                self.factor_counter[factor.strip()] += 1
    
    def save_results(self, output_file: Path):
        """Save the analysis results"""
        results = {
            "content_counts": dict(sorted(self.content_counter.items(), key=lambda x: x[1], reverse=True)),
            "factor_counts": dict(sorted(self.factor_counter.items(), key=lambda x: x[1], reverse=True))
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=1)
        
        # Print summary
        print("\nAnalysis Summary:")
        print(f"Total unique content entries: {len(self.content_counter)}")
        print(f"Total unique factors: {len(self.factor_counter)}")

def main():
    parser = argparse.ArgumentParser(description='Analyze parsed creature plans content.')
    parser.add_argument('--input', '-i', type=str, required=True,
                      help='Input JSON file (parsed_plans_short.json)')
    parser.add_argument('--output', '-o', type=str, required=True,
                      help='Output JSON file for analysis results')
    
    args = parser.parse_args()
    
    input_file = Path(args.input).absolute()
    output_file = Path(args.output).absolute()
    
    analyzer = ContentAnalyzer(input_file)
    analyzer.analyze_file()
    analyzer.save_results(output_file)

if __name__ == "__main__":
    main()