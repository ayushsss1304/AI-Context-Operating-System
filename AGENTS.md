# AI Context Operating System

AI Context Operating System is a shared memory and workflow-continuity layer for AI-native teams using multiple AI agents, copilots, and automation tools.

The MVP should prove that multiple AI agents can share memory, continue tasks across sessions, and let humans supervise their work.

## MVP Demo Scenario

1. Support Agent summarizes a customer issue and stores it as memory.
2. Engineering Agent retrieves related memories and creates a technical investigation note.
3. Product Agent reads the support and engineering context and creates a product impact summary.
4. Human Manager sees all agent actions in an activity timeline.
5. Human Manager approves or rejects the final recommendation.

## Core Modules

- Workspace
- Agent Registry
- Shared Memory Store
- Task / Workflow System
- Activity Timeline
- Human Approval Layer

## Build Rules

- Do not build a generic chatbot.
- Build infrastructure for shared organizational memory, context handoff, workflow continuity, and human oversight.
- Keep V1 small, demo-friendly, and backend-first.
- Use environment variables for secrets.
- Do not hardcode API keys.
