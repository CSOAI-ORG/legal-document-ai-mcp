<div align="center">

# Legal Document Ai MCP

**MCP server for legal document ai mcp operations**

[![PyPI](https://img.shields.io/pypi/v/meok-legal-document-ai-mcp)](https://pypi.org/project/meok-legal-document-ai-mcp/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![MEOK AI Labs](https://img.shields.io/badge/MEOK_AI_Labs-MCP_Server-purple)](https://meok.ai)

</div>

## Overview

Legal Document Ai MCP provides AI-powered tools via the Model Context Protocol (MCP).

## Tools

| Tool | Description |
|------|-------------|
| `generate_nda` | Generate a Non-Disclosure Agreement template with customizable terms. |
| `explain_clause` | Analyze a contract clause in plain language. Detects clause type, |
| `define_legal_term` | Look up a legal term with definition, context, and example usage. |
| `check_compliance` | Check a document against compliance framework requirements. Scans for |
| `case_summary` | Generate a structured legal case summary using the IRAC framework |

## Installation

```bash
pip install meok-legal-document-ai-mcp
```

## Usage with Claude Desktop

Add to your Claude Desktop MCP config (`claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "legal-document-ai-mcp": {
      "command": "python",
      "args": ["-m", "meok_legal_document_ai_mcp.server"]
    }
  }
}
```

## Usage with FastMCP

```python
from mcp.server.fastmcp import FastMCP

# This server exposes 5 tool(s) via MCP
# See server.py for full implementation
```

## License

MIT © [MEOK AI Labs](https://meok.ai)
