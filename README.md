<div align="center">
    <span style="font-size: 5rem;">🏡</span>
    <h1>Ayala Family Skills Registry</h1>
    <p>A repository of standardized, repeatable capabilities and automations for household management, personal projects, and family workflows.</p>
</div>

---

## About

This repository serves as a centralized hub of **Ayala Family AI Skills**—structured instructions, guidelines, and automation scripts designed for our household. 

Each skill represents a discrete capability or routine. By standardizing these tasks, we enable AI assistants (such as Claude, Gemini, or ChatGPT) to interact with our family projects, databases, document formats, and smart home configs with precision and safety.

This ensures:
- **Consistency**: Routine family workflows (like meal planning, tax prep, or smart home setup) are executed the same way every time.
- **Safety**: Clear boundaries prevent the AI from generating bad files, over-scheduling events, or misclassifying budget data.
- **Efficiency**: Speeds up repeating weekly, monthly, or annual chores through templates and automation.

---

## Directory Structure

Skills are organized logically by family/personal domain and skill name:

```text
AyalaSkills/
│
├── README.md               <-- Repository guidelines (this file)
└── skills/                 
    ├── <category>/         <-- Family domains (e.g., home, finance, social, kitchen)
    │   └── <skill-name>/   <-- The specific task or routine
    │       ├── skill.md    <-- Core instructions and rules for the AI
    │       └── [scripts/]  <-- (Optional) Helper automation scripts or tools
    └── ...
```

---

## Skill Catalog

Here is the current registry of skills for household and personal management:

| Category | Skill Name & Link | Description | Key Target |
| :--- | :--- | :--- | :--- |
| **Home** | [Tapo Device Control](skills/home/tapo/skill.md) | Turns Tapo smart plugs and bulbs on or off and checks status/power draw using auto-discovery. | Tapo smart devices |
| **Social** | [Facebook Messenger Control](skills/social/facebook/skill.md) | Hosts a Messenger chat bot to listen for home automation commands from authorized users. | Facebook Messenger chats |

---

## How to Use a Skill (For AI Agents)

When assigned a family task matching a skill in this registry, the agent should follow this checklist:

1. **Locate the Skill**: Find the correct category and skill folder under `skills/` (e.g., `skills/home/tapo/`).
2. **Read the Instructions**: Open and read the `skill.md` file completely before starting the task.
3. **Follow the Constraints**: Closely adhere to **Edge Cases & Constraints** (e.g., dietary restrictions, user authorization checks).
4. **Execute Automation Tools**: If the skill contains a `scripts/` folder, run or adapt the scripts as needed.
5. **Verify Outputs**: Use the **Checklist** at the end of `skill.md` to verify that all criteria have been met before declaring completion.

---

## Authoring New Skills

To add a new skill to the family registry, use the following template:

### 1. Create the Folder
Create a new directory:
`skills/<category>/<skill-name>/`

### 2. Format of `skill.md`
Every skill MUST have a `skill.md` file using this markdown structure:
- **Title**: A clean, descriptive title (H1).
- **Purpose**: A brief paragraph explaining why we do this task and what it solves.
- **Inputs**: What the AI needs (e.g., "last month's spreadsheet", "a list of flight confirmation numbers").
- **Detailed Steps**: Precise, sequential instructions. Avoid ambiguity.
- **Edge Cases & Constraints**: Rules the AI must respect (e.g., "do not buy non-organic apples", "never schedule flights with less than 2-hour layovers").
- **Examples**: Sample outputs or configuration files for the AI to emulate.
- **Checklist**: Checkboxes the AI can self-evaluate at the end.

---

## Setup & Running Scripts (Windows PowerShell)

For skills containing Python utilities or scripts, follow these steps to run them in a clean environment:

1. **Navigate to the script directory**:
   ```powershell
   cd "C:\Users\chest\Desktop\workspace\projects\AyalaSkills\skills\<category>\<skill-name>\scripts"
   ```
2. **Create a virtual environment** (if not already present):
   ```powershell
   python -m venv venv
   ```
3. **Activate the environment**:
   ```powershell
   .\venv\Scripts\Activate.ps1
   ```
4. **Install required dependencies**:
   ```powershell
   pip install -r requirements.txt
   ```
5. **Run the script**:
   ```powershell
   python main.py
   ```