#!/usr/bin/env python3
"""
Script to execute ide.py and capture the VSCode access URL.
After executing ide.py, this script will parse the output to find and display
the VSCode access URL.
"""

import subprocess
import re
import os
import sys

# Path to the ide.py file
IDE_SCRIPT_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tasks", "ide.py")

def run_ide_script():
    """
    Execute the ide.py script and capture its output.
    """
    print(f"Executing {IDE_SCRIPT_PATH}...")
    
    try:
        # Run the ide.py script and capture its output
        result = subprocess.run(
            [sys.executable, IDE_SCRIPT_PATH],
            capture_output=True,
            text=True,
            check=True
        )
        
        # Print the standard output for debugging
        print("\nOutput from ide.py:")
        print(result.stdout)
        
        # Extract the VSCode URL from the output
        url = extract_vscode_url(result.stdout)
        
        if url:
            print("\n" + "="*50)
            print(f"VSCode access URL: {url}")
            print("="*50)
        else:
            print("\nCould not find VSCode access URL in the output.")
            print("Check the full output above for any error messages or the URL format.")
        
        # If there were any errors, print them
        if result.stderr:
            print("\nErrors:")
            print(result.stderr)
            
    except subprocess.CalledProcessError as e:
        print(f"Error executing ide.py: {e}")
        print("\nStandard output:")
        print(e.stdout)
        print("\nStandard error:")
        print(e.stderr)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

def extract_vscode_url(output):
    """
    Extract the VSCode URL from the output.
    This function uses a regular expression to find URLs that look like VSCode access URLs.
    
    Args:
        output (str): The output from running ide.py
        
    Returns:
        str or None: The VSCode URL if found, None otherwise
    """
    # Common patterns for VSCode URLs
    # This regex looks for http/https URLs that might be VSCode access URLs
    url_patterns = [
        r'https?://[^\s]+vscode[^\s]*',  # URLs containing 'vscode'
        r'https?://[^\s]+code-server[^\s]*',  # URLs containing 'code-server'
        r'https?://[^\s]+/ide/[^\s]*',  # URLs containing '/ide/'
        r'https?://[^\s]+/interactive/[^\s]*',  # URLs containing '/interactive/'
        r'https?://[^\s]+:[0-9]+/[^\s]*'  # Any URL with a port number
    ]
    
    for pattern in url_patterns:
        matches = re.findall(pattern, output)
        if matches:
            return matches[0]  # Return the first match
    
    return None

if __name__ == "__main__":
    run_ide_script()