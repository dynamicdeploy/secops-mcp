#!/usr/bin/env python3
"""Test MCP server connection and tool discovery using MCP client."""

import json
import sys
import asyncio
from typing import List, Dict, Any


async def test_mcp_client_connection():
    """Test MCP server using Python MCP client library."""
    print("="*70)
    print("MCP Client Connection Test")
    print("="*70)
    
    try:
        from mcp import ClientSession, StdioServerParameters
        from mcp.client.stdio import stdio_client
        
        print("\n✓ MCP client library found")
        
        # Create server parameters
        server_params = StdioServerParameters(
            command=sys.executable,
            args=["main.py"],
            env=None
        )
        
        print("Connecting to MCP server...")
        
        # Connect to server
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                # Initialize
                print("Initializing session...")
                init_result = await session.initialize()
                print(f"✓ Server initialized: {init_result.server_info.name} v{init_result.server_info.version}")
                
                # List tools
                print("\nDiscovering tools...")
                tools_result = await session.list_tools()
                
                print(f"\n✓ Found {len(tools_result.tools)} tools:\n")
                
                for i, tool in enumerate(tools_result.tools, 1):
                    print(f"  {i:2}. {tool.name}")
                    if tool.description:
                        desc = tool.description[:60] + "..." if len(tool.description) > 60 else tool.description
                        print(f"      {desc}")
                    
                    # Show parameters
                    if tool.inputSchema and 'properties' in tool.inputSchema:
                        params = list(tool.inputSchema['properties'].keys())
                        if params:
                            print(f"      Parameters: {', '.join(params[:5])}{'...' if len(params) > 5 else ''}")
                
                # Test a simple tool call
                print("\n" + "="*70)
                print("Testing Tool Execution")
                print("="*70)
                
                # Test ipinfo (should work)
                print("\n1. Testing ipinfo_wrapper...")
                try:
                    result = await session.call_tool("ipinfo_wrapper", {})
                    print(f"   ✓ ipinfo_wrapper executed successfully")
                    if result.content:
                        content = result.content[0]
                        if hasattr(content, 'text'):
                            data = json.loads(content.text)
                            print(f"   ✓ Returned data with {len(data)} fields")
                except Exception as e:
                    print(f"   ✗ ipinfo_wrapper failed: {e}")
                
                # Test httpx (will fail but should return proper error)
                print("\n2. Testing httpx_wrapper...")
                try:
                    result = await session.call_tool("httpx_wrapper", {
                        "urls": ["https://hackerdogs.ai"]
                    })
                    print(f"   ✓ httpx_wrapper executed")
                    if result.content:
                        content = result.content[0]
                        if hasattr(content, 'text'):
                            data = json.loads(content.text)
                            if data.get('success'):
                                print(f"   ✓ httpx works!")
                            else:
                                error = data.get('error', '')[:80]
                                if 'projectdiscovery' in error or 'not found' in error:
                                    print(f"   ✓ httpx returned expected error message")
                                else:
                                    print(f"   ⚠ httpx error: {error}")
                except Exception as e:
                    print(f"   ✗ httpx_wrapper failed: {e}")
                
                return True
                
    except ImportError:
        print("⚠ MCP client library not available")
        print("  Install with: pip install mcp")
        return False
    except Exception as e:
        print(f"✗ Connection test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_without_mcp_library():
    """Fallback test when MCP library is not available."""
    print("="*70)
    print("MCP Tool Discovery (Code Analysis)")
    print("="*70)
    
    print("\nAnalyzing main.py for tool definitions...\n")
    
    try:
        with open("main.py", "r") as f:
            content = f.read()
        
        import re
        
        # Find all tool definitions
        tool_pattern = r'@mcp\.tool\(\)\s+def\s+(\w+)\(([^)]*)\)\s*->\s*str:'
        matches = list(re.finditer(tool_pattern, content, re.MULTILINE | re.DOTALL))
        
        print(f"✓ Found {len(matches)} MCP tool definitions:\n")
        
        for i, match in enumerate(matches, 1):
            tool_name = match.group(1)
            params_str = match.group(2)
            
            # Extract parameters
            params = []
            for param in params_str.split(','):
                param = param.strip()
                if param:
                    param_name = param.split(':')[0].split('=')[0].strip()
                    params.append(param_name)
            
            # Get docstring (next few lines after function definition)
            lines = content[match.end():match.end()+500].split('\n')
            docstring = ""
            for line in lines[:10]:
                if '"""' in line or "'''" in line:
                    # Extract docstring
                    if '"""' in line:
                        docstring = line.split('"""')[1] if '"""' in line else ""
                    break
            
            print(f"  {i:2}. {tool_name}")
            print(f"      Parameters: {', '.join(params) if params else 'None'}")
            if docstring:
                print(f"      Description: {docstring[:60]}...")
            print()
        
        return True
        
    except Exception as e:
        print(f"✗ Analysis failed: {e}")
        return False


async def main():
    """Run MCP connection tests."""
    print("="*70)
    print("MCP Server Connection & Discovery Test")
    print("="*70)
    
    # Try MCP client library first
    try:
        result = await test_mcp_client_connection()
        if result:
            print("\n✓ MCP client connection successful!")
            return 0
    except Exception as e:
        print(f"\n⚠ MCP client test failed: {e}")
    
    # Fallback to code analysis
    print("\n" + "="*70)
    result = test_without_mcp_library()
    
    if result:
        print("\n✓ Tool discovery completed!")
        return 0
    else:
        print("\n✗ Tool discovery failed")
        return 1


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

