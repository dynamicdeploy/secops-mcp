import subprocess
import json
from typing import Optional, Dict, Any


def run_subfinder(
    domain: str,
    recursive: bool = False,
) -> str:
    """Run subfinder to enumerate subdomains.
    
    Args:
        domain: Target domain to enumerate
        recursive: Whether to perform recursive enumeration
    
    Returns:
        str: JSON string containing enumeration results
    """
    try:
        # Build the command
        cmd = ["subfinder", "-d", domain, "-json"]
        if recursive:
            cmd.append("-recursive")
        
        # Run the command
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )
        
        # Parse the output - subfinder outputs one JSON object per line
        subdomains = []
        for line in result.stdout.strip().split('\n'):
            if line.strip():
                try:
                    data = json.loads(line)
                    subdomains.append(data)
                except json.JSONDecodeError:
                    continue
        
        return json.dumps({
            "success": True,
            "domain": domain,
            "recursive": recursive,
            "subdomains": subdomains,
            "count": len(subdomains)
        }, indent=2)
        
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