# WhatsApp MCP Server + Voice Control (Siri)

This is a voice add on for the MCP server for WhatsApp made by Luke Harris at ElevenLabs. This demo uses the ElevenLabs technology to read out messages in your contacts and speaks out their texts with the appropriate voice. So, your WhatsApp texts can be read out loud as Siri does, but with the actual voices of your loved ones. 

With this you can search you personal Whatsapp messages, search your contacts and send messages to either individuals or groups. This add on lets you now interact with the MCP + Claude functions as you do with Siri on your iPhone: completely voice controlled. Currently optimized for reading messages. 

It connects to your **personal WhatsApp account** directly via the Whatsapp web multidevice API (using the [whatsmeow](https://github.com/tulir/whatsmeow) library). All your messages are stored locally in a SQLite database and only sent to an LLM (such as Claude) when the agent accesses them through tools (which you control).


### Prerequisites

- Go
- Python 3.6+
- Anthropic Claude Desktop app (or Cursor)
- UV (Python package manager), install with `curl -LsSf https://astral.sh/uv/install.sh | sh`
- ElevenLabs and OpenAI API keys

### Steps

1. **Clone this repository**

   ```bash
   git clone https://github.com/lharries/whatsapp-mcp.git
   cd whatsapp-mcp
   ```

2. **Run the WhatsApp bridge**

   Navigate to the whatsapp-bridge directory and run the Go application:

   ```bash
   cd whatsapp-bridge
   go run main.go
   ```

   The first time you run it, you will be prompted to scan a QR code. Scan the QR code with your WhatsApp mobile app to authenticate.

   After approximately 20 days, you will might need to re-authenticate.

3. **Connect to the MCP server**

   Copy the below json with the appropriate {{PATH}} values:

   ```json
   {
     "mcpServers": {
       "whatsapp": {
         "command": "{{PATH_TO_UV}}", // Run `which uv` and place the output here
         "args": [
           "--directory",
           "{{PATH_TO_SRC}}/whatsapp-mcp/whatsapp-mcp-server", // cd into the repo, run `pwd` and enter the output here + "/whatsapp-mcp-server"
           "run",
           "main.py"
         ]
       }
     }
   }
   ```
   **Cursor**, save this as `mcp.json` in your Cursor configuration directory at:

   ```
   ~/.cursor/mcp.json
   ```

4. **Restart Cursor**

   Restart Cursor and start! 
   
   Please note that this method is slightly different than the origional - one file is run and keeps on going until manually stopped.

### MCP Tools

Claude can access the following tools to interact with WhatsApp:

- **search_contacts**: Search for contacts by name or phone number
- **list_messages**: Retrieve messages with optional filters and context
- **list_chats**: List available chats with metadata
- **get_chat**: Get information about a specific chat
- **get_direct_chat_by_contact**: Find a direct chat with a specific contact
- **get_contact_chats**: List all chats involving a specific contact
- **get_last_interaction**: Get the most recent message with a contact
- **get_message_context**: Retrieve context around a specific message
- **send_message**: Send a WhatsApp message to a specified phone number

Please note that our Siri feature is currently only set up to to access messages, so some of these features may not function as intended.
