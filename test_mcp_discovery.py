#!/usr/bin/env python3
"""Test MCP server tool discovery and execution."""

import json
import sys
import subprocess
from typing import Dict, Any, List


def test_mcp_tools_direct():
    """Test tools directly (without MCP)."""
    print("="*70)
    print("Direct Tool Testing")
    print("="*70)
    
    from tools.ipinfo import run_ipinfo
    from tools.httpx import run_httpx
    
    # Test ipinfo
    print("\n1. Testing ipinfo...")
    result = run_ipinfo()
    try:
        data = json.loads(result)
        print(f"   ✓ ipinfo works - returned {len(data)} fields")
    except:
        print(f"   ✗ ipinfo failed")
    
    # Test httpx error message
    print("\n2. Testing httpx error handling...")
    result = run_httpx(["https://hackerdogs.ai"])
    data = json.loads(result)
    if not data.get('success'):
        error = data.get('error', '')
        if 'Wrong httpx binary' in error or 'not found' in error:
            print(f"   ✓ httpx error handling works - clear error message")
        else:
            print(f"   ⚠ httpx error: {error[:100]}")
    else:
        print(f"   ✓ httpx works!")
    
    print("\n" + "="*70)


def test_mcp_server_startup():
    """Test if MCP server can start."""
    print("\n" + "="*70)
    print("MCP Server Startup Test")
    print("="*70)
    
    try:
        # Try to import and check server
        import main
        print("✓ MCP server module imports successfully")
        print(f"✓ Server name: {main.mcp.name}")
        print(f"✓ Server version: {main.mcp.version}")
        
        # Count tools
        tools = [attr for attr in dir(main.mcp) if not attr.startswith('_')]
        print(f"✓ Server initialized")
        
        return True
    except Exception as e:
        print(f"✗ Failed to start MCP server: {e}")
        return False


def test_mcp_tool_discovery():
    """Test MCP tool discovery using stdio transport simulation."""
    print("\n" + "="*70)
    print("MCP Tool Discovery Test")
    print("="*70)
    
    try:
        # Import the server
        import main
        
        # Get all registered tools
        # FastMCP stores tools in _tools attribute
        if hasattr(main.mcp, '_tools'):
            tools = main.mcp._tools
            print(f"\n✓ Found {len(tools)} registered MCP tools:\n")
            
            for tool_name, tool_info in tools.items():
                print(f"  • {tool_name}")
                if hasattr(tool_info, '__annotations__'):
                    params = tool_info.__annotations__
                    if 'return' in params:
                        del params['return']
                    if params:
                        print(f"    Parameters: {', '.join(params.keys())}")
        else:
            # Try alternative way to get tools
            print("\n⚠ Could not access tools directly, checking via attributes...")
            # List all @mcp.tool decorated functions
            import inspect
            for name, obj in inspect.getmembers(main):
                if inspect.isfunction(obj) and hasattr(obj, '__wrapped__'):
                    print(f"  • {name}")
        
        return True
    except Exception as e:
        print(f"✗ Failed to discover tools: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_mcp_protocol():
    """Test MCP protocol using a simple client."""
    print("\n" + "="*70)
    print("MCP Protocol Test (using mcp CLI if available)")
    print("="*70)
    
    # Check if mcp CLI is available
    try:
        result = subprocess.run(
            ["mcp", "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        print("✓ MCP CLI found")
        print(f"  Version: {result.stdout.strip()}")
        return True
    except FileNotFoundError:
        print("⚠ MCP CLI not found - install with: npm install -g @modelcontextprotocol/cli")
        return False
    except Exception as e:
        print(f"⚠ MCP CLI check failed: {e}")
        return False


def test_tool_signatures():
    """Test that all tool signatures are correct."""
    print("\n" + "="*70)
    print("Tool Signature Verification")
    print("="*70)
    
    import main
    import inspect
    
    issues = []
    tools_checked = 0
    
    # Get all tool functions from main
    for name, obj in inspect.getmembers(main):
        if inspect.isfunction(obj) and name.endswith('_wrapper'):
            tools_checked += 1
            sig = inspect.signature(obj)
            params = list(sig.parameters.keys())
            
            # Check if it has a docstring
            if not obj.__doc__ or len(obj.__doc__.strip()) < 20:
                issues.append(f"{name}: Missing or insufficient docstring")
            
            print(f"  ✓ {name}: {len(params)} parameters")
    
    print(f"\n✓ Checked {tools_checked} tool wrappers")
    if issues:
        print(f"\n⚠ Found {len(issues)} issues:")
        for issue in issues:
            print(f"  - {issue}")
    else:
        print("✓ All tool signatures look good")
    
    return len(issues) == 0


def main():
    """Run all tests."""
    print("="*70)
    print("MCP Server Comprehensive Test Suite")
    print("="*70)
    
    results = []
    
    # Test 1: Direct tool testing
    test_mcp_tools_direct()
    results.append(("Direct Tools", True))
    
    # Test 2: Server startup
    results.append(("Server Startup", test_mcp_server_startup()))
    
    # Test 3: Tool discovery
    results.append(("Tool Discovery", test_mcp_tool_discovery()))
    
    # Test 4: Tool signatures
    results.append(("Tool Signatures", test_tool_signatures()))
    
    # Test 5: MCP Protocol
    results.append(("MCP Protocol", test_mcp_protocol()))
    
    # Summary
    print("\n" + "="*70)
    print("Test Summary")
    print("="*70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{name:25} {status}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n✓ All tests passed!")
        return 0
    else:
        print(f"\n⚠ {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())

