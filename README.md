
# AI Workflow Orchestrator

An AI-assisted workflow and case management application built with Python, FastAPI, SQLite, and Ollama. The project demonstrates automated case validation, workflow routing, AI-supported issue classification, audit history, automated testing, and continuous integration.

## Project Overview

The application processes synthetic customer cases and determines the next workflow action based on document validation rules. A locally hosted Llama 3.2 model can classify validation issues and suggest corrective actions.

**Key safety principle:** AI recommendations are advisory. Python workflow rules control case routing, and cases with missing required documents remain in human review.

## Features

- Case retrieval and required-document validation
- Rule-based workflow routing
- REST API built with FastAPI
- SQLite persistence for workflow history
- Local AI classification through Ollama
- Structured AI response validation
- Fallback handling when AI classification fails
- Human-review safeguards
- Automated unit and API tests
- Git version control and GitHub Actions CI

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Workflow logic and application code |
| FastAPI | REST API |
| SQLite | Workflow result persistence |
| Ollama | Local model execution |
| Llama 3.2 1B | Local AI issue classification |
| unittest | Automated testing |
| Git and GitHub | Version control |
| GitHub Actions | Continuous integration |

## Architecture

```text
Client
  |
  v
FastAPI
  |
  v
Case Retrieval
  |
  v
Document Validation
  |
  v
Rule-Based Workflow Routing
  |
  +---- No issues ----> Validated workflow
  |
  +---- Issues ------> Human review required
                           |
                           v
                    Local AI classification
                           |
                           v
                    Validate AI response
                           |
                           v
                    Advisory recommendation

Workflow results and history are stored in SQLite.
GitHub Actions runs automated tests on code changes.
```

## Sample Cases

The application uses synthetic sample data.

| Case ID | Document status | Expected workflow status |
|---|---|---|
| `12345` | Document received | `VALIDATED` |
| `56789` | Document missing | `REVIEW_REQUIRED` |
| `99999` | Case not found | HTTP 404 |

These are demonstration cases, not real customer records.

## Prerequisites

- Python 3.12 or another compatible Python version
- Git
- Ollama, if you want to run the local AI classifier
- The Llama 3.2 1B model for AI-assisted classification

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/Akash-savanth/AI-Workflow-Orchestrator.git
cd AI-Workflow-Orchestrator
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it on Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, you can run the virtual environment's Python executable directly.

### 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Install and start Ollama

Install Ollama from https://ollama.com/download/windows.

Download the model:

```bash
ollama pull llama3.2:1b
```

Ollama must be running for real AI classification requests.

## Run the Application

Start the API:

```bash
uvicorn api:app --reload
```

Open the API documentation:

http://127.0.0.1:8000/docs

## API Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/` | API health message |
| GET | `/cases/{case_id}` | Process a case using workflow rules |
| GET | `/cases/{case_id}/history` | Retrieve stored workflow history |
| GET | `/cases/{case_id}/ai-review` | Process a case with optional AI issue classification |

Example AI-review request:

```bash
curl http://127.0.0.1:8000/cases/56789/ai-review
```

For case `56789`, the expected workflow outcome is `REVIEW_REQUIRED`, with human approval required.

## Run Tests

Run the workflow and API tests:

```bash
python -m unittest discover -s tests -v
```

Run the standalone AI classifier test:

```bash
python test_ai.py
```

The API tests mock the AI classifier where appropriate, so the automated test suite does not need to download or run the model.

## Continuous Integration

GitHub Actions runs the automated test suite when changes are pushed to the configured branches or when pull requests target those branches.

Workflow configuration:

`.github/workflows/tests.yml`

## Safety and Limitations

- The application uses synthetic sample cases only.
- AI output is treated as a recommendation, not an authoritative decision.
- Missing-document cases require human review.
- AI failures should fall back to rule-based workflow behavior.
- Local AI availability depends on Ollama and the downloaded model.
- This is a learning and portfolio project, not a production banking system.
- Production use would require additional security, authentication, authorization, privacy controls, monitoring, deployment hardening, and operational validation.

## Future Enhancements

- Add API authentication and authorization
- Expand validation and negative test coverage
- Add structured metrics and monitoring
- Improve database configuration and deployment
- Extend CI with code quality and security checks
- Explore controlled tool-calling and MCP integration

## Author

**Akash M P**

GitHub: https://github.com/Akash-savanth
