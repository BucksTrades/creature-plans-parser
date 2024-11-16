# Creature Plan Parser

Tools for parsing and analyzing creature plan data.

## Installation

No special installation required beyond Python 3.6+. The scripts use only standard library modules.

## Usage

### Parse Creature Plans

Basic usage:
```bash
python parsecreature.py --input /path/to/plans/directory --output /path/to/output/directory
```

The output directory will be automatically created if it doesn't exist. For example:
```bash
# Will create a new 'results' folder in current directory
python parsecreature.py --input plans --output results

# Will create nested directories if they don't exist
python parsecreature.py --input plans --output my_project/analysis/results
```

The script will:
- Create the output directory if it doesn't exist
- Parse all JSON files in the input directory
- Generate both full and condensed versions of the parsed data
- Save results to the specified output directory

### Example Directory Structure
```
your-project/
├── parsecreature.py
├── plans/              # Your input directory
│   ├── folder1/
│   └── folder2/
└── results/            # Will be created if it doesn't exist
    ├── parsed_plans.json
    └── parsed_plans_short.json
```

### Analyze Parsed Data

```bash
python chunkanalyzer.py --input /path/to/parsed_plans_short.json --output /path/to/analysis_results.json
```

The script will:
- Analyze the condensed parsed data
- Count unique content and factors
- Save analysis results to the specified output file
- Create the output directory if it doesn't exist

## File Structure

- `parsecreature.py`: Main parser for creature plan files
- `chunkanalyzer.py`: Analyzer for parsed plan data

## Tips

- Use relative paths for easier portability (e.g., `--input plans --output results`)
- Both scripts will create any necessary output directories
- On Windows, you can use either forward slashes `/` or backslashes `\` for paths
