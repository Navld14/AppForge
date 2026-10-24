import json
import re
from typing import Any
import google.generativeai as genai

MODEL_NAME = "gemini-1.5-flash"

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
  "auth_required": true,
  "payment_required": false,
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
      "fields": [{"name": "string", "type": "string", "required": true}],
      "relations": [{"entity": "string", "type": "one_to_many"}]
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
          {"name": "string", "type": "string", "nullable": false, "primary_key": true, "foreign_key": null}
        ],
        "indexes": ["list of column names to index"]
      }
    ]
  },
  "api_schema": {
    "endpoints": [
      {
        "method": "GET",
        "path": "string",
        "description": "string",
        "request_body": {},
        "response": {},
        "auth_required": true,
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
          {"type": "string", "props": {}, "data_source": null}
        ],
        "auth_required": true,
        "roles_allowed": ["string"]
      }
    ]
  },
  "auth_schema": {
    "strategy": "jwt",
    "roles": [
      {"name": "string", "inherits": null, "permissions": ["string"]}
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
  "db_schema": { ... },
  "api_schema": { ... },
  "ui_schema": { ... },
  "auth_schema": { ... },
  "refinement_notes": ["list of issues found and fixed"]
}

Intent: {intent}
Architecture: {architecture}
Schemas: {schemas}"""
}


class AppForgePipeline:

    async def run(self, prompt: str, api_key: str) -> dict:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(
            model_name=MODEL_NAME,
            generation_config={"response_mime_type": "application/json"}
        )
        stages = {}
        errors = []

        # Stage 1: Intent
        prompt_text = STAGE_PROMPTS["intent"].replace("{prompt}", prompt)
        intent_raw = await self._call_llm(model, prompt_text)
        intent, err = self._extract_json(intent_raw)
        stages["intent"] = intent
        if err:
            errors.append({"stage": "intent", "issue": err})

        # Stage 2: Architecture
        arch_prompt = STAGE_PROMPTS["architecture"].replace("{intent}", json.dumps(intent, indent=2))
        arch_raw = await self._call_llm(model, arch_prompt)
        architecture, err = self._extract_json(arch_raw)
        stages["architecture"] = architecture
        if err:
            errors.append({"stage": "architecture", "issue": err})

        # Stage 3: Schema Generation
        schema_prompt = STAGE_PROMPTS["schema"].replace("{architecture}", json.dumps(architecture, indent=2))
        schema_raw = await self._call_llm(model, schema_prompt)
        schemas, err = self._extract_json(schema_raw)
        stages["schemas"] = schemas
        if err:
            errors.append({"stage": "schema", "issue": err})

        # Stage 4: Refinement
        refined_prompt = (
            STAGE_PROMPTS["refinement"]
            .replace("{intent}", json.dumps(intent, indent=2))
            .replace("{architecture}", json.dumps(architecture, indent=2))
            .replace("{schemas}", json.dumps(schemas, indent=2))
        )
        refined_raw = await self._call_llm(model, refined_prompt)
        refined, err = self._extract_json(refined_raw)
        stages["refined_output"] = refined
        if err:
            errors.append({"stage": "refinement", "issue": err})

        validation_report = self._validate_consistency(refined)

        return {
            "success": validation_report.get("is_valid", False),
            "prompt": prompt,
            "stages": stages,
            "final_output": refined,
            "validation": validation_report,
            "errors_encountered": errors,
            "retries_used": sum(1 for e in errors if e)
        }

    async def _call_llm(self, model: genai.GenerativeModel, prompt: str) -> str:
        response = await model.generate_content_async(prompt)
        return response.text or "{}"

    def _extract_json(self, text: str) -> tuple[Any, str | None]:
        text = text.strip()
        text = re.sub(r'^```(?:json)?\s*', '', text, flags=re.MULTILINE)
        text = re.sub(r'\s*```$', '', text, flags=re.MULTILINE)
        text = text.strip()

        match = re.search(r'(\{[\s\S]*\})', text)
        if match:
            text = match.group(1)

        try:
            return json.loads(text), None
        except Exception as e:
            fallback = {
                "error": "Failed to parse JSON",
                "app_name": "App",
                "tables": [],
                "endpoints": [],
                "pages": []
            }
            return fallback, str(e)[:60]

    def _validate_consistency(self, refined: dict) -> dict:
        issues = []
        passed = []

        if not isinstance(refined, dict):
            return {"passed": [], "issues": ["Invalid refinement payload"], "is_valid": False}

        try:
            db = refined.get("db_schema", {})
            api = refined.get("api_schema", {})
            ui = refined.get("ui_schema", {})
            auth = refined.get("auth_schema", {})

            db_tables = {t.get("name") for t in db.get("tables", []) if isinstance(t, dict)}

            api_endpoints = [e.get("path") for e in api.get("endpoints", []) if isinstance(e, dict)]
            if api_endpoints:
                passed.append(f"{len(api_endpoints)} API endpoints generated")

            ui_pages = ui.get("pages", [])
            pages_with_routes = [p for p in ui_pages if isinstance(p, dict) and p.get("route")]
            if ui_pages and len(pages_with_routes) == len(ui_pages):
                passed.append("All UI pages have routes")
            elif ui_pages:
                issues.append(f"{len(ui_pages) - len(pages_with_routes)} UI pages missing routes")

            auth_roles = {r.get("name") for r in auth.get("roles", []) if isinstance(r, dict)}
            for ep in api.get("endpoints", []):
                if isinstance(ep, dict):
                    for role in ep.get("roles_allowed", []):
                        if role not in auth_roles:
                            issues.append(f"API endpoint '{ep.get('path')}' references undefined role '{role}'")

            if db_tables:
                passed.append(f"DB schema has {len(db_tables)} tables: {', '.join(filter(None, db_tables))}")

        except Exception as e:
            issues.append(f"Validation error: {str(e)}")

        return {
            "passed": passed,
            "issues": issues,
            "is_valid": len(issues) == 0 and len(passed) > 0
        }
