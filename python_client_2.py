#!/usr/bin/env python3
"""
FastMCP Python Client Example

This example demonstrates how to connect to the MCP server and use its tools.

Prerequisites:
    pip install fastmcp
    or
    uv add fastmcp
"""
import asyncio
import json
import traceback
from typing import List, cast, Any
from fastmcp import Client
from fastmcp.client.client import CallToolResult, ResourceTask
from fastmcp.client.tasks import ToolTask
from mcp.types import Tool, TextContent, TextResourceContents, BlobResourceContents
from fastmcp.exceptions import ToolError


async def main():
    """Main client function"""
    server_url = "http://localhost:8000/mcp"
    
    print("🚀 Connecting to MCP server...")
    print(f"   URL: {server_url}\n")
    
    client = Client(server_url)
    
    # list all tools
    async with client:
        try:
            tools: List[Tool]= await client.list_tools()
            for tool in tools:
                print(f"[JC] Tool descrption: {tool.description}")
                print(f"[JC] Tool: {tool.name} - {tool.description}")
            # fileter tools by tag
        except ToolError as e:
            print(f"❌ Error listing tools: {e}")
            return

    # call tools
    async with client:
        print("✅ Connected to MCP server!\n")
        
        # Example 1: Upload a job description
        print("=" * 60)
        print("Example 1: Upload Job Description")
        print("=" * 60)
        
        job_description = """
        We are looking for a Senior Python Developer with experience in:
        - FastAPI and async programming
        - LangChain and LLM integration
        - Vector databases (Supabase, ChromaDB)
        - MCP (Model Context Protocol)
        - 5+ years of Python experience
        """
        
        result: CallToolResult | ToolTask = await client.call_tool(
            "upload_job_description",
            arguments={
                "input_data": job_description,
                "input_type": "text"
            }
        )
        
        # Check for errors first (use getattr for type safety)
        if getattr(result, 'is_error', False):
            print(f"❌ Error: {result.content}")
            return
        
        # Parse response - check if content exists and is TextContent
        if result.content and len(result.content) > 0:
            content = result.content[0]
            if isinstance(content, TextContent):
                response_data = json.loads(content.text)
                job_id = response_data.get("job_id")
                print(f"✅ Job description uploaded!")
                print(f"   Job ID: {job_id}")
                print(f"   Preview: {response_data.get('text_preview', '')[:100]}...\n")
            else:
                print(f"❌ Unexpected content type: {type(content)}")
                return
        else:
            print(f"❌ No content in response")
            return
        
        # Example 2: Search for matching resumes
        print("=" * 60)
        print("Example 2: Search Matching Resumes")
        print("=" * 60)
        
        result = await client.call_tool(
            "search_matching_resumes",
            arguments={
                "job_description": job_description,
                "top_k": 3
            }
        )
        
        if getattr(result, 'is_error', False):
            print(f"❌ Error: {result.content}")
            return
        
        if result.content and len(result.content) > 0:
            content = result.content[0]
            if isinstance(content, TextContent):
                response_data = json.loads(content.text)
                print(f"✅ Found {response_data.get('total_found', 0)} matches")
                matches = response_data.get("matches", [])
                for i, match in enumerate(matches, 1):
                    print(f"\n   Match {i}:")
                    print(f"   - Resume ID: {match.get('resume_id')}")
                    print(f"   - Similarity: {match.get('similarity_score', 0):.2%}")
                    print(f"   - Skills: {', '.join(match.get('skills', [])[:5])}")
                    print(f"   - Experience: {match.get('experience_years')} years")
            else:
                print(f"❌ Unexpected content type: {type(content)}")
        else:
            print(f"❌ No content in response")
        
        # Example 3: Analyze job description
        print("\n" + "=" * 60)
        print("Example 3: Analyze Job Description")
        print("=" * 60)
        
        result = await client.call_tool(
            "analyze_job_description",
            arguments={
                "job_description": job_description
            }
        )
        
        if getattr(result, 'is_error', False):
            print(f"❌ Error: {result.content}")
        elif result.content and len(result.content) > 0:
            content = result.content[0]
            if isinstance(content, TextContent):
                response_data = json.loads(content.text)
                analysis = response_data.get("analysis", {})
                print("✅ Analysis complete!")
                print(f"   Required Skills: {', '.join(analysis.get('required_skills', []))}")
                print(f"   Experience Level: {analysis.get('experience_level', 'N/A')}")
                print(f"   Match Threshold: {analysis.get('match_threshold', 0):.2%}")
            else:
                print(f"❌ Unexpected content type: {type(content)}")
        else:
            print(f"❌ No content in response")
        
        # Example 4: List all job descriptions
        print("\n" + "=" * 60)
        print("Example 4: List All Job Descriptions")
        print("=" * 60)
        
        result = await client.call_tool("list_matched_job_descriptions")
        
        if getattr(result, 'is_error', False):
            print(f"❌ Error: {result.content}")
        elif result.content and len(result.content) > 0:
            content = result.content[0]
            if isinstance(content, TextContent):
                response_data = json.loads(content.text)
                jobs = response_data.get("jobs", [])
                print(f"✅ Found {len(jobs)} job description(s)")
                for job in jobs:
                    print(f"\n   Job ID: {job.get('job_id')}")
                    print(f"   - Uploaded: {job.get('uploaded_at')}")
                    print(f"   - Type: {job.get('input_type')}")
                    print(f"   - Has Matches: {job.get('has_matches')}")
                    print(f"   - Match Count: {job.get('match_count')}")
            else:
                print(f"❌ Unexpected content type: {type(content)}")
        else:
            print(f"❌ No content in response")
        
        # Example 5: Read a resources
        print("\n" + "=" * 60)
        print("Example 5: Read Resource (Job Description)")
        print("=" * 60)
        
        if job_id:
            resource_uri = f"resume://job/{job_id}"
            try:
                resources = await client.read_resource(resource_uri)
                print("type:", type(resources))
                print("repr:", repr(resources))
                print("dir:", dir(resources))
                
                # try multiple common shapes
                if hasattr(resources, "contents"):
                    contents = resources.contents # type: ignore
                elif hasattr(resources, "content"):
                    contents = resources.content # type: ignore
                elif isinstance(resources, dict) and "contents" in resources:
                    contents = resources.get("contents")
                elif isinstance(resources, (list, tuple)):
                    contents = list(resources)
                else:
                    raise RuntimeError(f"Unexpected read_resource result shape: {type(resources)} {resources!r}")

                if not contents:
                    print("❌ No contents in resources response")
                else:
                    content = contents[0]

                    if TextContent and isinstance(content, TextContent):
                        data = json.loads(content.text)
                    elif isinstance(content, dict) and "text" in content:
                        data = json.loads(content["text"])
                    elif hasattr(content, 'text'):
                        data = json.loads(getattr(content, 'text'))
                        # You know it has text, tell the type checker
                        # text_values = cast(Any, content).text  
                        # data = json.loads(text_values)  
                    else:
                        # fallback: print and inspect
                        print("Unexpected content type:", type(content), content)
                        raise RuntimeError("Unhandled content shape")

                    # now use `data` as before
                    print(f"✅ Resource read successfully! Job ID: {data.get('job', {}).get('id')}")
            except Exception as e:
                print(f"❌ Error reading resources: {traceback.format_exc()}")
        
        print("\n" + "=" * 60)
        print("✅ All examples completed!")
        print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())

