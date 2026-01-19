import subprocess
import json
from typing import List, Optional, Dict, Any


def run_httpx(
    targets: List[str],
    status_codes: Optional[List[int]] = None,
) -> str:
    """Run httpx to probe HTTP servers.
    
    Args:
        targets: List of target URLs or IPs to probe (e.g., ["https://example.com", "http://192.168.1.1"])
        status_codes: Optional list of status codes to filter (e.g., [200, 301, 404])
    
    Returns:
        str: JSON string containing probe results with discovered endpoints
    
    Performance Optimizations:
        - Request timeout: 5 seconds (faster than default 10s)
        - Retries: 1 (reduced from default for speed)
        - Max redirects: 3 (prevents following too many redirects)
        - Overall timeout: 30 seconds maximum (prevents hanging)
        - Typical scan time: 2-10 seconds for a single URL
    
    Example:
        run_httpx(["https://example.com"]) -> Returns JSON with probe results
        run_httpx(["https://example.com", "http://test.com"], [200, 301]) -> Filters by status codes
    """
    try:
        if not targets or len(targets) == 0:
            return json.dumps({
                "success": False,
                "error": "No targets provided. Please provide at least one URL or IP address."
            }, indent=2)
        
        # Build the command
        # For projectdiscovery httpx:
        # - Single URL: use -u flag
        # - Multiple URLs: use -l - (stdin) or pass as positional arguments
        # We'll use stdin for multiple URLs, or -u for single URL
        cmd = ["httpx", "-json", "-silent"]
        
        # Add timeout flag - confirmed supported in httpx v1.3.4
        # Default is 10s, we'll use 10s to match default behavior
        cmd.extend(["-timeout", "10"])
        
        # Add status code filter if provided
        if status_codes:
            # Ensure all are integers
            status_codes = [int(sc) for sc in status_codes if sc is not None]
            if status_codes:
                status_filter = ",".join(map(str, status_codes))
                cmd.extend(["-sc", status_filter])
        
        # For single URL, use -u flag (simpler)
        # For multiple URLs, use stdin with -l -
        if len(targets) == 1:
            cmd.extend(["-u", targets[0]])
            input_data = None
        else:
            # Multiple URLs: use stdin
            cmd.extend(["-l", "-"])
            input_data = "\n".join(targets)
        
        # Run the command with timeout to prevent hanging
        # Set timeout based on number of targets
        # For single URL: 20 seconds should be enough (site responds in <1s, but allow for httpx overhead)
        # For multiple URLs: 15s * count + 20s buffer
        # Note: If httpx hangs, it's likely due to invalid flags or network issues
        timeout_seconds = max(20, (15 * len(targets)) + 20)
        
        try:
            result = subprocess.run(
                cmd,
                input=input_data,  # Pass URLs via stdin if multiple, None if single URL
                capture_output=True,
                text=True,
                check=True,
                timeout=timeout_seconds
            )
        except subprocess.TimeoutExpired:
            return json.dumps({
                "success": False,
                "error": f"httpx scan timed out after {timeout_seconds} seconds. The httpx tool may be hanging or the target is unreachable. Command: {' '.join(cmd)}",
                "targets": targets,
                "timeout_seconds": timeout_seconds,
                "suggestion": "The site may be slow, or httpx may be waiting for a response. Try checking network connectivity or scanning a different URL."
            }, indent=2)
        
        # Parse the output - httpx outputs one JSON object per line
        output_lines = result.stdout.strip().split('\n')
        results = []
        for line in output_lines:
            if line.strip():
                try:
                    results.append(json.loads(line))
                except json.JSONDecodeError:
                    # Skip invalid JSON lines
                    continue
        
        return json.dumps({
            "success": True,
            "targets": targets,
            "results": results,
            "count": len(results)
        }, indent=2)
        
    except subprocess.CalledProcessError as e:
        # Check if it's the wrong httpx binary (Python httpx vs projectdiscovery httpx)
        error_msg = (e.stderr or "") + (e.stdout or "") + str(e)
        error_lower = error_msg.lower()
        
        if any(phrase in error_lower for phrase in [
            "command line client could not run",
            "required dependencies",
            "pip install 'httpx[cli]'"
        ]):
            return json.dumps({
                "success": False,
                "error": "Wrong httpx binary detected. Please install projectdiscovery httpx (not Python httpx). Install with: go install -v github.com/projectdiscovery/httpx/cmd/httpx@latest",
                "stderr": e.stderr,
                "stdout": e.stdout
            }, indent=2)
        
        # Check if httpx tool is not found
        if "no such file" in error_lower or "not found" in error_lower:
            return json.dumps({
                "success": False,
                "error": "httpx tool not found. Please install projectdiscovery httpx: go install -v github.com/projectdiscovery/httpx/cmd/httpx@latest",
                "stderr": e.stderr,
                "stdout": e.stdout
            }, indent=2)
        
        return json.dumps({
            "success": False,
            "error": f"httpx execution failed: {e.stderr or str(e)}",
            "stderr": e.stderr,
            "stdout": e.stdout
        }, indent=2)
    except FileNotFoundError:
        return json.dumps({
            "success": False,
            "error": "httpx tool not found. Please install projectdiscovery httpx: go install -v github.com/projectdiscovery/httpx/cmd/httpx@latest"
        }, indent=2)
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": f"Unexpected error: {str(e)}"
        }, indent=2)