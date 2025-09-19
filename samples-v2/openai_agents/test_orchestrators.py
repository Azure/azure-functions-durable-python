#!/usr/bin/env python3
#  Copyright (c) Microsoft Corporation. All rights reserved.
#  Licensed under the MIT License.
"""
Test script for OpenAI Agents with Durable Functions Extension
This script tests all orchestrators as specified in the instructions document.
"""

import requests
import json
import time
import argparse
import os
from typing import Dict, List, Tuple, Optional
import re

# List of orchestrators to test based on the instructions
ORCHESTRATORS = [
    "agent_lifecycle_example",
    "dynamic_system_prompt",
    "hello_world",
    "lifecycle_example", 
    "local_image",
    "non_strict_output_type",
    "previous_response_id",
    "remote_image",
    "tools",
    "message_filter",
]

BASE_URL = "http://localhost:7071/api/orchestrators"
TIMEOUT_SECONDS = 60  # Maximum time to wait for orchestration completion
POLL_INTERVAL = 2     # Seconds between status checks

def extract_status_url(orchestration_response: str) -> Optional[str]:
    """
    Extract the status query URL from orchestration response
    """
    try:
        response_data = json.loads(orchestration_response)
        return response_data.get("statusQueryGetUri")
    except:
        return None

def get_orchestration_status(status_url: str) -> Tuple[str, Optional[str], Optional[str]]:
    """
    Get the current status of an orchestration
    Returns: (runtime_status, output, error_details)
    """
    try:
        response = requests.get(status_url, timeout=10)
        if response.status_code in [200, 202]:  # Both 200 and 202 are valid responses
            status_data = json.loads(response.text)
            runtime_status = status_data.get("runtimeStatus", "Unknown")
            output = status_data.get("output")
            return runtime_status, output, None
        else:
            return "Error", None, f"HTTP {response.status_code}: {response.text}"
    except Exception as e:
        return "Error", None, f"Status check failed: {str(e)}"

def wait_for_completion(status_url: str, orchestrator_name: str) -> Tuple[str, Optional[str], Optional[str]]:
    """
    Wait for orchestration to complete and return final status
    Returns: (final_status, output, error_details)
    """
    print(f"    ⏳ Waiting for {orchestrator_name} to complete...")
    
    start_time = time.time()
    while time.time() - start_time < TIMEOUT_SECONDS:
        status, output, error = get_orchestration_status(status_url)
        
        print(f"    📊 Status: {status}")
        
        # Terminal states
        if status in ["Completed", "Failed", "Terminated", "Canceled"]:
            return status, output, error
        
        # Continue waiting for non-terminal states
        if status in ["Running", "Pending"]:
            time.sleep(POLL_INTERVAL)
            continue
        
        # Unknown status - might be an error
        if status == "Error":
            return status, output, error
            
        # Any other status, keep waiting
        time.sleep(POLL_INTERVAL)
    
    # Timeout reached
    return "Timeout", None, f"Orchestration did not complete within {TIMEOUT_SECONDS} seconds"

def test_orchestrator_full(orchestrator_name: str) -> Dict:
    """
    Test a single orchestrator end-to-end including completion
    Returns: detailed test result dictionary
    """
    print(f"\n🧪 Testing {orchestrator_name}...")
    result = {
        "name": orchestrator_name,
        "startup_success": False,
        "startup_response": None,
        "startup_error": None,
        "status_url": None,
        "instance_id": None,
        "final_status": None,
        "output": None,
        "execution_error": None,
        "execution_time": None
    }
    
    try:
        # Step 1: Start orchestration
        print(f"    🚀 Starting orchestration...")
        url = f"{BASE_URL}/{orchestrator_name}"
        start_time = time.time()
        
        response = requests.post(url, timeout=30)
        
        if response.status_code in [200, 202]:
            result["startup_success"] = True
            result["startup_response"] = response.text
            
            # Extract instance ID and status URL
            try:
                response_data = json.loads(response.text)
                result["instance_id"] = response_data.get("id")
                result["status_url"] = response_data.get("statusQueryGetUri")
                print(f"    ✅ Started successfully (Instance: {result['instance_id']})")
            except:
                print(f"    ⚠️ Started but couldn't parse response")
            
        else:
            result["startup_error"] = f"HTTP {response.status_code}: {response.text}"
            print(f"    ❌ Startup failed: {result['startup_error']}")
            return result
            
    except Exception as e:
        result["startup_error"] = f"Request failed: {str(e)}"
        print(f"    ❌ Startup failed: {result['startup_error']}")
        return result
    
    # Step 2: Wait for completion if we have a status URL
    if result["status_url"]:
        try:
            final_status, output, error = wait_for_completion(result["status_url"], orchestrator_name)
            result["final_status"] = final_status
            result["output"] = output
            result["execution_error"] = error
            result["execution_time"] = time.time() - start_time
            
            if final_status == "Completed":
                print(f"    ✅ Completed successfully in {result['execution_time']:.1f}s")
                if output:
                    print(f"    📝 Output: {str(output)[:100]}{'...' if len(str(output)) > 100 else ''}")
            elif final_status == "Failed":
                print(f"    ❌ Failed after {result['execution_time']:.1f}s")
                if error:
                    # Extract key error information
                    error_summary = str(error)[:200] + "..." if len(str(error)) > 200 else str(error)
                    print(f"    🔍 Error: {error_summary}")
            else:
                print(f"    ⚠️ Ended with status: {final_status}")
                
        except Exception as e:
            result["execution_error"] = f"Status monitoring failed: {str(e)}"
            print(f"    ❌ Status monitoring failed: {result['execution_error']}")
    else:
        print(f"    ⚠️ No status URL available for monitoring")
    
    return result

def run_all_tests() -> Dict:
    """
    Run comprehensive tests for all orchestrators and return results
    """
    print("🧪 Starting OpenAI Agents with Durable Functions Extension - Comprehensive Test Suite")
    print("=" * 80)
    
    results = {
        "test_results": [],
        "summary": {}
    }
    
    for i, orchestrator in enumerate(ORCHESTRATORS, 1):
        print(f"\n[{i}/{len(ORCHESTRATORS)}] " + "="*60)
        test_result = test_orchestrator_full(orchestrator)
        results["test_results"].append(test_result)
        
        # Small delay between tests to avoid overwhelming the system
        if i < len(ORCHESTRATORS):
            print(f"    ⏸️ Waiting {POLL_INTERVAL}s before next test...")
            time.sleep(POLL_INTERVAL)
    
    # Calculate summary statistics
    total = len(ORCHESTRATORS)
    startup_successful = sum(1 for r in results["test_results"] if r["startup_success"])
    execution_completed = sum(1 for r in results["test_results"] if r["final_status"] == "Completed")
    execution_failed = sum(1 for r in results["test_results"] if r["final_status"] == "Failed")
    execution_timeout = sum(1 for r in results["test_results"] if r["final_status"] == "Timeout")
    execution_other = sum(1 for r in results["test_results"] if r["final_status"] and r["final_status"] not in ["Completed", "Failed", "Timeout"])
    
    results["summary"] = {
        "total_tests": total,
        "startup_successful": startup_successful,
        "execution_completed": execution_completed,
        "execution_failed": execution_failed,
        "execution_timeout": execution_timeout,
        "execution_other": execution_other,
        "startup_success_rate": f"{(startup_successful/total)*100:.1f}%",
        "execution_success_rate": f"{(execution_completed/total)*100:.1f}%" if total > 0 else "0%"
    }
    
    return results

def print_report(results: Dict):
    """
    Print comprehensive test report
    """
    print("\n" + "=" * 80)
    print("📊 COMPREHENSIVE TEST VALIDATION REPORT")
    print("=" * 80)
    
    # Summary
    summary = results["summary"]
    print(f"\n📈 SUMMARY STATISTICS:")
    print(f"   Total Tests:           {summary['total_tests']}")
    print(f"   Startup Successful:    {summary['startup_successful']}/{summary['total_tests']} ({summary['startup_success_rate']})")
    print(f"   Execution Completed:   {summary['execution_completed']}/{summary['total_tests']} ({summary['execution_success_rate']})")
    print(f"   Execution Failed:      {summary['execution_failed']}")
    print(f"   Execution Timeout:     {summary['execution_timeout']}")
    print(f"   Execution Other:       {summary['execution_other']}")
    
    # Detailed results by category
    test_results = results["test_results"]
    
    # Startup successful tests
    startup_successful = [r for r in test_results if r["startup_success"]]
    if startup_successful:
        print(f"\n✅ STARTUP SUCCESSFUL ({len(startup_successful)}):")
        for test in startup_successful:
            print(f"   • {test['name']} (Instance: {test['instance_id'] or 'N/A'})")
    
    # Execution completed tests
    execution_completed = [r for r in test_results if r["final_status"] == "Completed"]
    if execution_completed:
        print(f"\n🎉 EXECUTION COMPLETED ({len(execution_completed)}):")
        for test in execution_completed:
            exec_time = f" in {test['execution_time']:.1f}s" if test['execution_time'] else ""
            print(f"   • {test['name']}{exec_time}")
            if test['output']:
                output_preview = str(test['output'])[:100] + "..." if len(str(test['output'])) > 100 else str(test['output'])
                print(f"     Output: {output_preview}")
    
    # Execution failed tests
    execution_failed = [r for r in test_results if r["final_status"] == "Failed"]
    if execution_failed:
        print(f"\n❌ EXECUTION FAILED ({len(execution_failed)}):")
        for test in execution_failed:
            exec_time = f" after {test['execution_time']:.1f}s" if test['execution_time'] else ""
            print(f"   • {test['name']}{exec_time}")
            if test['execution_error']:
                # Extract key error information
                error_lines = str(test['execution_error']).split('\\n')
                key_error = next((line for line in error_lines if 'RuntimeError:' in line or 'Exception:' in line), 
                               str(test['execution_error'])[:150])
                print(f"     Error: {key_error}")
    
    # Startup failed tests
    startup_failed = [r for r in test_results if not r["startup_success"]]
    if startup_failed:
        print(f"\n🚫 STARTUP FAILED ({len(startup_failed)}):")
        for test in startup_failed:
            print(f"   • {test['name']}")
            print(f"     Error: {test['startup_error']}")
    
    # Timeout tests
    timeout_tests = [r for r in test_results if r["final_status"] == "Timeout"]
    if timeout_tests:
        print(f"\n⏰ EXECUTION TIMEOUT ({len(timeout_tests)}):")
        for test in timeout_tests:
            print(f"   • {test['name']} (exceeded {TIMEOUT_SECONDS}s)")
    
    # Recommendations based on results
    print(f"\n💡 ANALYSIS & RECOMMENDATIONS:")
    
    if summary['execution_completed'] == summary['total_tests']:
        print("   🎉 EXCELLENT: All orchestrators completed successfully!")
        print("   • Integration is working correctly")
        print("   • Ready for production use")
    
    elif summary['startup_successful'] == summary['total_tests'] and summary['execution_failed'] > 0:
        print("   ⚠️ INFRASTRUCTURE OK, RUNTIME ISSUES DETECTED:")
        print("   • Azure Functions integration is working correctly")
        print("   • Orchestrators start successfully but fail during execution")
        
        # Analyze common error patterns
        common_errors = {}
        for test in execution_failed:
            if test['execution_error']:
                error_str = str(test['execution_error'])
                if 'event loop' in error_str.lower():
                    common_errors['AsyncIO Event Loop'] = common_errors.get('AsyncIO Event Loop', 0) + 1
                elif 'timeout' in error_str.lower():
                    common_errors['Timeout'] = common_errors.get('Timeout', 0) + 1
                elif 'openai' in error_str.lower():
                    common_errors['OpenAI API'] = common_errors.get('OpenAI API', 0) + 1
                else:
                    common_errors['Other'] = common_errors.get('Other', 0) + 1
        
        if common_errors:
            print("   • Common error patterns detected:")
            for error_type, count in common_errors.items():
                print(f"     - {error_type}: {count} occurrences")
        
        if 'AsyncIO Event Loop' in common_errors:
            print("   • SOLUTION: Implement event loop fix in sample code")
            print("     - See TEST_VALIDATION_REPORT.md for specific solutions")
    
    elif summary['startup_successful'] < summary['total_tests']:
        print("   🚨 INFRASTRUCTURE ISSUES DETECTED:")
        print("   • Some orchestrators failed to start")
        print("   • Check Azure Functions configuration")
        print("   • Verify environment variables and dependencies")
    
    else:
        print("   🔍 MIXED RESULTS - Review individual test details above")
    
    print("\n" + "=" * 80)

if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Test OpenAI Agents with Durable Functions Extension")
    parser.add_argument(
        "--output", "-o",
        default="comprehensive_test_results.json",
        help="Output file path for test results (default: comprehensive_test_results.json)"
    )
    args = parser.parse_args()
    
    # Check if Functions runtime is available
    try:
        response = requests.get("http://localhost:7071", timeout=5)
        print("✅ Azure Functions runtime is running")
    except:
        print("❌ Azure Functions runtime is not accessible at http://localhost:7071")
        print("Please ensure 'func start' is running in the project directory")
        exit(1)
    
    # Run comprehensive tests
    results = run_all_tests()
    
    # Print detailed report
    print_report(results)

    # Save results to file
    output_file = args.output
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n💾 Detailed results saved to: {os.path.basename(output_file)}")    # Exit with appropriate code
    if results["summary"]["execution_completed"] == results["summary"]["total_tests"]:
        print("🎉 All tests completed successfully!")
        exit(0)
    elif results["summary"]["startup_successful"] == results["summary"]["total_tests"]:
        print("⚠️ All orchestrators started but some failed during execution")
        exit(1)
    else:
        print("🚨 Some orchestrators failed to start")
        exit(2)
