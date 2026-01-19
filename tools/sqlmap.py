import subprocess
import json
from typing import List, Optional, Dict, Any


def run_sqlmap(
    url: str,
    risk: Optional[int] = 1,
    level: Optional[int] = 1,
) -> str:
    """Run sqlmap to test for SQL injection vulnerabilities.
    
    Args:
        url: Target URL to scan
        risk: Risk level (1-3, default: 1)
        level: Test level (1-5, default: 1)
    
    Returns:
        str: JSON string containing scan results
    """
    try:
        # Build the command
        cmd = ["sqlmap", "-u", url, "--batch", "--output-dir=/tmp/sqlmap"]
        if risk:
            cmd.extend(["--risk", str(risk)])
        if level:
            cmd.extend(["--level", str(level)])
        
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
            "risk": risk,
            "level": level,
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