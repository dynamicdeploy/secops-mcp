import subprocess
import json
from typing import Optional, Dict, Any


def run_hashcat(
    hash_file: str,
    wordlist: str,
    hash_type: str = "0",  # Default to MD5
) -> str:
    """Run Hashcat to crack hashes.
    
    Args:
        hash_file: Path to file containing hashes
        wordlist: Path to wordlist file
        hash_type: Hash type as string (e.g., "0" for MD5, "1000" for NTLM, "md5", "sha1")
    
    Returns:
        str: JSON string containing cracking results
    """
    try:
        # Convert hash type string to mode number if needed
        hash_mode_map = {
            "md5": "0",
            "sha1": "100",
            "sha256": "1400",
            "sha512": "1700",
            "ntlm": "1000",
            "bcrypt": "3200"
        }
        
        mode = hash_mode_map.get(hash_type.lower(), hash_type)
        
        # Build the command
        cmd = ["hashcat", "-m", str(mode), "--potfile-disable", "--outfile-format=2", hash_file, wordlist]
        
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
            "hash_file": hash_file,
            "hash_type": hash_type,
            "mode": mode,
            "results": {
                "output": result.stdout,
                "cracked_hashes": []  # Hashcat output format 2 would be parsed here
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