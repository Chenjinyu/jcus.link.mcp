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
from fastmcp import Client


async def main():
    """Main client function"""
    server_url = "http://localhost:8000/mcp"
    
    print("🚀 Connecting to MCP server...")
    print(f"   URL: {server_url}\n")
    
    async with Client(server_url) as client:
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
        
        result = await client.call_tool(
            "upload_job_description",
            arguments={
                "input_data": job_description,
                "input_type": "text"
            }
        )
        
        if result.content:
            response_data = json.loads(result.content[0].text)
            job_id = response_data.get("job_id")
            print(f"✅ Job description uploaded!")
            print(f"   Job ID: {job_id}")
            print(f"   Preview: {response_data.get('text_preview', '')[:100]}...\n")
        else:
            print(f"❌ Error: {result}")
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
        
        if result.content:
            response_data = json.loads(result.content[0].text)
            print(f"✅ Found {response_data.get('total_found', 0)} matches")
            matches = response_data.get("matches", [])
            for i, match in enumerate(matches, 1):
                print(f"\n   Match {i}:")
                print(f"   - Resume ID: {match.get('resume_id')}")
                print(f"   - Similarity: {match.get('similarity_score', 0):.2%}")
                print(f"   - Skills: {', '.join(match.get('skills', [])[:5])}")
                print(f"   - Experience: {match.get('experience_years')} years")
        else:
            print(f"❌ Error: {result}")
            return
        
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
        
        if result.content:
            response_data = json.loads(result.content[0].text)
            analysis = response_data.get("analysis", {})
            print("✅ Analysis complete!")
            print(f"   Required Skills: {', '.join(analysis.get('required_skills', []))}")
            print(f"   Experience Level: {analysis.get('experience_level', 'N/A')}")
            print(f"   Match Threshold: {analysis.get('match_threshold', 0):.2%}")
        else:
            print(f"❌ Error: {result}")
        
        # Example 4: List all job descriptions
        print("\n" + "=" * 60)
        print("Example 4: List All Job Descriptions")
        print("=" * 60)
        
        result = await client.call_tool("list_matched_job_descriptions")
        
        if result.content:
            response_data = json.loads(result.content[0].text)
            jobs = response_data.get("jobs", [])
            print(f"✅ Found {len(jobs)} job description(s)")
            for job in jobs:
                print(f"\n   Job ID: {job.get('job_id')}")
                print(f"   - Uploaded: {job.get('uploaded_at')}")
                print(f"   - Type: {job.get('input_type')}")
                print(f"   - Has Matches: {job.get('has_matches')}")
                print(f"   - Match Count: {job.get('match_count')}")
        else:
            print(f"❌ Error: {result}")
        
        # Example 5: Read a resource
        print("\n" + "=" * 60)
        print("Example 5: Read Resource (Job Description)")
        print("=" * 60)
        
        if job_id:
            resource_uri = f"resume://job/{job_id}"
            try:
                resource = await client.read_resource(resource_uri)
                if resource.contents:
                    content = json.loads(resource.contents[0].text)
                    print(f"✅ Resource read successfully!")
                    print(f"   Job ID: {content.get('job', {}).get('id')}")
                    print(f"   Text length: {len(content.get('job', {}).get('text', ''))} characters")
            except Exception as e:
                print(f"❌ Error reading resource: {e}")
        
        print("\n" + "=" * 60)
        print("✅ All examples completed!")
        print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())

