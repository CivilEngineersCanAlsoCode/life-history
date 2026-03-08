# Execution Scripts

This folder contains **deterministic Python scripts** that handle the actual work.

## Purpose
Execution scripts handle:
- API calls
- Data processing
- File operations
- Database interactions

## Guidelines
1. **Check before creating**: Always check if a script already exists before writing a new one
2. **Well-commented**: Include clear comments explaining the logic
3. **Testable**: Write scripts that can be easily tested
4. **Environment variables**: Use `.env` for sensitive configuration

## Example Script Structure
```python
#!/usr/bin/env python3
"""
Script Name: example_script.py
Purpose: Brief description of what this script does

Usage:
    python example_script.py --input data.json --output result.json
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def main():
    # Your logic here
    pass

if __name__ == "__main__":
    main()
```
