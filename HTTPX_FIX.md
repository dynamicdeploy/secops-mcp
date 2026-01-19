# HTTPX Tool Fix

## Issue Summary

The `httpx_wrapper` tool was failing with errors:
1. "No input provided: no files found" - when using `-l -` (stdin) without providing input
2. "expected str, bytes or os.PathLike object, not int" - type error with status_codes

## Root Cause

1. **Old code in container**: The Docker container was using old code that always used `-l -` (stdin) but didn't pass input data
2. **Missing input validation**: No check for empty target lists
3. **Type handling**: status_codes needed better type conversion

## Fix Applied

### 1. Smart URL Input Handling
- **Single URL**: Uses `-u` flag (simpler, more reliable)
- **Multiple URLs**: Uses `-l -` (stdin) with proper input piping
- **Empty list**: Returns clear error message

### 2. Input Validation
- Checks if targets list is empty
- Validates status_codes are integers
- Handles None values gracefully

### 3. Improved Documentation
- Added detailed docstring with examples
- Clear parameter descriptions
- Usage examples in MCP wrapper

## Code Changes

```python
# Before (broken):
cmd = ["httpx", "-json", "-silent", "-l", "-"]  # Always stdin, no input
result = subprocess.run(cmd, ...)  # No input provided!

# After (fixed):
if len(targets) == 1:
    cmd.extend(["-u", targets[0]])  # Single URL: use -u flag
    input_data = None
else:
    cmd.extend(["-l", "-"])  # Multiple URLs: use stdin
    input_data = "\n".join(targets)  # Pipe URLs via stdin

result = subprocess.run(cmd, input=input_data, ...)  # Proper input!
```

## Required Action

**Rebuild the Docker container** to get the updated code:

```bash
docker build -t hackerdogs/secops-mcp:latest .
docker push hackerdogs/secops-mcp:latest
```

## Testing

The fix handles:
- ✅ Single URL: `httpx_wrapper(["https://example.com"])`
- ✅ Multiple URLs: `httpx_wrapper(["https://site1.com", "http://site2.com"])`
- ✅ With status codes: `httpx_wrapper(["https://example.com"], [200, 301])`
- ✅ Empty list: Returns clear error
- ✅ Type errors: Handles non-integer status codes

## Documentation

The tool now has comprehensive documentation:
- Parameter descriptions
- Usage examples
- Return format explanation
- Error handling details

