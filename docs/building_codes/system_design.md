# 🧠 System Design Overview

This document defines the architecture of the AI-driven architectural workflow engine.

---

## ⚙️ 1. Core Concept

The system is a modular workflow engine that transforms user input into structured architectural outputs using staged processing.

---

## 🧩 2. Core Components

### Engine
- Executes workflows step-by-step
- Maintains shared context state

### Context Manager
- Stores dynamic data during execution
- Enables inter-stage communication

### Function Registry
- Maps stage names to executable functions
- Allows plug-and-play architecture

### Workflow Loader
- Loads JSON-defined workflows
- Enables external configuration without code changes

---

## 🔄 3. Execution Flow

1. Input received (e.g. building request)
2. Workflow selected (e.g. eco_design)
3. Engine loads steps
4. Each stage processes shared context
5. Final output generated

---

## 🧬 4. Design Philosophy

- Modular over monolithic
- Data-driven workflows
- Extensible stage system
- Separation of logic and configuration

---

## 🚀 5. Future Expansion

- AI reasoning inside stages
- Multi-agent collaboration
- Conditional workflow branching
- Visual diagram generation

---
