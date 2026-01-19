import subprocess
import json
from typing import List, Optional, Dict, Any


def run_xsstrike(
    url: str,
    crawl: bool = False,
) -> str:
    """Run XSStrike to detect XSS vulnerabilities.
    
    Args:
        url: Target URL to scan
        crawl: Whether to crawl the website for more URLs
    
    Returns:
        str: JSON string containing scan results
    """
    try:
        # Build the command
        cmd = ["xsstrike", "-u", url]
        if crawl:
            cmd.append("--crawl")
        
        # Run the command
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )
        
        # Parse the output
        return json.dumps({
            "success": True,
            "url": url,
            "crawl": crawl,
            "results": {
                "output": result.stdout
            }
        })
        
    except subprocess.CalledProcessError as e:
        return json.dumps({
            "success": False,
            "error": str(e),
            "stderr": e.stderr
        })
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": str(e)
        })