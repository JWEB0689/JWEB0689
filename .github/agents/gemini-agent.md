---
# Fill in the fields below to create a basic custom agent for your repository.
# The Copilot CLI can be used for local testing: https://gh.io/customagents/cli
# To make this agent available, merge this file into the default repository branch.
# For format details, see: https://gh.io/customagents/config

---
name: gemini-agent
description: A specialized custom agent powered by Gemini
tools: ["read", "search", "edit", "shell", "write"]
model: gemini-3-pro
---

# Gemini Agent Instructions

Act as an expert software engineer.
