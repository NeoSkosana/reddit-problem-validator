#!/usr/bin/env python
import os
import sys
from pathlib import Path

def main():
    """Run administrative tasks."""
    # Add parent directory to Python path to access our app modules
    project_root = Path(__file__).resolve().parent.parent
    sys.path.append(str(project_root))
    
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'reddit_validator.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed? Did "
            "you forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main()