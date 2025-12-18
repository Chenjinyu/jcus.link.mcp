from fastmcp import FastMCP
from fastmcp.server.auth.providers.github import GitHubProvider

# The GitHubProvider handles GitHub's token format and validation
auth_provider = GitHubProvider(
    client_id="Ov23liaQglKtHJCuIRsp",  # Your GitHub OAuth App Client ID
    client_secret="a7e24f3131eb9748ee23bd49f392dc95b2d2956d",     # Your GitHub OAuth App Client Secret
    base_url="http://localhost:8000",   # Must match your OAuth App configuration
    # redirect_path="/auth/callback"   # Default value, customize if needed
)

mcp = FastMCP(name="GitHub Secured App", auth=auth_provider)

# Add a protected tool to test authentication
@mcp.tool
async def get_user_info() -> dict:
    """Returns information about the authenticated GitHub user."""
    from fastmcp.server.dependencies import get_access_token
    
    token = get_access_token()
    if token is None:
        return {
            "error": "Not authenticated",
            "github_user": None,
            "name": None,
            "email": None
        }
    
    # The GitHubProvider stores user data in token claims
    # Access claims safely with getattr in case it's not present
    claims = getattr(token, "claims", {})
    return {
        "github_user": claims.get("login") if isinstance(claims, dict) else None,
        "name": claims.get("name") if isinstance(claims, dict) else None,
        "email": claims.get("email") if isinstance(claims, dict) else None
    }