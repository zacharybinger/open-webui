## ADDED Requirements

### Requirement: Elicitation Capability Declaration
The system SHALL declare support for "form" and "url" elicitation modes during MCP initialization.

#### Scenario: Client connects to MCP server
- **WHEN** the Open WebUI client initializes a connection to an MCP server
- **THEN** it sends a capabilities object containing `elicitation` with `form: {}` and `url: {}`

### Requirement: Form Elicitation Handling
The system SHALL intercept `elicitation/create` requests with `form` mode and render a dynamic UI.

#### Scenario: Server requests form data
- **WHEN** the server sends an `elicitation/create` request with a `requestedSchema` containing primitive types
- **THEN** the client displays a form matching the schema
- **AND** submits the user's valid input as the Accept response, or Cancel/Decline as appropriate

### Requirement: URL Elicitation Handling
The system SHALL intercept `elicitation/create` requests with `url` mode and safely request user consent.

#### Scenario: Server requests URL consent
- **WHEN** the server sends an `elicitation/create` request with a `url`
- **THEN** the client displays the target domain clearly and asks for human consent before allowing the user to open the URL securely

### Requirement: URLElicitationRequiredError Handling
The system SHALL intercept `-32042` tool execution errors and present the required URL elicitations.

#### Scenario: Tool requires authorization
- **WHEN** a tool call fails with a `-32042` error and a list of URL elicitations
- **THEN** the client presents the URL consent UI
- **AND** optionally auto-retries the tool call once the `notifications/elicitation/complete` webhook is received or the user confirms completion
