<div align="center">
    <span style="font-size: 5rem;">🏡</span>
    <h1>Ayala Skills Registry</h1>
    <p>A repository of standardized, repeatable capabilities and automations for personal projects, system integrations, and custom workflows.</p>
</div>

---

## About

This repository serves as a centralized hub of **Ayala Skills**—structured instructions, guidelines, and automation scripts. 

Each skill represents a discrete capability or routine. By standardizing these tasks, we enable AI assistants (such as Claude Code, Gemini, or ChatGPT) to interact with our projects, databases, document formats, and smart home configurations with precision and safety.

---

## Directory Structure

Skills are organized logically by category and name:

```text
<repository-name>/
│
├── README.md               <-- Repository guidelines (this file)
└── skills/                 
    ├── <category>/         <-- Skill domain (e.g. home, finance, social)
    │   └── <skill-name>/   <-- The specific task or capability
    │       ├── SKILL.md    <-- Main instruction file (with YAML frontmatter)
    │       └── [scripts/]  <-- (Optional) Supporting automation tools or helper scripts
    └── ...
```

---

## Skill Catalog

| Category | Skill Name & Link | Description | Key Target |
| :--- | :--- | :--- | :--- |
| **Home** | [Tapo Device Control](skills/home/tapo/SKILL.md) | Turns Tapo smart plugs and bulbs on or off and checks status/power draw using auto-discovery. | Tapo smart devices |
| **Social** | [Facebook Messenger Control](skills/social/facebook/SKILL.md) | Hosts a Messenger chat bot to listen for home automation commands from authorized users. | Facebook Messenger chats |

---

## How to Author New Skills

To add a new capability:
1. Create a directory: `skills/<category>/<skill-name>/`
2. Add a `SKILL.md` file using this structure:
   - **YAML Frontmatter**: Define `name` and `description` triggers.
   - **Purpose**: High-level explanation of the task.
   - **Inputs**: Required inputs/context.
   - **Detailed Steps**: Sequential guide for the AI.
   - **Edge Cases & Constraints**: Specific safety rules and parameters.
   - **Checklist**: Validation points for the AI before completing tasks.
