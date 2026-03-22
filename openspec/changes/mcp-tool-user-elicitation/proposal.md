## Why

Currently, Open WebUI executes Model Context Protocol (MCP) tool calls straight through, without human-in-the-loop safeguards. Implementing MCP's standard "Elicitation" flow allows servers to pause execution and request user approval, providing critical security approvals, out-of-band authorization, and dynamic workflows.

## What Changes

- Implement client-side support for both `form` and `url` MCP elicitation modes.
- Add a dynamic UI chat component capable of rendering restricted JSON schema primitives (String, Number, Boolean, Enum) for the form mode.
- Implement secure URL handling and consent components for external OAuth/payment flows.
- Intercept `-32042` error code (`URLElicitationRequiredError`) and optionally wait for `notifications/elicitation/complete` webhook.
- Provide a structured response routing (Accept/Decline/Cancel) to the remote MCP server.

## Capabilities

### New Capabilities
- `mcp-elicitation`: Core capability covering client support for MCP form and URL elicitation, routing, and user consent prompts.

### Modified Capabilities

## Impact

- Frontend: New UI components for form rendering and URL consent prompts in the chat interface. State management for pausing/resuming tool calls based on user input.
- Backend: Changes to MCP client connection handling to declare `elicitation` capabilities, intercept `elicitation/create` requests, and handle `-32042` errors.
