/**
 * TypeScript MCP Client Example
 * 
 * This example demonstrates how to connect to the MCP server using TypeScript/JavaScript
 * and interact with its tools and resources.
 * 
 * Prerequisites:
 *   npm install @modelcontextprotocol/sdk
 * 
 * Usage:
 *   npx ts-node examples/typescript_client.ts
 *   or
 *   tsx examples/typescript_client.ts
 */

import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { StdioClientTransport } from "@modelcontextprotocol/sdk/client/stdio.js";
import { SSEClientTransport } from "@modelcontextprotocol/sdk/client/sse.js";

// For HTTP/SSE transport (recommended for FastMCP)
async function createSSEClient(serverUrl: string): Promise<Client> {
  const transport = new SSEClientTransport(
    new URL(serverUrl),
    {
      method: "GET",
    }
  );
  
  const client = new Client(
    {
      name: "typescript-mcp-client",
      version: "1.0.0",
    },
    {
      capabilities: {},
    }
  );
  
  await client.connect(transport);
  return client;
}

// Alternative: For HTTP POST transport
async function createHTTPClient(serverUrl: string): Promise<Client> {
  // Note: You may need to use a custom transport for HTTP POST
  // This is a simplified example - adjust based on your FastMCP server setup
  const transport = new SSEClientTransport(
    new URL(serverUrl),
    {
      method: "POST",
    }
  );
  
  const client = new Client(
    {
      name: "typescript-mcp-client",
      version: "1.0.0",
    },
    {
      capabilities: {},
    }
  );
  
  await client.connect(transport);
  return client;
}

async function main() {
  const serverUrl = "http://localhost:8000/mcp";
  
  console.log("🚀 Connecting to MCP server...");
  console.log(`   URL: ${serverUrl}\n`);
  
  try {
    // Create client (using SSE transport for FastMCP)
    const client = await createSSEClient(serverUrl);
    
    console.log("✅ Connected to MCP server!\n");
    
    // Initialize the connection
    await client.initialize();
    
    // Example 1: List available tools
    console.log("=".repeat(60));
    console.log("Example 1: List Available Tools");
    console.log("=".repeat(60));
    
    const tools = await client.listTools();
    console.log(`✅ Found ${tools.tools.length} tool(s):`);
    tools.tools.forEach((tool) => {
      console.log(`   - ${tool.name}: ${tool.description}`);
    });
    
    // Example 2: Upload a job description
    console.log("\n" + "=".repeat(60));
    console.log("Example 2: Upload Job Description");
    console.log("=".repeat(60));
    
    const jobDescription = `
      We are looking for a Senior Python Developer with experience in:
      - FastAPI and async programming
      - LangChain and LLM integration
      - Vector databases (Supabase, ChromaDB)
      - MCP (Model Context Protocol)
      - 5+ years of Python experience
    `;
    
    const uploadResult = await client.callTool("upload_job_description", {
      input_data: jobDescription,
      input_type: "text",
    });
    
    let jobId: string | undefined;
    
    if (uploadResult.content && uploadResult.content.length > 0) {
      const content = uploadResult.content[0];
      if (content.type === "text") {
        const responseData = JSON.parse(content.text);
        jobId = responseData.job_id;
        console.log("✅ Job description uploaded!");
        console.log(`   Job ID: ${jobId}`);
        console.log(`   Preview: ${responseData.text_preview?.substring(0, 100)}...`);
      }
    }
    
    // Example 3: Search for matching resumes
    console.log("\n" + "=".repeat(60));
    console.log("Example 3: Search Matching Resumes");
    console.log("=".repeat(60));
    
    const searchResult = await client.callTool("search_matching_resumes", {
      job_description: jobDescription,
      top_k: 3,
    });
    
    if (searchResult.content && searchResult.content.length > 0) {
      const content = searchResult.content[0];
      if (content.type === "text") {
        const responseData = JSON.parse(content.text);
        console.log(`✅ Found ${responseData.total_found || 0} matches`);
        const matches = responseData.matches || [];
        matches.forEach((match: any, index: number) => {
          console.log(`\n   Match ${index + 1}:`);
          console.log(`   - Resume ID: ${match.resume_id}`);
          console.log(`   - Similarity: ${(match.similarity_score * 100).toFixed(2)}%`);
          console.log(`   - Skills: ${match.skills?.slice(0, 5).join(", ")}`);
          console.log(`   - Experience: ${match.experience_years} years`);
        });
      }
    }
    
    // Example 4: Analyze job description
    console.log("\n" + "=".repeat(60));
    console.log("Example 4: Analyze Job Description");
    console.log("=".repeat(60));
    
    const analyzeResult = await client.callTool("analyze_job_description", {
      job_description: jobDescription,
    });
    
    if (analyzeResult.content && analyzeResult.content.length > 0) {
      const content = analyzeResult.content[0];
      if (content.type === "text") {
        const responseData = JSON.parse(content.text);
        const analysis = responseData.analysis || {};
        console.log("✅ Analysis complete!");
        console.log(`   Required Skills: ${(analysis.required_skills || []).join(", ")}`);
        console.log(`   Experience Level: ${analysis.experience_level || "N/A"}`);
        console.log(`   Match Threshold: ${(analysis.match_threshold * 100 || 0).toFixed(2)}%`);
      }
    }
    
    // Example 5: List all job descriptions
    console.log("\n" + "=".repeat(60));
    console.log("Example 5: List All Job Descriptions");
    console.log("=".repeat(60));
    
    const listResult = await client.callTool("list_matched_job_descriptions", {});
    
    if (listResult.content && listResult.content.length > 0) {
      const content = listResult.content[0];
      if (content.type === "text") {
        const responseData = JSON.parse(content.text);
        const jobs = responseData.jobs || [];
        console.log(`✅ Found ${jobs.length} job description(s)`);
        jobs.forEach((job: any) => {
          console.log(`\n   Job ID: ${job.job_id}`);
          console.log(`   - Uploaded: ${job.uploaded_at}`);
          console.log(`   - Type: ${job.input_type}`);
          console.log(`   - Has Matches: ${job.has_matches}`);
          console.log(`   - Match Count: ${job.match_count}`);
        });
      }
    }
    
    // Example 6: Read a resource
    if (jobId) {
      console.log("\n" + "=".repeat(60));
      console.log("Example 6: Read Resource (Job Description)");
      console.log("=".repeat(60));
      
      try {
        const resourceUri = `resume://job/${jobId}`;
        const resource = await client.readResource({ uri: resourceUri });
        
        if (resource.contents && resource.contents.length > 0) {
          const content = resource.contents[0];
          if (content.type === "text") {
            const responseData = JSON.parse(content.text);
            console.log("✅ Resource read successfully!");
            console.log(`   Job ID: ${responseData.job?.id}`);
            console.log(`   Text length: ${responseData.job?.text?.length || 0} characters`);
          }
        }
      } catch (error) {
        console.log(`❌ Error reading resource: ${error}`);
      }
    }
    
    console.log("\n" + "=".repeat(60));
    console.log("✅ All examples completed!");
    console.log("=".repeat(60));
    
    // Close the connection
    await client.close();
    
  } catch (error) {
    console.error("❌ Error:", error);
    process.exit(1);
  }
}

// Run the example
if (require.main === module) {
  main().catch((error) => {
    console.error("Fatal error:", error);
    process.exit(1);
  });
}

export { main, createSSEClient, createHTTPClient };

