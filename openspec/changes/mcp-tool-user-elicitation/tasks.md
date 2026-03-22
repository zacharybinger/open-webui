## 1. Backend MCP Client Updates

- [ ] 1.1 Declare `elicitation` capabilities (`form` and `url`) in MCP initialization
- [ ] 1.2 Intercept `elicitation/create` JSON-RPC requests from the server
- [ ] 1.3 Route elicitation requests to the frontend via WebSocket/SSE
- [ ] 1.4 Intercept `-32042` (`URLElicitationRequiredError`) during tool execution and route to frontend
- [ ] 1.5 Implement response routing (Accept/Decline/Cancel) back to the MCP server
- [ ] 1.6 Support pausing and resuming tool execution awaiting elicitation response

## 2. Frontend UI Components

- [ ] 2.1 Create dynamic JSON Schema form renderer component for primitive types (String, Number, Boolean, Enum)
- [ ] 2.2 Create URL consent component to securely display domains and request user actions
- [ ] 2.3 Integrate elicitation UI components into the chat interface
- [ ] 2.4 Handle Webhook/SSE events to trigger elicitation modals/inline UI
- [ ] 2.5 Emit Accept/Decline/Cancel events back to the backend
