#!/usr/bin/env python3
"""
Test runner script for Coffee Shop WhatsApp Bot.
Provides convenient commands to run different test suites.
"""

import os
import sys
import subprocess
import argparse

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)


def run_unit_tests():
    """Run unit tests."""
    print("🧪 Running Unit Tests...")
    print("=" * 50)
    cmd = [sys.executable, '-m', 'pytest', 'tests/unit/', '-v', '--tb=short']
    return subprocess.run(cmd, cwd=project_root)


def run_integration_tests():
    """Run integration tests."""
    print("🔗 Running Integration Tests...")
    print("=" * 50)
    cmd = [sys.executable, '-m', 'pytest', 'tests/integration/', '-v', '--tb=short']
    return subprocess.run(cmd, cwd=project_root)


def run_all_tests():
    """Run all tests."""
    print("🚀 Running All Tests...")
    print("=" * 50)
    cmd = [sys.executable, '-m', 'pytest', 'tests/', '-v', '--tb=short']
    return subprocess.run(cmd, cwd=project_root)


def run_legacy_integration():
    """Run legacy integration tests (original format)."""
    print("🔄 Running Legacy Integration Tests...")
    print("=" * 50)
    
    test_files = [
        'tests/integration/test_system_integration.py',
        'tests/integration/test_clover_integration.py',
        'tests/integration/test_whatsapp_integration.py',
        'tests/integration/test_llm_integration.py'
    ]
    
    for test_file in test_files:
        if os.path.exists(os.path.join(project_root, test_file)):
            print(f"\n📋 Running {test_file}...")
            cmd = [sys.executable, test_file]
            env = os.environ.copy()
            env['PYTHONPATH'] = f"{project_root}:{project_root}/venv/lib/python3.13/site-packages"
            subprocess.run(cmd, cwd=project_root, env=env)


def main():
    """Main test runner function."""
    parser = argparse.ArgumentParser(description='Coffee Shop WhatsApp Bot Test Runner')
    parser.add_argument('test_type', choices=['unit', 'integration', 'all', 'legacy'], 
                       help='Type of tests to run')
    parser.add_argument('--verbose', '-v', action='store_true', 
                       help='Verbose output')
    
    args = parser.parse_args()
    
    if args.test_type == 'unit':
        result = run_unit_tests()
    elif args.test_type == 'integration':
        result = run_integration_tests()
    elif args.test_type == 'all':
        result = run_all_tests()
    elif args.test_type == 'legacy':
        result = run_legacy_integration()
    
    return result.returncode if hasattr(result, 'returncode') else 0


if __name__ == '__main__':
    sys.exit(main())
