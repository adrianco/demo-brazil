#!/usr/bin/env python3
"""
Brazilian Soccer MCP Knowledge Graph - Server Testing

CONTEXT:
This script tests the Brazilian Soccer Knowledge Graph MCP server by running
demo questions and validating responses. It ensures all tools work correctly
and can answer the 25 demo questions from the implementation guide.

PHASE: 2/3 - Enhancement/Integration
PURPOSE: MCP server implementation for Claude integration
DATA SOURCES: Neo4j graph database with Brazilian soccer data
DEPENDENCIES: mcp, neo4j, asyncio

TECHNICAL DETAILS:
- Neo4j Connection: bolt://localhost:7687 (neo4j/neo4j123)
- Graph Schema: Player, Team, Match, Competition entities
- Performance: Caching, query optimization
- Testing: Integration with demo questions

INTEGRATION:
- MCP Tools: Complete tool set for soccer data queries
- Error Handling: Graceful fallbacks
- Rate Limiting: Built-in for external APIs
"""

import asyncio
import json
import logging
import sys
from pathlib import Path
from typing import Dict, Any, List
import time

# Add the src directory to Python path for imports
src_dir = Path(__file__).parent
sys.path.insert(0, str(src_dir))

from mcp_server import BrazilianSoccerMCPServer
from mcp_server.config import DEMO_QUESTIONS, TOOL_HELP

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MCPServerTester:
    """Test the MCP server with demo questions"""

    def __init__(self):
        self.server = BrazilianSoccerMCPServer()
        self.results = []
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0

    async def setup(self):
        """Setup the test environment"""
        try:
            await self.server.connect_to_neo4j()
            logger.info("✓ Connected to Neo4j database")
            return True
        except Exception as e:
            logger.error(f"✗ Failed to connect to Neo4j: {e}")
            return False

    async def cleanup(self):
        """Cleanup test resources"""
        await self.server.close()

    async def test_tool(self, tool_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Test a specific tool with given parameters"""
        try:
            start_time = time.time()

            # Get the appropriate tool handler
            if tool_name.startswith('search_player') or tool_name.startswith('get_player'):
                result = await getattr(self.server.player_tools, tool_name)(**params)
            elif tool_name.startswith('search_team') or tool_name.startswith('get_team'):
                result = await getattr(self.server.team_tools, tool_name)(**params)
            elif tool_name.startswith('get_match') or tool_name.startswith('search_matches') or tool_name.startswith('get_head_to_head'):
                result = await getattr(self.server.match_tools, tool_name)(**params)
            elif tool_name.startswith('get_competition'):
                result = await getattr(self.server.match_tools, tool_name)(**params)
            elif tool_name.startswith('find_common') or tool_name.startswith('get_rivalry'):
                result = await getattr(self.server.analysis_tools, tool_name)(**params)
            else:
                return {"error": f"Unknown tool: {tool_name}"}

            execution_time = time.time() - start_time

            return {
                "success": True,
                "result": result,
                "execution_time": execution_time,
                "has_error": "error" in result
            }

        except Exception as e:
            execution_time = time.time() - start_time
            return {
                "success": False,
                "error": str(e),
                "execution_time": execution_time,
                "has_error": True
            }

    async def run_demo_questions(self):
        """Run all demo questions and validate responses"""
        logger.info("Starting demo questions test...")

        for question in DEMO_QUESTIONS:
            self.total_tests += 1
            question_id = question["id"]
            question_text = question["question"]
            tool_name = question["tool"]
            params = question["params"]
            expected_fields = question.get("expected_fields", [])

            logger.info(f"Testing Q{question_id}: {question_text}")
            logger.info(f"Tool: {tool_name}, Params: {params}")

            # Test the tool
            test_result = await self.test_tool(tool_name, params)

            # Validate the response
            validation_result = self.validate_response(test_result, expected_fields)

            # Record results
            result = {
                "question_id": question_id,
                "question": question_text,
                "tool": tool_name,
                "params": params,
                "test_result": test_result,
                "validation": validation_result,
                "passed": validation_result["passed"]
            }

            self.results.append(result)

            if validation_result["passed"]:
                self.passed_tests += 1
                logger.info(f"✓ Q{question_id} PASSED ({test_result['execution_time']:.2f}s)")
            else:
                self.failed_tests += 1
                logger.error(f"✗ Q{question_id} FAILED: {validation_result['reason']}")

            logger.info("-" * 80)

    def validate_response(self, test_result: Dict[str, Any], expected_fields: List[str]) -> Dict[str, Any]:
        """Validate a test response"""
        if not test_result["success"]:
            return {
                "passed": False,
                "reason": f"Tool execution failed: {test_result.get('error', 'Unknown error')}"
            }

        if test_result["has_error"]:
            return {
                "passed": False,
                "reason": f"Tool returned error: {test_result['result'].get('error', 'Unknown error')}"
            }

        result_data = test_result["result"]

        # Check if expected fields are present
        missing_fields = []
        for field in expected_fields:
            if field not in result_data:
                missing_fields.append(field)

        if missing_fields:
            return {
                "passed": False,
                "reason": f"Missing expected fields: {missing_fields}"
            }

        # Additional validation based on tool type
        if not self.validate_tool_specific(result_data, expected_fields):
            return {
                "passed": False,
                "reason": "Tool-specific validation failed"
            }

        return {
            "passed": True,
            "reason": "All validations passed"
        }

    def validate_tool_specific(self, result_data: Dict[str, Any], expected_fields: List[str]) -> bool:
        """Perform tool-specific validation"""
        # Check for common data integrity issues
        if "name" in result_data and not result_data["name"]:
            return False

        if "players" in result_data and not isinstance(result_data["players"], list):
            return False

        if "teams" in result_data and not isinstance(result_data["teams"], list):
            return False

        if "matches" in result_data and not isinstance(result_data["matches"], list):
            return False

        return True

    async def test_additional_scenarios(self):
        """Test additional scenarios beyond demo questions"""
        logger.info("Testing additional scenarios...")

        additional_tests = [
            {
                "name": "Empty search",
                "tool": "search_player",
                "params": {"name": "XYZ_NONEXISTENT"},
                "expect_empty": True
            },
            {
                "name": "Large result limit",
                "tool": "search_player",
                "params": {"name": "Silva", "limit": 50},
                "expect_results": True
            },
            {
                "name": "Team statistics",
                "tool": "get_team_stats",
                "params": {"team_name": "Flamengo"},
                "expect_stats": True
            },
            {
                "name": "Competition top scorers",
                "tool": "get_competition_top_scorers",
                "params": {"competition": "Brasileirão", "limit": 5},
                "expect_scorers": True
            }
        ]

        for test in additional_tests:
            logger.info(f"Testing: {test['name']}")
            result = await self.test_tool(test["tool"], test["params"])

            if result["success"] and not result["has_error"]:
                logger.info(f"✓ {test['name']} passed")
            else:
                logger.error(f"✗ {test['name']} failed")

    def generate_report(self) -> str:
        """Generate a test report"""
        report = []
        report.append("=" * 80)
        report.append("Brazilian Soccer MCP Server Test Report")
        report.append("=" * 80)
        report.append("")
        report.append(f"Total Tests: {self.total_tests}")
        report.append(f"Passed: {self.passed_tests}")
        report.append(f"Failed: {self.failed_tests}")
        report.append(f"Success Rate: {(self.passed_tests/self.total_tests*100):.1f}%")
        report.append("")

        # Summary by tool
        tools_summary = {}
        for result in self.results:
            tool = result["tool"]
            if tool not in tools_summary:
                tools_summary[tool] = {"passed": 0, "failed": 0}

            if result["passed"]:
                tools_summary[tool]["passed"] += 1
            else:
                tools_summary[tool]["failed"] += 1

        report.append("Results by Tool:")
        report.append("-" * 40)
        for tool, stats in tools_summary.items():
            total = stats["passed"] + stats["failed"]
            success_rate = (stats["passed"] / total * 100) if total > 0 else 0
            report.append(f"{tool}: {stats['passed']}/{total} ({success_rate:.0f}%)")

        report.append("")

        # Failed tests details
        failed_results = [r for r in self.results if not r["passed"]]
        if failed_results:
            report.append("Failed Tests:")
            report.append("-" * 40)
            for result in failed_results:
                report.append(f"Q{result['question_id']}: {result['question']}")
                report.append(f"  Tool: {result['tool']}")
                report.append(f"  Reason: {result['validation']['reason']}")
                report.append("")

        # Performance summary
        execution_times = [r["test_result"]["execution_time"] for r in self.results if r["test_result"]["success"]]
        if execution_times:
            avg_time = sum(execution_times) / len(execution_times)
            max_time = max(execution_times)
            min_time = min(execution_times)

            report.append("Performance Summary:")
            report.append("-" * 40)
            report.append(f"Average execution time: {avg_time:.2f}s")
            report.append(f"Max execution time: {max_time:.2f}s")
            report.append(f"Min execution time: {min_time:.2f}s")

        return "\n".join(report)

    async def run_all_tests(self):
        """Run all tests"""
        if not await self.setup():
            logger.error("Failed to setup test environment")
            return False

        try:
            # Run demo questions
            await self.run_demo_questions()

            # Run additional scenarios
            await self.test_additional_scenarios()

            # Generate and display report
            report = self.generate_report()
            print("\n" + report)

            # Save results to file
            results_file = src_dir / "test_results.json"
            with open(results_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "summary": {
                        "total_tests": self.total_tests,
                        "passed_tests": self.passed_tests,
                        "failed_tests": self.failed_tests,
                        "success_rate": (self.passed_tests/self.total_tests*100) if self.total_tests > 0 else 0
                    },
                    "results": self.results
                }, f, indent=2, ensure_ascii=False)

            logger.info(f"Test results saved to: {results_file}")

            return self.failed_tests == 0

        finally:
            await self.cleanup()

async def main():
    """Main test function"""
    tester = MCPServerTester()
    success = await tester.run_all_tests()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    asyncio.run(main())