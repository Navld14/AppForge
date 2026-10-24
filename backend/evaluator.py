import asyncio
import time
from pipeline import AppForgePipeline

EVAL_PROMPTS = [
    {"id": 1, "type": "real", "prompt": "Build a CRM with login, contacts, dashboard, role-based access, and premium plan with payments. Admins can see analytics."},
    {"id": 2, "type": "real", "prompt": "Create an e-commerce platform with product listings, shopping cart, checkout with Stripe, order tracking, and seller dashboard."},
    {"id": 3, "type": "real", "prompt": "Build a project management tool like Trello with boards, cards, drag-and-drop, team members, deadlines, and notifications."},
    {"id": 4, "type": "real", "prompt": "Create a healthcare appointment booking system with doctors, patients, scheduling, medical records, and billing."},
    {"id": 5, "type": "real", "prompt": "Build a learning management system with courses, video lessons, quizzes, student progress tracking, and certificate generation."},
]

class Evaluator:
    def __init__(self):
        self.pipeline = AppForgePipeline()

    async def _test_single_prompt(self, item: dict, api_key: str) -> dict:
        start = time.time()
        retries = 0
        success = False
        failure_type = None

        try:
            # Set a 30s timeout per prompt so nothing hangs forever
            result = await asyncio.wait_for(self.pipeline.run(item["prompt"], api_key), timeout=35.0)
            success = result.get("success", False)
            retries = result.get("retries_used", 0)

            if not result.get("validation", {}).get("is_valid", False):
                failure_type = "validation_issues"

        except asyncio.TimeoutError:
            failure_type = "Request Timed Out"
        except Exception as e:
            failure_type = str(e)[:100]

        latency = round(time.time() - start, 2)

        return {
            "id": item["id"],
            "type": item["type"],
            "prompt_preview": item["prompt"][:80] + "...",
            "success": success,
            "retries": retries,
            "failure_type": failure_type,
            "latency_seconds": latency
        }

    async def run(self, api_key: str, max_prompts: int = 5) -> dict:
        prompts_to_test = EVAL_PROMPTS[:max_prompts]
        
        # Run all test prompts concurrently
        tasks = [self._test_single_prompt(item, api_key) for item in prompts_to_test]
        results = await asyncio.gather(*tasks)

        total = len(results)
        successes = sum(1 for r in results if r["success"])
        avg_latency = round(sum(r["latency_seconds"] for r in results) / total, 2)
        avg_retries = round(sum(r["retries"] for r in results) / total, 2)
        
        failure_types = {}
        for r in results:
            if r["failure_type"]:
                ft = r["failure_type"]
                failure_types[ft] = failure_types.get(ft, 0) + 1

        return {
            "summary": {
                "total_tested": total,
                "success_rate": f"{round(successes/total*100)}%",
                "avg_latency_seconds": avg_latency,
                "avg_retries_per_request": avg_retries,
                "failure_types": failure_types
            },
            "per_prompt_results": results,
            "note": f"Ran {max_prompts} prompts concurrently."
        }
