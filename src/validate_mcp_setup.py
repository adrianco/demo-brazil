#!/usr/bin/env python3
"""
Brazilian Soccer MCP Knowledge Graph - Setup Validation

CONTEXT:
This script validates that the MCP server implementation is correctly set up
and can be initialized. It performs basic checks without requiring a full
Neo4j database connection.

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

import sys
import importlib
import inspect
from pathlib import Path

# Add the src directory to Python path for imports
src_dir = Path(__file__).parent
sys.path.insert(0, str(src_dir))

def check_imports():
    """Check if all required modules can be imported"""
    print("Checking imports...")

    required_modules = [
        'mcp_server',
        'mcp_server.server',
        'mcp_server.config',
        'mcp_server.tools',
        'mcp_server.tools.player_tools',
        'mcp_server.tools.team_tools',
        'mcp_server.tools.match_tools',
        'mcp_server.tools.analysis_tools'
    ]

    failed_imports = []

    for module_name in required_modules:
        try:
            importlib.import_module(module_name)
            print(f"  ✓ {module_name}")
        except ImportError as e:
            print(f"  ✗ {module_name}: {e}")
            failed_imports.append(module_name)

    return len(failed_imports) == 0, failed_imports

def check_server_class():
    """Check if the main server class can be instantiated"""
    print("\nChecking server class...")

    try:
        from mcp_server import BrazilianSoccerMCPServer
        server = BrazilianSoccerMCPServer()
        print("  ✓ BrazilianSoccerMCPServer can be instantiated")

        # Check if server has expected attributes
        expected_attributes = ['server', 'driver', 'cache', 'player_tools', 'team_tools', 'match_tools', 'analysis_tools']
        for attr in expected_attributes:
            if hasattr(server, attr):
                print(f"  ✓ Server has attribute: {attr}")
            else:
                print(f"  ✗ Server missing attribute: {attr}")
                return False

        return True

    except Exception as e:
        print(f"  ✗ Failed to instantiate server: {e}")
        return False

def check_tool_classes():
    """Check if all tool classes can be instantiated"""
    print("\nChecking tool classes...")

    tool_classes = [
        ('mcp_server.tools.player_tools', 'PlayerTools'),
        ('mcp_server.tools.team_tools', 'TeamTools'),
        ('mcp_server.tools.match_tools', 'MatchTools'),
        ('mcp_server.tools.analysis_tools', 'AnalysisTools')
    ]

    for module_name, class_name in tool_classes:
        try:
            module = importlib.import_module(module_name)
            tool_class = getattr(module, class_name)

            # Try to instantiate with mock parameters
            instance = tool_class(driver=None, cache={})
            print(f"  ✓ {class_name} can be instantiated")

            # Check methods
            methods = [method for method in dir(instance) if not method.startswith('_') and callable(getattr(instance, method))]
            print(f"    Methods: {', '.join(methods)}")

        except Exception as e:
            print(f"  ✗ {class_name}: {e}")
            return False

    return True

def check_configuration():
    """Check configuration settings"""
    print("\nChecking configuration...")

    try:
        from mcp_server.config import Config, DEMO_QUESTIONS, TOOL_HELP

        # Check Config class
        print(f"  ✓ Config class loaded")
        print(f"  ✓ Neo4j URI: {Config.NEO4J_URI}")
        print(f"  ✓ Server name: {Config.SERVER_NAME}")
        print(f"  ✓ Cache TTL: {Config.CACHE_TTL_MINUTES} minutes")

        # Check demo questions
        print(f"  ✓ Demo questions: {len(DEMO_QUESTIONS)} configured")

        # Check tool help
        print(f"  ✓ Tool help: {len(TOOL_HELP)} tools documented")

        # Validate configuration
        Config.validate()
        print("  ✓ Configuration validation passed")

        return True

    except Exception as e:
        print(f"  ✗ Configuration check failed: {e}")
        return False

def check_entry_points():
    """Check if entry point scripts are properly configured"""
    print("\nChecking entry points...")

    scripts = [
        'run_mcp_server.py',
        'test_mcp_server.py',
        'validate_mcp_setup.py'
    ]

    for script in scripts:
        script_path = src_dir / script
        if script_path.exists():
            print(f"  ✓ {script} exists")

            # Check if file is executable
            if script_path.stat().st_mode & 0o111:
                print(f"    ✓ {script} is executable")
            else:
                print(f"    ! {script} is not executable (run: chmod +x {script})")
        else:
            print(f"  ✗ {script} missing")
            return False

    return True

def check_dependencies():
    """Check external dependencies"""
    print("\nChecking external dependencies...")

    required_packages = [
        'neo4j',
        'mcp',
        'asyncio'
    ]

    for package in required_packages:
        try:
            importlib.import_module(package)
            print(f"  ✓ {package}")
        except ImportError:
            print(f"  ✗ {package} (install with: pip install {package})")
            return False

    return True

def main():
    """Main validation function"""
    print("Brazilian Soccer MCP Server - Setup Validation")
    print("=" * 60)

    checks = [
        ("External Dependencies", check_dependencies),
        ("Module Imports", check_imports),
        ("Server Class", check_server_class),
        ("Tool Classes", check_tool_classes),
        ("Configuration", check_configuration),
        ("Entry Points", check_entry_points)
    ]

    passed = 0
    total = len(checks)

    for check_name, check_func in checks:
        print(f"\n[{check_name}]")
        if check_func():
            passed += 1
            print(f"  ✓ {check_name} passed")
        else:
            print(f"  ✗ {check_name} failed")

    print("\n" + "=" * 60)
    print(f"Validation Results: {passed}/{total} checks passed")

    if passed == total:
        print("🎉 All checks passed! MCP server is ready to run.")
        print("\nNext steps:")
        print("1. Ensure Neo4j is running on bolt://localhost:7687")
        print("2. Run: python run_mcp_server.py --test-connection")
        print("3. Start server: python run_mcp_server.py")
        return True
    else:
        print("❌ Some checks failed. Please fix the issues above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)