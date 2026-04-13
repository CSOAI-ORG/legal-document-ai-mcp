# Legal Document AI MCP Server
**By MEOK AI Labs** | [meok.ai](https://meok.ai)

Legal document toolkit: NDA generation, contract clause explanation, legal term definitions, compliance checking, and case summaries.

## Tools

| Tool | Description |
|------|-------------|
| `generate_nda` | Generate customizable NDA templates (mutual, unilateral, multilateral) |
| `explain_clause` | Analyze contract clauses in plain language with risk indicators |
| `define_legal_term` | Look up legal terms with definitions, context, and examples |
| `check_compliance` | Check documents against GDPR, HIPAA, SOC2, PCI-DSS frameworks |
| `case_summary` | Generate structured legal case summaries using IRAC framework |

## Installation

```bash
pip install mcp
```

## Usage

### Run the server

```bash
python server.py
```

### Claude Desktop config

```json
{
  "mcpServers": {
    "legal-document": {
      "command": "python",
      "args": ["/path/to/legal-document-ai-mcp/server.py"]
    }
  }
}
```

## Pricing

| Tier | Limit | Price |
|------|-------|-------|
| Free | 30 calls/day | $0 |
| Pro | Unlimited + premium features | $9/mo |
| Enterprise | Custom + SLA + support | Contact us |

## License

MIT
