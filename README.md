# MCP server for Obsidian

MCP server to interact with Obsidian via the Local REST API community plugin.

<a href="https://glama.ai/mcp/servers/3wko1bhuek"><img width="380" height="200" src="https://glama.ai/mcp/servers/3wko1bhuek/badge" alt="server for Obsidian MCP server" /></a>

## Components

### Tools

The server implements multiple tools to interact with Obsidian:

- list_files_in_vault: Lists all files and directories in the root directory of your Obsidian vault
- list_files_in_dir: Lists all files and directories in a specific Obsidian directory
- get_file_contents: Return the content of a single file in your vault.
- search: Search for documents matching a specified text query across all files in the vault
- patch_content: Insert content into an existing note relative to a heading, block reference, or frontmatter field.
- append_content: Append content to a new or existing file in the vault.
- delete_file: Delete a file or directory from your vault.

### Example prompts

Its good to first instruct Claude to use Obsidian. Then it will always call the tool.

The use prompts like this:
- Get the contents of the last architecture call note and summarize them
- Search for all files where Azure CosmosDb is mentioned and quickly explain to me the context in which it is mentioned
- Summarize the last meeting notes and put them into a new note 'summary meeting.md'. Add an introduction so that I can send it via email.

## Configuration

### Obsidian REST API settings

The server reads Obsidian REST API settings from environment variables. For local
development, create a `.env` file in the working directory:

```
OBSIDIAN_API_KEY=your_api_key_here
OBSIDIAN_PROTOCOL=http
OBSIDIAN_HOST=127.0.0.1
OBSIDIAN_PORT=27123
OBSIDIAN_URL=
OBSIDIAN_VERIFY_SSL=false

MCP_HOST=127.0.0.1
MCP_PORT=8000
MCP_HTTP_PATH=/mcp
```

You can also copy `.env.example` and fill in the values from the Obsidian Local
REST API plugin config.

If you prefer putting the variables directly in the MCP client config:

```json
{
  "mcp-obsidian": {
    "command": "uv",
    "args": [
      "--directory",
      "<dir_to>/mcp-obsidian",
      "run",
      "mcp-obsidian"
    ],
    "env": {
      "OBSIDIAN_API_KEY": "<your_api_key_here>",
      "OBSIDIAN_PROTOCOL": "http",
      "OBSIDIAN_HOST": "127.0.0.1",
      "OBSIDIAN_PORT": "27123",
      "MCP_HOST": "127.0.0.1",
      "MCP_PORT": "8000",
      "MCP_HTTP_PATH": "/mcp"
    }
  }
}
```
Sometimes Claude has issues detecting the location of uv / uvx. You can use `which uvx` to find and paste the full path in above config in such cases.

Note:
- You can find the API key in the Obsidian plugin config
- Default protocol is http
- Default port is 27123 if not specified
- Default host is 127.0.0.1 if not specified
- If you use https, set `OBSIDIAN_PROTOCOL=https` and usually `OBSIDIAN_PORT=27124`
- `OBSIDIAN_URL` is optional and overrides protocol, host, and port when set
- MCP web service defaults to `http://127.0.0.1:8000`
- MCP Streamable HTTP endpoint defaults to `http://127.0.0.1:8000/mcp`

## Quickstart

### Install

#### Obsidian REST API

You need the Obsidian REST API community plugin running: https://github.com/coddingtonbear/obsidian-local-rest-api

Install and enable it in the settings and copy the api key.

#### Claude Desktop

On MacOS: `~/Library/Application\ Support/Claude/claude_desktop_config.json`

On Windows: `%APPDATA%/Claude/claude_desktop_config.json`

<details>
  <summary>Development/Unpublished Servers Configuration</summary>
  
```json
{
  "mcpServers": {
    "mcp-obsidian": {
      "command": "uv",
      "args": [
        "--directory",
        "<dir_to>/mcp-obsidian",
        "run",
        "mcp-obsidian"
      ],
      "env": {
        "OBSIDIAN_API_KEY": "<your_api_key_here>",
        "OBSIDIAN_PROTOCOL": "http",
        "OBSIDIAN_HOST": "127.0.0.1",
        "OBSIDIAN_PORT": "27123",
        "MCP_HOST": "127.0.0.1",
        "MCP_PORT": "8000",
        "MCP_HTTP_PATH": "/mcp"
      }
    }
  }
}
```
</details>

<details>
  <summary>Published Servers Configuration</summary>
  
```json
{
  "mcpServers": {
    "mcp-obsidian": {
      "command": "uvx",
      "args": [
        "mcp-obsidian"
      ],
      "env": {
        "OBSIDIAN_API_KEY": "<YOUR_OBSIDIAN_API_KEY>",
        "OBSIDIAN_PROTOCOL": "http",
        "OBSIDIAN_HOST": "127.0.0.1",
        "OBSIDIAN_PORT": "27123",
        "MCP_HOST": "127.0.0.1",
        "MCP_PORT": "8000",
        "MCP_HTTP_PATH": "/mcp"
      }
    }
  }
}
```
</details>

## Development

### Building

To prepare the package for distribution:

1. Sync dependencies and update lockfile:
```bash
uv sync
```

### Running

Start the MCP HTTP service:

```bash
uv run mcp-obsidian
```

Default URLs:

- Health check: `http://127.0.0.1:8000/health`
- MCP Streamable HTTP endpoint: `http://127.0.0.1:8000/mcp`

### Debugging

For the best debugging experience, we strongly recommend using the [MCP Inspector](https://github.com/modelcontextprotocol/inspector).

You can launch the MCP Inspector via [`npm`](https://docs.npmjs.com/downloading-and-installing-node-js-and-npm) with this command:

```bash
npx @modelcontextprotocol/inspector
```

After launching, connect it to the Streamable HTTP URL: `http://127.0.0.1:8000/mcp`.

You can also watch the server logs with this command:

```bash
tail -n 20 -f ~/Library/Logs/Claude/mcp-server-mcp-obsidian.log
```
