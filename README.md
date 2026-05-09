# 2026 PyData Boston x Cursor Data Science Hackathon

Welcome! This repository is the starting point for participants in the **2026 PyData Boston x Cursor Data Science Hackathon**.

This guide helps you get your machine ready and confirms that Cursor can connect to a running Marimo notebook.

## Before the Hackathon

Please make sure you have the following:

- `uv` installed on your computer (installation guide: [Astral uv installation](https://docs.astral.sh/uv/getting-started/installation/)).
- `npm` available on your computer (installation guide: [Node.js and npm installation](https://docs.npmjs.com/downloading-and-installing-node-js-and-npm)).
- Cursor downloaded from the [Cursor website](https://www.cursor.com/).
- A Cursor account created (**do not purchase a paid plan yet**).
- A working internet connection.

### Step 1: Create a Work Folder

Create a folder where you will do your hackathon work.

Use whichever term is familiar to you:

- **Folder**: a place on your computer for files.
- **Workspace**: the folder you open in Cursor.
- **Repository (repo)**: a folder tracked with Git (optional for now).

If you are unsure, just create a normal folder named `pydata-hackathon` anywhere convenient (for example, your Desktop or Documents folder).

### Step 2: Install the `marimo-pair` Skill

Open a terminal, move into your work folder, and run:

```bash
npx skills install marimo-team/marimo-pair
```

### Step 3: Start the Marimo Notebook Server

In the same folder, run:

```bash
uvx marimo edit --sandbox --no-token hackathon-notebook.py
```

This should start Marimo locally at `http://localhost:2718`.

### Step 4: Open Cursor and Create an Agent

In Cursor:

1. Open your work folder.
2. Go to the latest Cursor Agent view.
3. Create a new agent in that folder.

### Step 5: Connect Cursor Agent to Marimo

Send this prompt to your Cursor agent:

```text
Using the marimo-pair skill, connect to my running marimo notebook at http://localhost:2718
```

Then ask the agent to create a new Markdown cell that says:

```text
Hello!
```

## Success Check

You are set up correctly when:

- Cursor agent connects to your running Marimo notebook, and
- A new Markdown cell appears in the notebook containing `Hello!`.

At that point, you are ready to build during the hackathon.
