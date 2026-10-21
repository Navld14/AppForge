import anthropic
import json
import re
from typing import Any


STAGE_PROMPTS = {
    "intent": """You are Stage 1 of an app compiler: Intent Extraction.

Parse the user's natural language request into a structured intermediate form.

Return ONLY valid JSON in this exact schema:
{
  "app_name": "string",
  "app_type": "string (e.g. CRM, E-commerce, SaaS, Dashboard, etc.)",
  "core_entities": ["list of main data entities"],
  "features": ["list of explicit features requested"],
  "roles": ["list of user roles"],
  "auth_required": true/false,
  "payment_required": true/false,
  "ambiguities": ["list of unclear or missing requirements"],
  "assumptions": ["list of reasonable assumptions made"]
}

User prompt: {prompt}""",

    "architecture": """You are Stage 2 of an app compiler: System Design Layer.

Given the extracted intent below, design the full application architecture.

Return ONLY valid JSON in this exact schema:
{
  "entities": [
    {
      "name": "string",
      "description": "string",
      "fields": [{"name": "string", "type": "string", "required": true/false}],
      "relations": [{"entity": "string", "type": "one_to_many|many_to_many|one_to_one"}]
    }
  ],
  "flows": [
    {"name": "string", "steps": ["string"], "roles_involved": ["string"]}
  ],
  "roles": [
    {"name": "string", "permissions": ["string"]}
  ],
  "pages": ["list of page names needed"]
}

Extracted intent: {intent}""",

    "schema": """You are Stage 3 of an app compiler: Schema Generation.

Given the architecture below, generate four complete schemas.

Return ONLY valid JSON in this exact schema:
{
  "db_schema": {
    "tables": [
      {
        "name": "string",
        "columns": [
          {"name": "string", "type": "string", "nullable": true/false, "primary_key": true/false, "foreign_key": "table.column or null"}
        ],
        "indexes": ["list of column names to index"]
      }
    ]
  },
  "api_schema": {
    "endpoints": [
      {
        "method": "GET|POST|PUT|DELETE",
        "path": "string",
        "description": "string",
        "request_body": {"field": "type"},
        "response": {"field": "type"},
        "auth_required": true/false,
        "roles_allowed": ["string"]
      }
    ]
  },
  "ui_schema": {
    "pages": [
      {
        "name": "string",
        "route": "string",
        "components": [
          {"type": "string", "props": {}, "data_source": "api_endpoint or null"}
        ],
        "auth_required": true/false,
        "roles_allowed": ["string"]
      }
    ]
  },
  "auth_schema": {
    "strategy": "string (jwt, session, oauth, etc.)",
    "roles": [
      {"name": "string", "inherits": "string or null", "permissions": ["string"]}
    ],
    "protected_routes": ["string"],
    "token_expiry": "string"
  }
}

Architecture: {architecture}""",

    "refinement": """You are Stage 4 of an app compiler: Refinement Layer.

Review all schemas for inconsistencies and fix them. Check:
1. Every API endpoint's request/response fields exist in DB schema
2. Every UI page's data_source matches a real API endpoint
3. Every role referenced in API/UI exists in auth_schema
4. Foreign keys reference real tables and columns
5. No orphaned entities

Return the COMPLETE corrected output as ONLY valid JSON with this schema:
{
  "db_schema": { ...same as before... },
  "api_schema": { ...same as before... },
  "ui_schema": { ...same as before... },
  "auth_schema": { ...same as before... },
  "refinement_notes": ["list of issues found and fixed"]
}

Intent: {intent}
Architecture: {architecture}
Schemas: {schemas}"""
}


class AppForgePipeline:

    async def run(self, prompt: str, api_key: str) -> dict:
        client = anthropic.Anthropic(api_key=api_key)
        stages = {}
        errors = []

        # Stage 1: Intent Extraction
        intent_raw = await self._call_llm(client, STAGE_PROMPTS["intent"].format(prompt=prompt))
        intent, err = self._parse_and_repair(client, intent_raw, "intent", api_key)
        stages["intent"] = intent
        if err:
            errors.append({"stage": "intent", "issue": err})

        # Stage 2: Architecture
        arch_raw = await self._call_llm(client, STAGE_PROMPTS["architecture"].format(
            intent=json.dumps(intent, indent=2)
        ))
        architecture, err = self._parse_and_repair(client, arch_raw, "architecture", api_key)
        stages["architecture"] = architecture
        if err:
            errors.append({"stage": "architecture", "issue": err})

        # Stage 3: Schema Generation
        schema_raw = await self._call_llm(client, STAGE_PROMPTS["schema"].format(
            architecture=json.dumps(architecture, indent=2)
        ))
        schemas, err = self._parse_and_repair(client, schema_raw, "schema", api_key)
        stages["schemas"] = schemas
        if err:
            errors.append({"stage": "schema", "issue": err})

        # Stage 4: Refinement
        refined_raw = await self._call_llm(client, STAGE_PROMPTS["refinement"].format(
            intent=json.dumps(intent, indent=2),
            architecture=json.dumps(architecture, indent=2),
            schemas=json.dumps(schemas, indent=2)
        ))
        refined, err = self._parse_and_repair(client, refined_raw, "refinement", api_key)
        stages["refined_output"] = refined
        if err:
            errors.append({"stage": "refinement", "issue": err})

        # Validate cross-layer consistency
        validation_report = self._validate_consistency(refined)

        return {
            "success": True,
            "prompt": prompt,
            "stages": stages,
            "final_output": refined,
            "validation": validation_report,
            "errors_encountered": errors,
            "retries_used": sum(1 for e in errors if e)
        }

    async def _call_llm(self, client: anthropic.Anthropic, prompt: str) -> str:
        message = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=4000,
            messages=[{"role": "user", "content": prompt}]
        )
        return message.content[0].text

    def _extract_json(self, text: str) -> Any:
        text = text.strip()
        text = re.sub(r'^```(?:json)?\s*', '', text)
        text = re.sub(r'\s*```$', '', text)
        text = text.strip()
        return json.loads(text)

    def _parse_and_repair(self, client: anthropic.Anthropic, raw: str, stage: str, api_key: str):
        try:
            return self._extract_json(raw), None
        except json.JSONDecodeError as e:
            repair_prompt = f"""The following text should be valid JSON but has errors: {str(e)}

Text:
{raw}

Return ONLY the corrected valid JSON, nothing else, no markdown fences."""
            try:
                repaired = client.messages.create(
                    model="claude-sonnet-4-6",
                    max_tokens=4000,
                    messages=[{"role": "user", "content": repair_prompt}]
                ).content[0].text
                return self._extract_json(repaired), f"JSON repair needed in {stage} stage"
            except Exception as e2:
                return {"error": f"Could not parse {stage} output", "raw": raw[:500]}, str(e2)

    def _validate_consistency(self, refined: dict) -> dict:
        issues = []
        passed = []

        try:
            db = refined.get("db_schema", {})
            api = refined.get("api_schema", {})
            ui = refined.get("ui_schema", {})
            auth = refined.get("auth_schema", {})

            db_tables = {t["name"] for t in db.get("tables", [])}

            api_endpoints = [e["path"] for e in api.get("endpoints", [])]
            if api_endpoints:
                passed.append(f"{len(api_endpoints)} API endpoints generated")

            ui_pages = ui.get("pages", [])
            pages_with_routes = [p for p in ui_pages if p.get("route")]
            if len(pages_with_routes) == len(ui_pages):
                passed.append("All UI pages have routes")
            else:
                issues.append(f"{len(ui_pages) - len(pages_with_routes)} UI pages missing routes")

            auth_roles = {r["name"] for r in auth.get("roles", [])}
            for ep in api.get("endpoints", []):
                for role in ep.get("roles_allowed", []):
                    if role not in auth_roles:
                        issues.append(f"API endpoint '{ep['path']}' references undefined role '{role}'")

            if db_tables:
                passed.append(f"DB schema has {len(db_tables)} tables: {', '.join(db_tables)}")

        except Exception as e:
            issues.append(f"Validation error: {str(e)}")

        return {
            "passed": passed,
            "issues": issues,
            "is_valid": len(issues) == 0
        }
