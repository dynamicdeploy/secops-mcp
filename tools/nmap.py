import subprocess
import json
from typing import List, Optional, Dict, Any


def run_nmap(
    target: str,
    ports: Optional[str] = None,
    scan_type: Optional[str] = "sV",
) -> str:
    """Run an Nmap network scan on the specified target.
    
    Args:
        target: The target IP or hostname to scan
        ports: Specific ports to scan (e.g., "22,80,443")
        scan_type: Scan type options (e.g., "sV" for version detection, "sS" for SYN scan)
    
    Returns:
        str: JSON string containing scan results
    """
    try:
        # Build the command
        cmd = ["nmap", "-oX", "-", target]  # Output in XML format to stdout
        if ports:
            cmd.extend(["-p", ports])
        if scan_type:
            # Add scan type as a single flag (e.g., "sV" becomes "-sV")
            cmd.append(f"-{scan_type}")
        
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
            "target": target,
            "ports": ports,
            "scan_type": scan_type,
            "results": {
                "xml_output": result.stdout
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