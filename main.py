import json
from typing import List, Optional

from mcp.server.fastmcp import FastMCP

from tools.nuclei import run_nuclei
from tools.ffuf import run_ffuf
from tools.wfuzz import run_wfuzz
from tools.sqlmap import run_sqlmap
from tools.nmap import run_nmap
from tools.hashcat import run_hashcat
from tools.httpx import run_httpx
from tools.subfinder import run_subfinder
from tools.tlsx import run_tlsx
from tools.xsstrike import run_xsstrike
from tools.ipinfo import run_ipinfo
from tools.amass import amass_wrapper as amass_tool
from tools.dirsearch import dirsearch_wrapper as dirsearch_tool
from tools.gospider import gospider_wrapper, gospider_crawl_with_filter
from tools.arjun import arjun_wrapper, arjun_bulk_scan, arjun_with_custom_payloads

# Create server
mcp = FastMCP(name="secops-mcp",
    version="1.0.0"
)


@mcp.tool()
def nuclei_scan_wrapper(
    target: str,
    templates: Optional[List[str]] = None,
    severity: Optional[str] = None,
    output_format: str = "json",
) -> str:
    """Run a Nuclei security scan on the specified target.
    
    Args:
        target: The target URL or IP to scan
        templates: List of specific template names to use (optional)
        severity: Filter by severity level (critical, high, medium, low, info)
        output_format: Output format (json, text)
    
    Returns:
        JSON string containing scan results with findings array
    """
    return run_nuclei(target, templates, severity, output_format)


@mcp.tool()
def ffuf_wrapper(
    url: str,
    wordlist: str,
    filter_code: Optional[str] = "404",
) -> str:
    """Run ffuf to fuzz web application endpoints.
    
    Args:
        url: Target URL with FUZZ keyword (e.g., "http://example.com/FUZZ")
        wordlist: Path to wordlist file
        filter_code: HTTP status code to filter out (e.g., "404")
    
    Returns:
        JSON string containing fuzzing results
    """
    return run_ffuf(url, wordlist, filter_code)


@mcp.tool()
def wfuzz_wrapper(
    url: str,
    wordlist: str,
    hide_code: Optional[str] = "404",
) -> str:
    """Run wfuzz to fuzz web application endpoints.
    
    Args:
        url: Target URL with FUZZ keyword (e.g., "http://example.com/FUZZ")
        wordlist: Path to wordlist file
        hide_code: HTTP status code to hide from results (e.g., "404")
    
    Returns:
        JSON string containing fuzzing results
    """
    return run_wfuzz(url, wordlist, hide_code)


@mcp.tool()
def sqlmap_wrapper(
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
        JSON string containing scan results
    """
    return run_sqlmap(url, risk, level)


@mcp.tool()
def nmap_wrapper(
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
        JSON string containing scan results in XML format
    """
    return run_nmap(target, ports, scan_type)


@mcp.tool()
def hashcat_wrapper(
    hash_file: str,
    wordlist: str,
    hash_type: str,
) -> str:
    """Run Hashcat to crack hashes.
    
    Args:
        hash_file: Path to file containing hashes
        wordlist: Path to wordlist file
        hash_type: Hash type (e.g., "0" for MD5, "1000" for NTLM, "md5", "sha1", "sha256")
    
    Returns:
        JSON string containing cracking results
    """
    return run_hashcat(hash_file, wordlist, hash_type)


@mcp.tool()
def httpx_wrapper(
    urls: List[str],
    status_codes: Optional[List[int]] = None,
) -> str:
    """Run httpx to probe HTTP servers and discover endpoints.
    
    Args:
        urls: List of target URLs or IPs to probe (required, at least one URL)
              Example: ["https://example.com"] or ["https://site1.com", "http://site2.com"]
        status_codes: Optional list of HTTP status codes to filter results
              Example: [200, 301, 404] - only returns results with these status codes
              If not provided, returns all status codes
    
    Returns:
        JSON string containing probe results with discovered endpoints, status codes, titles, etc.
        Format: {"success": true/false, "targets": [...], "results": [...], "count": N}
    
    Performance:
        - Request timeout: 5 seconds per request
        - Max retries: 1 (for speed)
        - Max redirects: 3
        - Overall timeout: 30 seconds maximum
        - Scans typically complete in 2-10 seconds for a single URL
    
    Example usage:
        - Single URL: httpx_wrapper(["https://hackerdogs.ai"])
        - Multiple URLs: httpx_wrapper(["https://site1.com", "http://site2.com"])
        - With status filter: httpx_wrapper(["https://example.com"], [200, 301])
    """
    return run_httpx(urls, status_codes)


@mcp.tool()
def subfinder_wrapper(
    domain: str,
    recursive: bool = False,
) -> str:
    """Run subfinder to enumerate subdomains.
    
    Args:
        domain: Target domain to enumerate
        recursive: Whether to perform recursive enumeration
    
    Returns:
        JSON string containing enumeration results with subdomains array
    """
    return run_subfinder(domain, recursive)


@mcp.tool()
def tlsx_wrapper(
    host: str,
    port: Optional[int] = 443,
) -> str:
    """Run tlsx to analyze TLS configurations.
    
    Args:
        host: Target hostname or IP address
        port: Target port (default: 443)
    
    Returns:
        JSON string containing TLS analysis results
    """
    return run_tlsx(host, port)


@mcp.tool()
def xsstrike_wrapper(
    url: str,
    crawl: bool = False,
) -> str:
    """Run XSStrike to detect XSS vulnerabilities.
    
    Args:
        url: Target URL to scan
        crawl: Whether to crawl the website for more URLs
    
    Returns:
        JSON string containing scan results
    """
    return run_xsstrike(url, crawl)


@mcp.tool()
def ipinfo_wrapper(
    ip: Optional[str] = None,
) -> str:
    """Get IP information using ipinfo.io.
    
    Args:
        ip: Optional IP address to lookup. If not provided, uses the current IP.
    
    Returns:
        JSON string containing IP information (location, ISP, etc.)
    """
    return run_ipinfo(ip)


@mcp.tool()
def amass_wrapper(
    domain: str,
    passive: bool = True,
) -> str:
    """Run Amass to enumerate subdomains and perform attack surface mapping.
    
    Args:
        domain: Target domain to enumerate
        passive: Whether to perform passive enumeration only (default: True)
    
    Returns:
        JSON string containing discovered subdomains with addresses and sources
    """
    result = amass_tool(domain, passive)
    return json.dumps(result, indent=2)


@mcp.tool()
def dirsearch_wrapper(
    url: str,
    extensions: Optional[List[str]] = None,
    wordlist: Optional[str] = None,
) -> str:
    """Run Dirsearch to brute force directories and files.
    
    Args:
        url: Target URL to scan
        extensions: File extensions to check (e.g., ["php", "html", "txt"])
        wordlist: Path to custom wordlist file
    
    Returns:
        JSON string containing discovered paths and their status codes
    """
    result = dirsearch_tool(url, extensions, wordlist)
    return json.dumps(result, indent=2)


@mcp.tool()
def gospider_scan(
    target: str,
    depth: int = 3,
    concurrent: int = 10,
    timeout: int = 10,
    user_agent: Optional[str] = None,
    headers: Optional[List[str]] = None,
    include_subs: bool = False,
    include_other_source: bool = False,
    output_format: str = "json"
) -> str:
    """Run Gospider to crawl websites and discover URLs, forms, and secrets.
    
    Args:
        target: Target URL or domain to crawl
        depth: Maximum crawling depth (default: 3)
        concurrent: Number of concurrent requests (default: 10)
        timeout: Request timeout in seconds (default: 10)
        user_agent: Custom User-Agent string
        headers: Custom headers to include (e.g., ["Authorization: Bearer token"])
        include_subs: Include subdomains in crawling (default: False)
        include_other_source: Include other sources like robots.txt, sitemap.xml (default: False)
        output_format: Output format (json, txt)
    
    Returns:
        JSON string containing discovered URLs, forms, and secrets
    """
    result = gospider_wrapper(
        target=target,
        depth=depth,
        concurrent=concurrent,
        timeout=timeout,
        user_agent=user_agent,
        headers=headers,
        include_subs=include_subs,
        include_other_source=include_other_source,
        output_format=output_format
    )
    return json.dumps(result, indent=2)


@mcp.tool()
def gospider_filtered_scan(
    target: str,
    extensions: Optional[List[str]] = None,
    exclude_extensions: Optional[List[str]] = None,
    filter_length: Optional[int] = None,
    depth: int = 3,
    concurrent: int = 10,
    timeout: int = 10,
    include_subs: bool = False
) -> str:
    """Run Gospider web crawling with filtering capabilities.
    
    Args:
        target: Target URL or domain to crawl
        extensions: Only crawl URLs with these extensions (e.g., ["js", "json"])
        exclude_extensions: Exclude URLs with these extensions (e.g., ["png", "jpg"])
        filter_length: Filter URLs by response length
        depth: Maximum crawling depth (default: 3)
        concurrent: Number of concurrent requests (default: 10)
        timeout: Request timeout in seconds (default: 10)
        include_subs: Include subdomains in crawling (default: False)
    
    Returns:
        JSON string containing filtered crawling results
    """
    result = gospider_crawl_with_filter(
        target=target,
        extensions=extensions,
        exclude_extensions=exclude_extensions,
        filter_length=filter_length,
        depth=depth,
        concurrent=concurrent,
        timeout=timeout,
        include_subs=include_subs
    )
    return json.dumps(result, indent=2)


@mcp.tool()
def arjun_scan(
    url: str,
    method: str = "GET",
    wordlist: Optional[str] = None,
    headers: Optional[List[str]] = None,
    data: Optional[str] = None,
    delay: int = 0,
    timeout: int = 10,
    threads: int = 25,
    stable: bool = False,
    output_format: str = "json"
) -> str:
    """Run Arjun to discover HTTP parameters in web applications.
    
    Args:
        url: Target URL to scan for parameters
        method: HTTP method to use (GET, POST, PUT, etc.)
        wordlist: Custom wordlist file path
        headers: Custom headers to include (e.g., ["Authorization: Bearer token"])
        data: POST data for POST requests
        delay: Delay between requests in seconds (default: 0)
        timeout: Request timeout in seconds (default: 10)
        threads: Number of threads to use (default: 25)
        stable: Use stable mode for fewer false positives (default: False)
        output_format: Output format (json, txt)
    
    Returns:
        JSON string containing discovered parameters
    """
    result = arjun_wrapper(
        url=url,
        method=method,
        wordlist=wordlist,
        headers=headers,
        data=data,
        delay=delay,
        timeout=timeout,
        threads=threads,
        stable=stable,
        output_format=output_format
    )
    return json.dumps(result, indent=2)


@mcp.tool()
def arjun_bulk_parameter_scan(
    urls: List[str],
    method: str = "GET",
    wordlist: Optional[str] = None,
    threads: int = 25,
    stable: bool = False
) -> str:
    """Run Arjun parameter discovery on multiple URLs.
    
    Args:
        urls: List of target URLs to scan
        method: HTTP method to use (default: GET)
        wordlist: Custom wordlist file path
        threads: Number of threads to use (default: 25)
        stable: Use stable mode for fewer false positives (default: False)
    
    Returns:
        JSON string containing aggregated results from all scanned URLs
    """
    result = arjun_bulk_scan(
        urls=urls,
        method=method,
        wordlist=wordlist,
        threads=threads,
        stable=stable
    )
    return json.dumps(result, indent=2)


@mcp.tool()
def arjun_custom_parameter_scan(
    url: str,
    method: str = "GET",
    custom_params: Optional[List[str]] = None,
    wordlist: Optional[str] = None,
    timeout: int = 10,
    threads: int = 25,
    stable: bool = False
) -> str:
    """Run Arjun with custom parameter testing capabilities.
    
    Args:
        url: Target URL to scan
        method: HTTP method to use (default: GET)
        custom_params: Custom parameters to test (e.g., ["api_key", "token"])
        wordlist: Custom wordlist file path
        timeout: Request timeout in seconds (default: 10)
        threads: Number of threads to use (default: 25)
        stable: Use stable mode for fewer false positives (default: False)
    
    Returns:
        JSON string containing results with custom parameter testing
    """
    result = arjun_with_custom_payloads(
        url=url,
        method=method,
        custom_params=custom_params,
        wordlist=wordlist,
        timeout=timeout,
        threads=threads,
        stable=stable
    )
    return json.dumps(result, indent=2)


if __name__ == "__main__":
    mcp.run(transport="stdio")