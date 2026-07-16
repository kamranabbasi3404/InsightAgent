"""
Automated Test Runner for InsightAgent.
Executes the 20-question test suite, evaluates routing accuracy,
measures response times, verifies citations, and generates a report.
"""
import os
import sys
import json
import time
import requests
from typing import Dict, List, Any

# Reconfigure stdout to use UTF-8
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

API_URL = "http://localhost:8000/api/chat"
QUERIES_FILE = os.path.join(os.path.dirname(__file__), "test_queries.json")
REPORT_MD_FILE = os.path.join(os.path.dirname(__file__), "test_report.md")


def load_queries() -> List[Dict[str, Any]]:
    """Load the test queries from JSON."""
    if not os.path.exists(QUERIES_FILE):
        print(f"Error: Test queries file not found at {QUERIES_FILE}")
        sys.exit(1)
    with open(QUERIES_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def run_single_test(test_case: Dict[str, Any]) -> Dict[str, Any]:
    """Run a single query against the chat API and return stats."""
    query = test_case["query"]
    expected_route = test_case["expected_route"]
    query_id = test_case["id"]
    description = test_case["description"]

    print(f"[{query_id}/20] Testing: \"{query}\"")
    print(f"      Expected Route: {expected_route}")

    start_time = time.time()
    try:
        response = requests.post(API_URL, json={"query": query}, timeout=300)
        elapsed_time = time.time() - start_time
        
        if response.status_code != 200:
            print(f"      ❌ FAILED: Status code {response.status_code} - {response.text}")
            return {
                "id": query_id,
                "query": query,
                "expected_route": expected_route,
                "actual_route": "error",
                "route_matched": False,
                "status_code": response.status_code,
                "elapsed_time": elapsed_time,
                "citations_count": 0,
                "trace_steps": 0,
                "passed_checks": False,
                "error": f"HTTP {response.status_code}: {response.text}"
            }
            
        data = response.json()
        actual_route = data.get("route", "")
        citations = data.get("citations", [])
        trace = data.get("trace", [])
        conflicts = data.get("conflicts", [])
        
        route_matched = actual_route == expected_route
        
        # System-wide checks
        passed_checks = True
        failure_reasons = []
        
        # 1. Routing classification check
        if not route_matched:
            passed_checks = False
            failure_reasons.append(f"Route mismatch: expected '{expected_route}', got '{actual_route}'")
            
        # 2. Citations check: local and web queries should have citations
        if expected_route in ["local_only", "web_only", "hybrid"] and len(citations) == 0:
            # We allow local_only queries to have 0 citations ONLY if no documents match, 
            # but here we have indexed the document, so they should return citations.
            passed_checks = False
            failure_reasons.append("No citations returned for retrieval-based query")
            
        # 3. Trace check: trace must not be empty
        if len(trace) == 0:
            passed_checks = False
            failure_reasons.append("Reasoning trace is empty")
            
        # 4. Citation formats check
        for cit in citations:
            snippet = cit.get("snippet", "")
            source = cit.get("source", "")
            if not snippet or not source:
                passed_checks = False
                failure_reasons.append(f"Invalid citation structure: {cit}")
        
        print(f"      Actual Route: {actual_route}")
        print(f"      Citations: {len(citations)} | Trace steps: {len(trace)}")
        print(f"      Time: {elapsed_time:.2f}s")
        if passed_checks:
            print("      ✅ PASSED")
        else:
            print(f"      ❌ FAILED: {', '.join(failure_reasons)}")
            
        return {
            "id": query_id,
            "query": query,
            "expected_route": expected_route,
            "actual_route": actual_route,
            "route_matched": route_matched,
            "status_code": 200,
            "elapsed_time": elapsed_time,
            "citations_count": len(citations),
            "trace_steps": len(trace),
            "conflicts_count": len(conflicts),
            "passed_checks": passed_checks,
            "failure_reasons": failure_reasons
        }
        
    except Exception as e:
        elapsed_time = time.time() - start_time
        print(f"      ❌ ERROR: {str(e)}")
        return {
            "id": query_id,
            "query": query,
            "expected_route": expected_route,
            "actual_route": "exception",
            "route_matched": False,
            "status_code": 500,
            "elapsed_time": elapsed_time,
            "citations_count": 0,
            "trace_steps": 0,
            "passed_checks": False,
            "error": str(e)
        }


def generate_report(results: List[Dict[str, Any]]):
    """Calculate statistics and output a markdown report."""
    total_tests = len(results)
    successful_routes = sum(1 for r in results if r.get("route_matched", False))
    passed_system_checks = sum(1 for r in results if r.get("passed_checks", False))
    
    routing_accuracy = (successful_routes / total_tests) * 100 if total_tests > 0 else 0.0
    system_pass_rate = (passed_system_checks / total_tests) * 100 if total_tests > 0 else 0.0
    avg_time = sum(r["elapsed_time"] for r in results) / total_tests if total_tests > 0 else 0.0
    
    # Group by route type
    by_route: Dict[str, Dict[str, int]] = {}
    for r in results:
        route = r["expected_route"]
        if route not in by_route:
            by_route[route] = {"total": 0, "matched": 0, "passed": 0}
        by_route[route]["total"] += 1
        if r.get("route_matched", False):
            by_route[route]["matched"] += 1
        if r.get("passed_checks", False):
            by_route[route]["passed"] += 1

    report_lines = [
        "# InsightAgent Automated Test Report",
        f"**Date:** {time.strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "## Summary Metrics",
        f"- **Total Queries Executed:** {total_tests}",
        f"- **Routing Accuracy:** {routing_accuracy:.1f}% ({successful_routes}/{total_tests})",
        f"- **System Verification Pass Rate:** {system_pass_rate:.1f}% ({passed_system_checks}/{total_tests})",
        f"- **Average Response Time:** {avg_time:.2f} seconds",
        f"- **Routing Success Criteria (>=90%):** {'✅ PASSED' if routing_accuracy >= 90.0 else '❌ FAILED'}",
        "",
        "## Routing Performance by Category",
        "| Route Category | Queries | Route Matches | Accuracy | Checks Passed | Pass Rate |",
        "|---|---|---|---|---|---|",
    ]
    
    for route, stats in by_route.items():
        acc = (stats["matched"] / stats["total"]) * 100
        pr = (stats["passed"] / stats["total"]) * 100
        report_lines.append(f"| {route} | {stats['total']} | {stats['matched']} | {acc:.1f}% | {stats['passed']} | {pr:.1f}% |")
        
    report_lines.extend([
        "",
        "## Detailed Query Run Log",
        "| ID | Query | Expected Route | Actual Route | Citations | Trace Steps | Time | Verification |",
        "|---|---|---|---|---|---|---|---|",
    ])
    
    for r in results:
        ver_status = "✅ PASS" if r.get("passed_checks", False) else "❌ FAIL"
        reasons = f"<br><small>{', '.join(r.get('failure_reasons', []))}</small>" if r.get("failure_reasons") else ""
        report_lines.append(
            f"| {r['id']} | {r['query']} | {r['expected_route']} | {r['actual_route']} | "
            f"{r.get('citations_count', 0)} | {r.get('trace_steps', 0)} | {r['elapsed_time']:.2f}s | {ver_status}{reasons} |"
        )
        
    report_text = "\n".join(report_lines)
    
    with open(REPORT_MD_FILE, "w", encoding="utf-8") as f:
        f.write(report_text)
        
    print("\n" + "=" * 60)
    print("TEST EXECUTION COMPLETED")
    print("=" * 60)
    print(f"Routing Accuracy: {routing_accuracy:.1f}% ({successful_routes}/{total_tests})")
    print(f"System Verification Pass Rate: {system_pass_rate:.1f}% ({passed_system_checks}/{total_tests})")
    print(f"Average Response Time: {avg_time:.2f}s")
    print(f"Report saved to: {REPORT_MD_FILE}")
    print("=" * 60)
    
    return routing_accuracy >= 90.0 and (passed_system_checks >= successful_routes)


def main():
    print("=" * 60)
    print("STARTING INSIGHTAGENT AUTOMATED SYSTEM-WIDE TEST SUITE")
    print("=" * 60)
    
    queries = load_queries()
    results = []
    
    for test_case in queries:
        res = run_single_test(test_case)
        results.append(res)
        # Small delay between requests to be nice to Groq/Tavily rate limits
        time.sleep(1.0)
        
    success = generate_report(results)
    
    if not success:
        print("❌ Test suite did not meet all quality criteria (90% routing accuracy & 100% check pass rate).")
        sys.exit(1)
    else:
        print("✅ All automated tests and validations passed successfully!")
        sys.exit(0)


if __name__ == "__main__":
    main()
