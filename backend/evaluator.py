import asyncio
import time
from pipeline import AppForgePipeline

EVAL_PROMPTS = [
    {"id": 1, "type": "real", "prompt": "Build a CRM with login, contacts, dashboard, role-based access, and premium plan with payments. Admins can see analytics."},
    {"id": 2, "type": "real", "prompt": "Create an e-commerce platform with product listings, shopping cart, checkout with Stripe, order tracking, and seller dashboard."},
    {"id": 3, "type": "real", "prompt": "Build a project management tool like Trello with boards, cards, drag-and-drop, team members, deadlines, and notifications."},
    {"id": 4, "type": "real", "prompt": "Create a healthcare appointment booking system with doctors, patients, scheduling, medical records, and billing."},
    {"id": 5, "type": "real", "prompt": "Build a learning management system with courses, video lessons, quizzes, student progress tracking, and certificate generation."},
    {"id": 6, "type": "real", "prompt": "Create a SaaS invoicing tool with clients, invoices, recurring billing, payment tracking, and financial reports."},
    {"id": 7, "type": "real", "prompt": "Build a food delivery app with restaurants, menus, orders, delivery tracking, reviews, and driver management."},
    {"id": 8, "type": "real", "prompt": "Create a real estate platform with property listings, search filters, virtual tours, agent profiles, and lead management."},
    {"id": 9, "type": "real", "prompt": "Build a gym management system with member check-in, class scheduling, trainer assignments, and membership plans."},
    {"id": 10, "type": "real", "prompt": "Create a social media analytics dashboard that tracks engagement, follower growth, post performance across platforms."},
    {"id": 11, "type": "edge_vague", "prompt": "Build me an app."},
    {"id": 12, "type": "edge_vague", "prompt": "I want something like Airbnb but different."},
    {"id": 13, "type": "edge_conflicting", "prompt": "Build a free app where users pay for everything. All users are admins but also no one has admin access."},
    {"id": 14, "type": "edge_conflicting", "prompt": "Create an app with no database but store everything permanently. No login required but users must be authenticated."},
    {"id": 15, "type": "edge_incomplete", "prompt": "Build a dashboard with charts."},
    {"id": 16, "type": "edge_incomplete", "prompt": "Make a login system."},
    {"id": 17, "type": "edge_vague", "prompt": "Build something for my business to manage things better."},
    {"id": 18, "type": "edge_conflicting", "prompt": "Create a real-time chat app but all messages must be stored for 10 years and also immediately deleted after reading."},
    {"id": 19, "type": "edge_incomplete", "prompt": "I need an API."},
    {"id": 20, "type": "edge_vague", "prompt": "Build an app like Netflix but for books and also it should be an app for music."},
]


class Evaluator:
    def __init__(self):
        self.pipeline = AppForgePipeline()

    async def run(self, api_key: str, max_prompts: int = 5) -> dict:
        results = []
        prompts_to_test = EVAL_PROMPTS[:max_prompts]

        for item in prompts_to_test:
            start = time.time()
            retries = 0
            success = False
            failure_type = None

            try:
                result = await self.pipeline.run(item["prompt"], api_key)
                success = result.get("success", False)
                retries = result.get("retries_used", 0)

                if not result["validation"]["is_valid"]:
                    failure_type = "validation_issues"

            except Exception as e:
                failure_type = str(e)[:100]

            latency = round(time.time() - start, 2)

            results.append({
                "id": item["id"],
                "type": item["type"],
                "prompt_preview": item["prompt"][:80] + "...",
                "success": success,
                "retries": retries,
                "failure_type": failure_type,
                "latency_seconds": latency
            })

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
            "note": f"Ran {max_prompts} of 20 prompts. Full dataset available in code."
        }
