/**
 * Simple TypeScript MCP Client Example using Fetch API
 * 
 * This example uses the native fetch API to communicate with the FastMCP server.
 * This is simpler than using the MCP SDK and works directly with FastMCP's HTTP endpoints.
 * 
 * Usage:
 *   npx ts-node examples/typescript_client_simple.ts
 *   or
 *   tsx examples/typescript_client_simple.ts
 */

interface MCPRequest {
  jsonrpc: string;
  id: number;
  method: string;
  params?: Record<string, any>;
}

interface MCPResponse {
  jsonrpc: string;
  id: number;
  result?: any;
  error?: {
    code: number;
    message: string;
  };
}

class SimpleMCPClient {
  private baseUrl: string;
  private requestId: number = 1;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl;
  }

  private async sendRequest(method: string, params?: Record<string, any>): Promise<MCPResponse> {
    const request: MCPRequest = {
      jsonrpc: "2.0",
      id: this.requestId++,
      method,
      params,
    };

    try {
      const response = await fetch(`${this.baseUrl}/messages/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(request),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data: MCPResponse = await response.json();
      return data;
    } catch (error) {
      console.error("Request failed:", error);
      throw error;
    }
  }

  async listTools(): Promise<string[]> {
    const response = await this.sendRequest("tools/list");
    if (response.error) {
      throw new Error(response.error.message);
    }
    return response.result?.tools?.map((tool: any) => tool.name) || [];
  }

  async callTool(name: string, arguments_: Record<string, any>): Promise<any> {
    const response = await this.sendRequest("tools/call", {
      name,
      arguments: arguments_,
    });

    if (response.error) {
      throw new Error(response.error.message);
    }

    // Extract text content from result
    if (response.result?.content && response.result.content.length > 0) {
      const content = response.result.content[0];
      if (content.type === "text") {
        try {
          return JSON.parse(content.text);
        } catch {
          return content.text;
        }
      }
    }

    return response.result;
  }

  async readResource(uri: string): Promise<any> {
    const response = await this.sendRequest("resources/read", { uri });
    if (response.error) {
      throw new Error(response.error.message);
    }

    if (response.result?.contents && response.result.contents.length > 0) {
      const content = response.result.contents[0];
      if (content.type === "text") {
        try {
          return JSON.parse(content.text);
        } catch {
          return content.text;
        }
      }
    }

    return response.result;
  }
}

async function main() {
  const serverUrl = "http://localhost:8000";
  const client = new SimpleMCPClient(serverUrl);

  console.log("🚀 Connecting to MCP server...");
  console.log(`   URL: ${serverUrl}\n`);

  try {
    // Example 1: List available tools
    console.log("=".repeat(60));
    console.log("Example 1: List Available Tools");
    console.log("=".repeat(60));

    const tools = await client.listTools();
    console.log(`✅ Found ${tools.length} tool(s):`);
    tools.forEach((tool) => {
      console.log(`   - ${tool}`);
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

    const jobId = uploadResult.job_id;
    console.log("✅ Job description uploaded!");
    console.log(`   Job ID: ${jobId}`);
    console.log(`   Preview: ${uploadResult.text_preview?.substring(0, 100)}...`);

    // Example 3: Search for matching resumes
    console.log("\n" + "=".repeat(60));
    console.log("Example 3: Search Matching Resumes");
    console.log("=".repeat(60));

    const searchResult = await client.callTool("search_matching_resumes", {
      job_description: jobDescription,
      top_k: 3,
    });

    console.log(`✅ Found ${searchResult.total_found || 0} matches`);
    const matches = searchResult.matches || [];
    matches.forEach((match: any, index: number) => {
      console.log(`\n   Match ${index + 1}:`);
      console.log(`   - Resume ID: ${match.resume_id}`);
      console.log(`   - Similarity: ${(match.similarity_score * 100).toFixed(2)}%`);
      console.log(`   - Skills: ${match.skills?.slice(0, 5).join(", ")}`);
      console.log(`   - Experience: ${match.experience_years} years`);
    });

    // Example 4: Analyze job description
    console.log("\n" + "=".repeat(60));
    console.log("Example 4: Analyze Job Description");
    console.log("=".repeat(60));

    const analyzeResult = await client.callTool("analyze_job_description", {
      job_description: jobDescription,
    });

    const analysis = analyzeResult.analysis || {};
    console.log("✅ Analysis complete!");
    console.log(`   Required Skills: ${(analysis.required_skills || []).join(", ")}`);
    console.log(`   Experience Level: ${analysis.experience_level || "N/A"}`);
    console.log(`   Match Threshold: ${(analysis.match_threshold * 100 || 0).toFixed(2)}%`);

    // Example 5: List all job descriptions
    console.log("\n" + "=".repeat(60));
    console.log("Example 5: List All Job Descriptions");
    console.log("=".repeat(60));

    const listResult = await client.callTool("list_matched_job_descriptions", {});

    const jobs = listResult.jobs || [];
    console.log(`✅ Found ${jobs.length} job description(s)`);
    jobs.forEach((job: any) => {
      console.log(`\n   Job ID: ${job.job_id}`);
      console.log(`   - Uploaded: ${job.uploaded_at}`);
      console.log(`   - Type: ${job.input_type}`);
      console.log(`   - Has Matches: ${job.has_matches}`);
      console.log(`   - Match Count: ${job.match_count}`);
    });

    // Example 6: Read a resource
    if (jobId) {
      console.log("\n" + "=".repeat(60));
      console.log("Example 6: Read Resource (Job Description)");
      console.log("=".repeat(60));

      try {
        const resourceUri = `resume://job/${jobId}`;
        const resource = await client.readResource(resourceUri);
        console.log("✅ Resource read successfully!");
        console.log(`   Job ID: ${resource.job?.id}`);
        console.log(`   Text length: ${resource.job?.text?.length || 0} characters`);
      } catch (error) {
        console.log(`❌ Error reading resource: ${error}`);
      }
    }

    console.log("\n" + "=".repeat(60));
    console.log("✅ All examples completed!");
    console.log("=".repeat(60));
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

export { SimpleMCPClient, main };

