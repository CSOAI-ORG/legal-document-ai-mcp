#!/usr/bin/env python3
"""
Legal Document AI MCP Server
================================
Legal document toolkit for AI agents: NDA generation, contract clause explanation,
legal term definitions, compliance checking, and case summary writing.

By MEOK AI Labs | https://meok.ai

Install: pip install mcp
Run:     python server.py
"""

import re
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Any, Optional
from mcp.server.fastmcp import FastMCP

# ---------------------------------------------------------------------------
# Rate limiting
# ---------------------------------------------------------------------------
FREE_DAILY_LIMIT = 30
_usage: dict[str, list[datetime]] = defaultdict(list)


def _check_rate_limit(caller: str = "anonymous") -> Optional[str]:
    now = datetime.now()
    cutoff = now - timedelta(days=1)
    _usage[caller] = [t for t in _usage[caller] if t > cutoff]
    if len(_usage[caller]) >= FREE_DAILY_LIMIT:
        return f"Free tier limit reached ({FREE_DAILY_LIMIT}/day). Upgrade: https://mcpize.com/legal-document-ai-mcp/pro"
    _usage[caller].append(now)
    return None


# ---------------------------------------------------------------------------
# Legal reference data
# ---------------------------------------------------------------------------
LEGAL_TERMS = {
    "force majeure": {
        "definition": "A contractual provision that frees both parties from obligation when an extraordinary event beyond their control prevents one or both from fulfilling duties.",
        "context": "Common in commercial contracts to address unforeseeable circumstances like natural disasters, pandemics, or government actions.",
        "example": "The supplier shall not be liable for delays caused by force majeure events including but not limited to earthquakes, floods, epidemics, or government orders.",
    },
    "indemnification": {
        "definition": "A contractual obligation of one party to compensate the other for losses or damages arising from specified events or breaches.",
        "context": "Shifts financial risk between parties. Common in service agreements, IP licenses, and vendor contracts.",
        "example": "Provider shall indemnify and hold harmless Client from any third-party claims arising from Provider's negligence or willful misconduct.",
    },
    "severability": {
        "definition": "A clause that preserves the remainder of a contract if one provision is found invalid or unenforceable.",
        "context": "Standard boilerplate clause ensuring partial invalidity does not void the entire agreement.",
        "example": "If any provision of this Agreement is held invalid, the remaining provisions shall continue in full force and effect.",
    },
    "non-compete": {
        "definition": "A restrictive covenant preventing a party from engaging in competing activities for a specified period and geographic area.",
        "context": "Common in employment and acquisition agreements. Enforceability varies significantly by jurisdiction.",
        "example": "Employee agrees not to engage in competing business within 50 miles of Company's offices for 12 months following termination.",
    },
    "liquidated damages": {
        "definition": "A predetermined amount of money that must be paid as damages for breach of contract, agreed upon at the time of contract formation.",
        "context": "Used when actual damages would be difficult to calculate. Must be reasonable; excessive amounts may be deemed penalties.",
        "example": "For each day of delay beyond the completion date, Contractor shall pay $500 per day as liquidated damages.",
    },
    "arbitration": {
        "definition": "A method of alternative dispute resolution where disputes are resolved by one or more arbitrators rather than through litigation.",
        "context": "Often faster and more private than court proceedings. May be binding or non-binding.",
        "example": "Any dispute arising from this Agreement shall be resolved by binding arbitration under the rules of the American Arbitration Association.",
    },
    "intellectual property assignment": {
        "definition": "The transfer of ownership rights in intellectual property (patents, copyrights, trademarks, trade secrets) from one party to another.",
        "context": "Common in employment agreements and contractor arrangements to ensure the company owns work product.",
        "example": "Contractor hereby assigns to Company all right, title, and interest in any inventions, works of authorship, or discoveries made during the engagement.",
    },
    "limitation of liability": {
        "definition": "A contractual provision that caps the maximum amount of damages one party can recover from the other.",
        "context": "Manages risk exposure. Often expressed as a multiple of fees paid or a fixed dollar amount.",
        "example": "In no event shall Provider's total liability exceed the fees paid by Client in the twelve months preceding the claim.",
    },
    "governing law": {
        "definition": "A clause specifying which jurisdiction's laws will govern the interpretation and enforcement of the contract.",
        "context": "Critical in cross-border agreements. Should be paired with a dispute resolution clause.",
        "example": "This Agreement shall be governed by and construed in accordance with the laws of the State of Delaware.",
    },
    "representations and warranties": {
        "definition": "Statements of fact (representations) and promises about the condition of something (warranties) that form the basis of the agreement.",
        "context": "If proven false, they can give rise to breach of contract or indemnification claims.",
        "example": "Each party represents and warrants that it has full power and authority to enter into this Agreement.",
    },
}

NDA_TYPES = {
    "mutual": "Both parties share and protect each other's confidential information",
    "unilateral": "Only one party (the discloser) shares confidential information",
    "multilateral": "Three or more parties share confidential information",
}


# ---------------------------------------------------------------------------
# Core operations
# ---------------------------------------------------------------------------
def _generate_nda(party_a: str, party_b: str, nda_type: str,
                  duration_months: int, jurisdiction: str,
                  scope: str) -> dict:
    """Generate an NDA template with customizable terms."""
    if nda_type not in NDA_TYPES:
        return {"error": f"Invalid NDA type. Use: {list(NDA_TYPES.keys())}"}

    effective_date = datetime.now().strftime("%B %d, %Y")
    expiry_date = (datetime.now() + timedelta(days=duration_months * 30)).strftime("%B %d, %Y")

    sections = [
        {
            "section": "1. DEFINITIONS",
            "content": f'"Confidential Information" means any non-public information disclosed by either party relating to {scope}, including but not limited to technical data, trade secrets, business plans, financial information, customer lists, and proprietary processes.'
        },
        {
            "section": "2. OBLIGATIONS",
            "content": f"The Receiving Party agrees to: (a) hold Confidential Information in strict confidence; (b) not disclose it to third parties without prior written consent; (c) use it solely for the purpose of {scope}; (d) protect it with at least the same degree of care used for its own confidential information."
        },
        {
            "section": "3. EXCLUSIONS",
            "content": "Confidential Information does not include information that: (a) is or becomes publicly available through no fault of the Receiving Party; (b) was already known to the Receiving Party prior to disclosure; (c) is independently developed without use of Confidential Information; (d) is disclosed by a third party without restriction."
        },
        {
            "section": "4. TERM",
            "content": f"This Agreement is effective from {effective_date} and shall remain in force for {duration_months} months until {expiry_date}. Obligations of confidentiality shall survive termination for a period of {max(12, duration_months)} months."
        },
        {
            "section": "5. RETURN OF MATERIALS",
            "content": "Upon termination or request, the Receiving Party shall promptly return or destroy all Confidential Information and certify such destruction in writing."
        },
        {
            "section": "6. REMEDIES",
            "content": "The parties acknowledge that breach may cause irreparable harm for which monetary damages would be insufficient. The Disclosing Party shall be entitled to seek injunctive relief in addition to any other remedies available at law or equity."
        },
        {
            "section": "7. GOVERNING LAW",
            "content": f"This Agreement shall be governed by the laws of {jurisdiction}."
        },
        {
            "section": "8. ENTIRE AGREEMENT",
            "content": "This Agreement constitutes the entire understanding between the parties regarding confidentiality and supersedes all prior negotiations and agreements."
        },
    ]

    header = f"""NON-DISCLOSURE AGREEMENT ({nda_type.upper()})

This Non-Disclosure Agreement ("Agreement") is entered into as of {effective_date}

BETWEEN:
  "{party_a}" (hereinafter "{'Disclosing Party' if nda_type == 'unilateral' else 'Party A'}")
AND:
  "{party_b}" (hereinafter "{'Receiving Party' if nda_type == 'unilateral' else 'Party B'}")

PURPOSE: {scope}"""

    return {
        "nda_type": nda_type,
        "type_description": NDA_TYPES[nda_type],
        "parties": {"party_a": party_a, "party_b": party_b},
        "effective_date": effective_date,
        "expiry_date": expiry_date,
        "duration_months": duration_months,
        "jurisdiction": jurisdiction,
        "scope": scope,
        "header": header,
        "sections": sections,
        "signature_block": f"""
IN WITNESS WHEREOF, the parties have executed this Agreement as of the date first written above.

{party_a}                              {party_b}
Signature: _______________             Signature: _______________
Name: ____________________             Name: ____________________
Title: ___________________             Title: ___________________
Date: ____________________             Date: ____________________""",
        "disclaimer": "TEMPLATE ONLY. Not legal advice. Have an attorney review before signing.",
    }


def _explain_clause(clause_text: str, context: str) -> dict:
    """Analyze and explain a contract clause in plain language."""
    if not clause_text.strip():
        return {"error": "Clause text cannot be empty"}

    words = clause_text.split()
    word_count = len(words)

    # Detect clause type
    clause_types = {
        "indemnif": "indemnification",
        "confidential": "confidentiality",
        "terminat": "termination",
        "force majeure": "force majeure",
        "non-compete": "non-compete",
        "intellectual property": "ip_assignment",
        "arbitrat": "dispute_resolution",
        "warrant": "warranty",
        "limit": "limitation_of_liability",
        "governing law": "governing_law",
        "severab": "severability",
    }

    detected_type = "general"
    for keyword, ctype in clause_types.items():
        if keyword in clause_text.lower():
            detected_type = ctype
            break

    # Readability assessment
    complex_phrases = ["notwithstanding", "hereinafter", "whereas", "pursuant to",
                       "in the event that", "shall be deemed", "without limitation",
                       "to the fullest extent"]
    found_complex = [p for p in complex_phrases if p in clause_text.lower()]
    readability = "simple" if len(found_complex) == 0 else "moderate" if len(found_complex) <= 2 else "complex"

    # Risk indicators
    risk_phrases = {
        "unlimited liability": "HIGH",
        "sole discretion": "MEDIUM",
        "irrevocable": "MEDIUM",
        "perpetual": "MEDIUM",
        "waive": "MEDIUM",
        "exclusive remedy": "HIGH",
        "as-is": "HIGH",
        "no warranty": "HIGH",
        "consequential damages": "MEDIUM",
    }

    risks = []
    for phrase, level in risk_phrases.items():
        if phrase in clause_text.lower():
            risks.append({"phrase": phrase, "risk_level": level})

    # Key obligations
    obligations = []
    obligation_markers = ["shall", "must", "agrees to", "is required to", "will"]
    for marker in obligation_markers:
        for match in re.finditer(rf'\b{marker}\b\s+(.{{20,80}}?)(?:[.;]|$)', clause_text, re.I):
            obligations.append(match.group(0).strip()[:100])

    return {
        "clause_type": detected_type,
        "word_count": word_count,
        "readability": readability,
        "complex_phrases_found": found_complex,
        "risk_indicators": risks,
        "obligations_detected": obligations[:5],
        "plain_language_notes": [
            f"This appears to be a {detected_type.replace('_', ' ')} clause",
            f"Readability: {readability} ({len(found_complex)} legal jargon phrases detected)",
            f"{'No significant risk phrases found' if not risks else f'Found {len(risks)} risk indicator(s) - review carefully'}",
        ],
        "context": context,
        "recommendation": "Have a qualified attorney review any clause with HIGH risk indicators before signing.",
    }


def _define_legal_term(term: str) -> dict:
    """Look up a legal term definition."""
    term_lower = term.lower().strip()

    # Direct match
    if term_lower in LEGAL_TERMS:
        result = LEGAL_TERMS[term_lower].copy()
        result["term"] = term
        result["found"] = True
        return result

    # Partial match
    matches = []
    for key, data in LEGAL_TERMS.items():
        if term_lower in key or key in term_lower:
            matches.append({"term": key, **data})

    if matches:
        return {
            "term": term,
            "found": False,
            "partial_matches": matches,
            "suggestion": f"Did you mean: {', '.join(m['term'] for m in matches)}?",
        }

    return {
        "term": term,
        "found": False,
        "available_terms": sorted(LEGAL_TERMS.keys()),
        "suggestion": "Term not in database. Try one of the available terms or provide more context.",
    }


def _compliance_check(document_text: str, framework: str) -> dict:
    """Check document text against compliance requirements."""
    frameworks = {
        "GDPR": {
            "required_elements": [
                ("data controller", "Must identify the data controller"),
                ("data processor", "Must identify any data processors"),
                ("lawful basis", "Must state the lawful basis for processing"),
                ("data subject rights", "Must describe data subject rights"),
                ("retention", "Must specify data retention periods"),
                ("transfer", "Must address international data transfers"),
                ("breach notification", "Must include breach notification procedures"),
                ("dpo", "Should reference Data Protection Officer if applicable"),
            ],
        },
        "HIPAA": {
            "required_elements": [
                ("protected health information", "Must define PHI scope"),
                ("permitted use", "Must specify permitted uses and disclosures"),
                ("safeguard", "Must require appropriate safeguards"),
                ("breach", "Must include breach notification requirements"),
                ("minimum necessary", "Must apply minimum necessary standard"),
                ("individual rights", "Must address patient access rights"),
                ("business associate", "Must define business associate obligations"),
            ],
        },
        "SOC2": {
            "required_elements": [
                ("security", "Must address security controls"),
                ("availability", "Must address system availability"),
                ("confidentiality", "Must address data confidentiality"),
                ("access control", "Must define access control procedures"),
                ("monitoring", "Must include monitoring and logging"),
                ("incident response", "Must have incident response plan"),
                ("vendor management", "Must address third-party risk"),
            ],
        },
        "PCI_DSS": {
            "required_elements": [
                ("cardholder data", "Must define cardholder data handling"),
                ("encryption", "Must require encryption of card data"),
                ("access", "Must restrict access to card data"),
                ("network", "Must address network security"),
                ("vulnerability", "Must include vulnerability management"),
                ("monitoring", "Must maintain audit trails"),
            ],
        },
    }

    if framework not in frameworks:
        return {"error": f"Unknown framework '{framework}'. Available: {list(frameworks.keys())}"}

    text_lower = document_text.lower()
    checks = frameworks[framework]["required_elements"]

    results = []
    found_count = 0
    for keyword, requirement in checks:
        present = keyword in text_lower
        if present:
            found_count += 1
        results.append({
            "element": keyword,
            "requirement": requirement,
            "found": present,
            "status": "PASS" if present else "MISSING",
        })

    coverage = (found_count / len(checks)) * 100

    if coverage >= 90:
        assessment = "Good coverage - minor gaps may exist"
    elif coverage >= 70:
        assessment = "Partial coverage - several required elements missing"
    elif coverage >= 50:
        assessment = "Insufficient - significant compliance gaps"
    else:
        assessment = "Poor - document needs substantial revision"

    return {
        "framework": framework,
        "document_length": len(document_text),
        "word_count": len(document_text.split()),
        "coverage_pct": round(coverage, 1),
        "assessment": assessment,
        "elements_found": found_count,
        "elements_total": len(checks),
        "results": results,
        "missing_elements": [r for r in results if not r["found"]],
        "disclaimer": "Automated check only. Does not replace professional legal/compliance review.",
    }


def _case_summary(case_name: str, parties: list[str], facts: str,
                   legal_issues: list[str], holding: str) -> dict:
    """Generate a structured case summary / brief."""
    if not facts.strip():
        return {"error": "Case facts cannot be empty"}

    # Extract key dates from facts
    dates = re.findall(r'\b\d{4}\b|\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}\b', facts, re.I)

    # Count sentences for complexity
    sentences = [s.strip() for s in re.split(r'[.!?]+', facts) if s.strip()]
    fact_complexity = "simple" if len(sentences) <= 5 else "moderate" if len(sentences) <= 15 else "complex"

    # Structure the summary
    summary = {
        "case_name": case_name,
        "parties": {
            "plaintiff": parties[0] if len(parties) > 0 else "Unknown",
            "defendant": parties[1] if len(parties) > 1 else "Unknown",
            "other": parties[2:] if len(parties) > 2 else [],
        },
        "procedural_history": f"Case involving {' v. '.join(parties[:2]) if len(parties) >= 2 else case_name}",
        "facts": {
            "narrative": facts,
            "sentence_count": len(sentences),
            "complexity": fact_complexity,
            "key_dates": dates[:10],
        },
        "legal_issues": [
            {"issue_number": i + 1, "issue": issue}
            for i, issue in enumerate(legal_issues)
        ],
        "holding": holding,
        "analysis": {
            "issue_count": len(legal_issues),
            "fact_sentences": len(sentences),
        },
        "irac_framework": {
            "issue": legal_issues[0] if legal_issues else "Not specified",
            "rule": "Applicable legal standards referenced in the holding",
            "application": "How the court applied the rule to the facts",
            "conclusion": holding or "Not specified",
        },
        "disclaimer": "AI-generated summary. Verify against original court documents.",
    }

    return summary


# ---------------------------------------------------------------------------
# MCP Server
# ---------------------------------------------------------------------------
mcp = FastMCP(
    "Legal Document AI MCP",
    instructions="Legal document toolkit: NDA generation, contract clause explanation, legal term definitions, compliance checking, and case summaries. By MEOK AI Labs.")


@mcp.tool()
def generate_nda(party_a: str, party_b: str, nda_type: str = "mutual",
                 duration_months: int = 24, jurisdiction: str = "State of Delaware",
                 scope: str = "exploring a potential business relationship") -> dict:
    """Generate a Non-Disclosure Agreement template with customizable terms.

    Args:
        party_a: First party name/company
        party_b: Second party name/company
        nda_type: NDA type (mutual, unilateral, multilateral)
        duration_months: Agreement duration in months
        jurisdiction: Governing law jurisdiction
        scope: Purpose/scope of the NDA
    """
    err = _check_rate_limit()
    if err:
        return {"error": err}
    try:
        return _generate_nda(party_a, party_b, nda_type, duration_months, jurisdiction, scope)
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def explain_clause(clause_text: str, context: str = "") -> dict:
    """Analyze a contract clause in plain language. Detects clause type,
    readability, risk indicators, and key obligations.

    Args:
        clause_text: The contract clause text to analyze
        context: Optional context about the agreement type
    """
    err = _check_rate_limit()
    if err:
        return {"error": err}
    try:
        return _explain_clause(clause_text, context)
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def define_legal_term(term: str) -> dict:
    """Look up a legal term with definition, context, and example usage.

    Args:
        term: Legal term to define (e.g. "force majeure", "indemnification")
    """
    err = _check_rate_limit()
    if err:
        return {"error": err}
    try:
        return _define_legal_term(term)
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def check_compliance(document_text: str, framework: str = "GDPR") -> dict:
    """Check a document against compliance framework requirements. Scans for
    required elements and reports coverage gaps.

    Args:
        document_text: The document text to check
        framework: Compliance framework (GDPR, HIPAA, SOC2, PCI_DSS)
    """
    err = _check_rate_limit()
    if err:
        return {"error": err}
    try:
        return _compliance_check(document_text, framework)
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def case_summary(case_name: str, parties: list[str], facts: str,
                 legal_issues: list[str] = [], holding: str = "") -> dict:
    """Generate a structured legal case summary using the IRAC framework
    (Issue, Rule, Application, Conclusion).

    Args:
        case_name: Name of the case (e.g. "Smith v. Jones")
        parties: List of party names [plaintiff, defendant, ...]
        facts: Narrative of the case facts
        legal_issues: List of legal issues in the case
        holding: Court's holding/decision
    """
    err = _check_rate_limit()
    if err:
        return {"error": err}
    try:
        return _case_summary(case_name, parties, facts, legal_issues, holding)
    except Exception as e:
        return {"error": str(e)}


if __name__ == "__main__":
    mcp.run()
