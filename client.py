from fastmcp import Client
import asyncio

async def main():
    # The client will automatically handle GitHub OAuth
    async with Client("http://localhost:8000/mcp", auth="oauth") as client:
        # First-time connection will open GitHub login in your browser
        print("✓ Authenticated with GitHub!")
        
        # Test the protected tool
        result = await client.call_tool("get_user_info")
        
        # Access structured content from CallToolResult
        if result.structured_content:
            user_data = result.structured_content
            print(f"GitHub user: {user_data.get('github_user')}")
            print(f"Name: {user_data.get('name')}")
            print(f"Email: {user_data.get('email')}")
        elif result.content:
            # Fallback to text content if structured content not available
            for content in result.content:
                if hasattr(content, 'text'):
                    print(f"Result: {content.text}")
        else:
            print(f"Error: {result.isError}")

if __name__ == "__main__":
    asyncio.run(main())