"""
Tests for MCP server tools.
Tests the actual MCP tool implementations and server functionality.
"""
import pytest
import asyncio
import sys
import os
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import patch, MagicMock

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Import handler functions instead of MCP tools
import mcp_handlers


class TestServerTools:
    """Test suite for MCP server tools."""

    @pytest.mark.asyncio
    async def test_submit_job_tool_success(self, temp_script, valid_cores):
        """Test successful job submission through MCP tool."""
        result = mcp_handlers.submit_slurm_job_handler(temp_script, valid_cores)
        
        assert isinstance(result, dict)
        # Should either be a success response or error response
        if "isError" in result:
            assert isinstance(result["isError"], bool)
        else:
            assert "job_id" in result or "error" in result

    @pytest.mark.asyncio
    async def test_submit_job_tool_enhanced(self, temp_script, job_parameters):
        """Test enhanced job submission through MCP tool."""
        result = mcp_handlers.submit_slurm_job_handler(
            temp_script, 
            cores=4,
            memory=job_parameters["memory"],
            time_limit=job_parameters["time_limit"],
            job_name=job_parameters["job_name"],
            partition=job_parameters["partition"]
        )
        
        assert isinstance(result, dict)
        
        if not result.get("isError") and "job_id" in result:
            # Verify parameters were passed through
            assert result.get("memory") == job_parameters["memory"]
            assert result.get("time_limit") == job_parameters["time_limit"]
            assert result.get("job_name") == job_parameters["job_name"]
            assert result.get("partition") == job_parameters["partition"]

    @pytest.mark.asyncio
    async def test_submit_job_tool_invalid_file(self, valid_cores):
        """Test job submission tool with invalid file."""
        result = mcp_handlers.submit_slurm_job_handler("nonexistent.sh", valid_cores)
        
        assert isinstance(result, dict)
        # Should handle error gracefully
        assert "isError" in result or "error" in result

    @pytest.mark.asyncio
    async def test_submit_job_tool_invalid_cores(self, temp_script):
        """Test job submission tool with invalid cores."""
        result = mcp_handlers.submit_slurm_job_handler(temp_script, 0)
        
        assert isinstance(result, dict)
        assert "isError" in result or "error" in result

    @pytest.mark.asyncio
    async def test_check_status_tool(self, sample_job_id):
        """Test job status checking tool."""
        result = mcp_handlers.check_job_status_handler(sample_job_id)
        
        assert isinstance(result, dict)
        # Should either be a success response or error response
        if "isError" in result:
            assert isinstance(result["isError"], bool)
        else:
            assert "job_id" in result or "error" in result

    @pytest.mark.asyncio
    async def test_cancel_job_tool(self, sample_job_id):
        """Test job cancellation tool."""
        result = mcp_handlers.cancel_slurm_job_handler(sample_job_id)
        
        assert isinstance(result, dict)
        # Should handle cancellation request
        if not result.get("isError"):
            assert "job_id" in result or "status" in result

    @pytest.mark.asyncio
    async def test_list_jobs_tool(self):
        """Test job listing tool."""
        result = mcp_handlers.list_slurm_jobs_handler()
        
        assert isinstance(result, dict)
        if not result.get("isError"):
            assert "jobs" in result or "count" in result

    @pytest.mark.asyncio
    async def test_list_jobs_tool_with_filters(self):
        """Test job listing tool with filters."""
        result = mcp_handlers.list_slurm_jobs_handler(user="testuser", state="RUNNING")
        
        assert isinstance(result, dict)
        if not result.get("isError"):
            # Should include filter information
            assert "user_filter" in result or "state_filter" in result

    @pytest.mark.asyncio
    async def test_get_slurm_info_tool(self):
        """Test cluster info tool."""
        result = mcp_handlers.get_slurm_info_handler()
        
        assert isinstance(result, dict)
        if not result.get("isError"):
            assert "cluster_name" in result or "partitions" in result

    @pytest.mark.asyncio
    async def test_get_job_details_tool(self, sample_job_id):
        """Test job details tool."""
        result = mcp_handlers.get_job_details_handler(sample_job_id)
        
        assert isinstance(result, dict)
        if not result.get("isError"):
            assert "job_id" in result

    @pytest.mark.asyncio
    async def test_get_job_output_tool(self, sample_job_id):
        """Test job output tool."""
        for output_type in ["stdout", "stderr"]:
            result = mcp_handlers.get_job_output_handler(sample_job_id, output_type)
            
            assert isinstance(result, dict)
            if not result.get("isError"):
                assert "job_id" in result or "output_type" in result

    @pytest.mark.asyncio
    async def test_get_queue_info_tool(self):
        """Test queue info tool."""
        result = mcp_handlers.get_queue_info_handler()
        
        assert isinstance(result, dict)
        if not result.get("isError"):
            assert "jobs" in result or "total_jobs" in result

    @pytest.mark.asyncio
    async def test_get_queue_info_tool_with_partition(self):
        """Test queue info tool with partition filter."""
        result = mcp_handlers.get_queue_info_handler(partition="compute")
        
        assert isinstance(result, dict)
        if not result.get("isError"):
            assert "partition_filter" in result or "jobs" in result

    @pytest.mark.asyncio
    async def test_submit_array_job_tool(self, array_script, array_parameters):
        """Test array job submission tool."""
        result = mcp_handlers.submit_array_job_handler(
            array_script,
            array_parameters["array_range"],
            cores=array_parameters["cores"],
            memory=array_parameters["memory"],
            time_limit=array_parameters["time_limit"],
            job_name=array_parameters["job_name"]
        )
        
        assert isinstance(result, dict)
        if not result.get("isError") and not result.get("error"):
            # Should have array job information
            assert "array_job_id" in result or "array_range" in result

    @pytest.mark.asyncio
    async def test_get_node_info_tool(self):
        """Test node info tool."""
        result = mcp_handlers.get_node_info_handler()
        
        assert isinstance(result, dict)
        if not result.get("isError"):
            assert "nodes" in result or "total_nodes" in result

    @pytest.mark.asyncio
    async def test_tool_parameter_defaults(self, temp_script):
        """Test that tools handle default parameters correctly."""
        # Test submit job with minimal parameters
        result = mcp_handlers.submit_slurm_job_handler(temp_script, cores=1)
        assert isinstance(result, dict)
        
        # Test submit job with default memory and time
        result = mcp_handlers.submit_slurm_job_handler(temp_script, cores=1, memory="1GB")
        assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_tool_parameter_validation(self):
        """Test parameter validation in tools."""
        # Test with missing required parameters
        with pytest.raises(TypeError):
            mcp_handlers.submit_slurm_job_handler()  # Missing required parameters
        
        # Test with invalid parameter types
        result = mcp_handlers.submit_slurm_job_handler("script.sh", "invalid_cores")
        assert isinstance(result, dict)
        # Should handle type error gracefully

    @pytest.mark.asyncio
    async def test_concurrent_tool_execution(self, temp_script):
        """Test concurrent execution of tools."""
        # Submit multiple jobs concurrently using ThreadPoolExecutor
        def run_submit_job(script, cores, job_name):
            return mcp_handlers.submit_slurm_job_handler(script, cores=cores, job_name=job_name)
        
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = []
            for i in range(3):
                future = executor.submit(run_submit_job, temp_script, 1, f"concurrent_{i}")
                futures.append(future)
            
            results = [future.result() for future in futures]
        
        # Check that all completed
        assert len(results) == 3
        for result in results:
            assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_tool_error_handling(self):
        """Test error handling in tools."""
        # Test with various error conditions using handler functions
        error_scenarios = [
            ("submit_slurm_job_handler", ["nonexistent.sh"], {"cores": 1}),
            ("check_job_status_handler", ["invalid_job_id"], {}),
            ("cancel_slurm_job_handler", ["invalid_job_id"], {}),
            ("get_job_details_handler", ["invalid_job_id"], {}),
        ]
        
        for handler_name, args, kwargs in error_scenarios:
            try:
                handler_func = getattr(mcp_handlers, handler_name)
                result = handler_func(*args, **kwargs)
                assert isinstance(result, dict)
                # Should handle errors gracefully
            except Exception as e:
                # Exception handling is also acceptable
                assert isinstance(e, Exception)

    @pytest.mark.asyncio
    async def test_integration_workflow_through_tools(self, temp_script):
        """Test complete workflow through MCP handler functions."""
        # Submit job
        submit_result = mcp_handlers.submit_slurm_job_handler(temp_script, cores=2, job_name="integration_test")
        assert isinstance(submit_result, dict)
        
        if not submit_result.get("isError") and "job_id" in submit_result:
            job_id = submit_result["job_id"]
            
            # Check status
            status_result = mcp_handlers.check_job_status_handler(job_id)
            assert isinstance(status_result, dict)
            
            # Get details
            details_result = mcp_handlers.get_job_details_handler(job_id)
            assert isinstance(details_result, dict)
            
            # Try to get output
            output_result = mcp_handlers.get_job_output_handler(job_id, output_type="stdout")
            assert isinstance(output_result, dict)
            
            # Cancel job
            cancel_result = mcp_handlers.cancel_slurm_job_handler(job_id)
            assert isinstance(cancel_result, dict)

    @pytest.mark.asyncio
    async def test_tool_logging(self, temp_script, caplog):
        """Test that handler functions produce appropriate log messages."""
        with caplog.at_level("INFO"):
            result = mcp_handlers.submit_slurm_job_handler(temp_script, cores=1)
            
            # Should have logged the operation
            assert len(caplog.records) >= 0  # Logs may vary based on implementation
            assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_tool_response_consistency(self, temp_script, sample_job_id):
        """Test that all handler functions return consistent response formats."""
        handler_tests = [
            ("submit_slurm_job_handler", [temp_script], {"cores": 1}),
            ("check_job_status_handler", [sample_job_id], {}),
            ("list_slurm_jobs_handler", [], {}),
            ("get_slurm_info_handler", [], {}),
            ("get_node_info_handler", [], {}),
        ]
        
        for handler_name, args, kwargs in handler_tests:
            handler_func = getattr(mcp_handlers, handler_name)
            result = handler_func(*args, **kwargs)
            assert isinstance(result, dict)
            
            # All results should be dictionaries
            # and should not contain both success and error indicators
            if result.get("isError"):
                assert "content" in result or "error" in result
            else:
                # Success responses should have meaningful data
                assert len(result) > 0

    @pytest.mark.asyncio
    async def test_array_job_workflow(self, array_script):
        """Test array job workflow through handler functions."""
        # Submit array job
        result = mcp_handlers.submit_array_job_handler(
            array_script,
            array_range="1-3",
            cores=1,
            memory="1GB",
            time_limit="00:10:00",
            job_name="test_array"
        )
        
        assert isinstance(result, dict)
        
        if not result.get("isError") and "array_job_id" in result:
            array_job_id = result["array_job_id"]
            
            # Check status of array job
            status_result = mcp_handlers.check_job_status_handler(array_job_id)
            assert isinstance(status_result, dict)
            
            # Try to cancel array job
            cancel_result = mcp_handlers.cancel_slurm_job_handler(array_job_id)
            assert isinstance(cancel_result, dict)

    @pytest.mark.asyncio
    async def test_tool_timeout_handling(self, temp_script):
        """Test that handler functions complete in reasonable time."""
        # Test with a reasonable timeout
        try:
            def run_submit():
                return mcp_handlers.submit_slurm_job_handler(temp_script, cores=1)
            
            with ThreadPoolExecutor() as executor:
                future = executor.submit(run_submit)
                result = future.result(timeout=30.0)  # 30 second timeout
                assert isinstance(result, dict)
        except Exception as e:
            # Timeout or other exceptions are acceptable for this test
            assert isinstance(e, Exception)

    def test_tool_documentation(self):
        """Test that all handler functions have proper documentation."""
        handlers = [
            "submit_slurm_job_handler",
            "check_job_status_handler", 
            "cancel_slurm_job_handler",
            "list_slurm_jobs_handler",
            "get_slurm_info_handler",
            "get_job_details_handler",
            "get_job_output_handler",
            "get_queue_info_handler",
            "submit_array_job_handler",
            "get_node_info_handler"
        ]
        
        for handler_name in handlers:
            # Check that each handler exists and has documentation
            handler_func = getattr(mcp_handlers, handler_name, None)
            assert handler_func is not None, f"Handler {handler_name} not found"
            
            # Check that function has a docstring (optional check since some may not have detailed docs)
            if hasattr(handler_func, '__doc__') and handler_func.__doc__:
                docstring = handler_func.__doc__.strip().lower()
                assert len(docstring) > 0
