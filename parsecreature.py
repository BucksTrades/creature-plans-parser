import json
import os
import argparse
from datetime import datetime
from typing import List, Dict, Tuple
from dataclasses import dataclass
from pathlib import Path

@dataclass
class ThoughtData:
    timestamp: datetime
    content: str
    real_time_factors: List[str]
    relevance_score: float
    confidence_score: float

class CreaturePlanParser:
    def __init__(self, plans_directory: str, output_directory: str):
        self.plans_directory = Path(plans_directory)
        self.output_directory = Path(output_directory)
        self.output_directory.mkdir(exist_ok=True)
        
        # Define content to exclude
        self.excluded_content = [
            "Exploring system dynamics and adaptation patterns",
            "plan_"  # This will match any content containing "plan_"
        ]
    
    # [Rest of the CreaturePlanParser class remains the same]
    def should_exclude_content(self, content: str) -> bool:
        """Check if content should be excluded"""
        return any(excluded in content for excluded in self.excluded_content)
    
    def parse_timestamp(self, timestamp_str: str) -> datetime:
        """Parse timestamp with nanosecond precision"""
        if '.' in timestamp_str:
            main_part, fractional = timestamp_str.split('.')
            fractional = fractional.replace('Z', '')[:6]
            timestamp_str = f"{main_part}.{fractional}Z"
        return datetime.strptime(timestamp_str, "%Y-%m-%dT%H:%M:%S.%fZ")
    
    def parse_single_plan(self, plan_path: Path) -> Dict:
        """Parse a single plan JSON file"""
        try:
            with open(plan_path, 'r', encoding='utf-8') as f:
                plan_data = json.load(f)
                
            thoughts = []
            for thought in plan_data.get("thoughts", []):
                # Skip thoughts with excluded content
                if self.should_exclude_content(thought["content"].strip()):
                    continue
                    
                try:
                    thought_data = ThoughtData(
                        timestamp=self.parse_timestamp(thought["timestamp"]),
                        content=thought["content"].strip(),
                        real_time_factors=thought["real_time_factors"],
                        relevance_score=thought["relevance_score"],
                        confidence_score=thought["confidence_score"]
                    )
                    thoughts.append(thought_data)
                except Exception as e:
                    print(f"Error processing thought in {plan_path.name}: {str(e)}")
                    continue
                
            # Sort thoughts by timestamp
            thoughts.sort(key=lambda x: x.timestamp)
            
            # Only return if there are thoughts after filtering
            if thoughts:
                return {
                    "plan_id": plan_data.get("id"),
                    "folder": plan_path.parent.name,
                    "file_name": plan_path.name,
                    "thoughts": [
                        {
                            "timestamp": str(t.timestamp),
                            "content": t.content,
                            "real_time_factors": t.real_time_factors,
                            "relevance_score": t.relevance_score,
                            "confidence_score": t.confidence_score
                        }
                        for t in thoughts
                    ]
                }
            else:
                return None
            
        except Exception as e:
            print(f"Error processing file {plan_path}: {str(e)}")
            return None

    def create_condensed_output(self, all_plans: Dict) -> List[Dict]:
        """Create a minimal version with just content and real_time_factors as a flat list"""
        condensed = []
        
        for dir_plans in all_plans["plans"].values():
            for plan_data in dir_plans.values():
                for thought in plan_data["thoughts"]:
                    if thought["content"].strip() != "Exploring system dynamics and adaptation patterns":
                        thought_data = {
                            "c": thought["content"].strip(),
                            "r": thought["real_time_factors"]
                        }
                        condensed.append(thought_data)
                
        return condensed

    def parse_all_plans(self) -> Tuple[Dict, Dict]:
        """Parse all JSON files and create both full and condensed outputs"""
        all_plans = {}
        errors = []

        try:
            directories = [d for d in self.plans_directory.iterdir() if d.is_dir()]
            directories.sort(key=lambda x: int(x.name))
            
            print(f"Found {len(directories)} directories")
            
            for dir_path in directories:
                print(f"\nProcessing directory: {dir_path.name}")
                dir_plans = {}
                
                json_files = list(dir_path.glob('*.json'))
                print(f"Found {len(json_files)} JSON files")
                
                for file_path in json_files:
                    try:
                        print(f"Processing file: {file_path.name}")
                        plan_data = self.parse_single_plan(file_path)
                        if plan_data is not None:
                            dir_plans[file_path.name] = plan_data
                    except Exception as e:
                        error_msg = f"Error processing {file_path}: {str(e)}"
                        print(error_msg)
                        errors.append(error_msg)
                
                if dir_plans:
                    all_plans[dir_path.name] = dir_plans
                
        except Exception as e:
            errors.append(f"Directory error: {str(e)}")
        
        results = {
            "plans": all_plans,
            "metadata": {
                "total_directories": len(all_plans),
                "total_plans": sum(len(plans) for plans in all_plans.values()),
                "base_directory": str(self.plans_directory),
                "processed_at": datetime.now().isoformat()
            },
            "errors": errors
        }
        
        # Create condensed version
        condensed_results = self.create_condensed_output(results)
        
        return results, condensed_results

def main():
    parser = argparse.ArgumentParser(description='Parse creature plan files.')
    parser.add_argument('--input', '-i', type=str, required=True,
                      help='Input directory containing plan folders')
    parser.add_argument('--output', '-o', type=str, required=True,
                      help='Output directory for parsed results')
    
    args = parser.parse_args()
    
    # Convert to absolute paths
    plans_dir = Path(args.input).absolute()
    output_dir = Path(args.output).absolute()
    
    parser = CreaturePlanParser(plans_dir, output_dir)
    
    print("Starting plan parsing...")
    full_results, condensed_results = parser.parse_all_plans()
    
    # Save full results
    output_file = output_dir / "parsed_plans.json"
    print(f"\nSaving full results to {output_file}")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(full_results, f, indent=2, default=str)
    
    # Save condensed results with readable formatting
    condensed_file = output_dir / "parsed_plans_short.json"
    print(f"Saving condensed results to {condensed_file}")
    with open(condensed_file, 'w', encoding='utf-8') as f:
        # Use indent=1 for compact but readable format
        json.dump(condensed_results, f, indent=1)
        
    print("\nProcessing complete!")
    print(f"Total directories processed: {full_results['metadata']['total_directories']}")
    print(f"Total plans processed: {full_results['metadata']['total_plans']}")
    
    if full_results['errors']:
        print("\nErrors encountered:")
        for error in full_results['errors']:
            print(f"- {error}")

if __name__ == "__main__":
    main()