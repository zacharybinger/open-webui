## Context

Model Context Protocol (MCP) clients execute server-provided tools. Currently, Open WebUI does this automatically without human intervention. This poses security and usability risks when a tool requires user consent, credentials, or additional parameters mid-execution. The MCP "Elicitation" spec provides a standard way for servers to request such information using either a "form" (JSON schema) or a "url" (external consent/OAuth flow).

## Goals / Non-Goals

**Goals:**
- Implement client support for form and url elicitation modes.
- Build dynamic UI components to render form mode primitives.
- Provide secure URL consent mechanisms.
- Support `-32042` retry after url elicitation.

**Non-Goals:**
- Supporting complex, nested JSON schemas in form mode.
- Server-side statefulness for paused requests.

## Decisions

**Decision 1: Frontend Dynamic Form Component**
*Rationale:* Create a new UI component that takes a JSON Schema (primitives only: String, Number, Boolean, Enum) and dynamically renders the appropriate HTML inputs. This ensures we flexibly support any future primitive-based server requests without hardcoding specific forms.
*Alternatives:* Hardcode common forms. Rejected because MCP servers can request arbitrary data types depending on the tool.

**Decision 2: URL Consent Link Handling**
*Rationale:* Do not pre-fetch the URL to prevent CSRF or unexpected side-effects. Display the domain prominently and require an explicit user action to open the external link in a secure context. This mitigates phishing and spoofing risks.

**Decision 3: Backend interception of `elicitation/create` and `-32042`**
*Rationale:* The backend acts as the MCP client proxy. It must intercept these requests/errors, pass them to the frontend via WebSocket/SSE, and pause its own processing or prepare to retry tool calls once it receives the frontend response or webhook.

## Risks / Trade-offs

- [Risk] Phishing via URL mode → Mitigation: Highlight the domain clearly in the UI; do not render URLs as clickable outside the consent component.
- [Risk] Server requests sensitive data via form mode → Mitigation: Display a clear warning about which server/tool is requesting the data, reminding the user not to share passwords if unexpected.
