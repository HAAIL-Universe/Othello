# OTHELLO PROJECT INDEX — COMPLETE DOCUMENTATION
**Generated:** 2025-12-17  
**Repository:** HAAIL-Universe/Othello  
**Purpose:** Comprehensive index of the Othello project structure, code, and runtime behavior

---

## TABLE OF CONTENTS
1. [Filesystem Inventory](#1-filesystem-inventory)
2. [Backend Analysis](#2-backend-analysis)
3. [Frontend Analysis](#3-frontend-analysis)
4. [State, Auth, and Session](#4-state-auth-and-session)
5. [Database & Persistence](#5-database--persistence)
6. [Configuration & Environment](#6-configuration--environment)
7. [Runtime & Deployment](#7-runtime--deployment)
8. [Risk & Smell Notes](#8-risk--smell-notes)

---

## 1. FILESYSTEM INVENTORY

### 1.1 Root Directory Structure

```
Othello/
├── api.py                          # Flask server entry point (1599 lines)
├── othello_ui.html                 # Single-page frontend application (2891 lines)
├── requirements.txt                # Python dependencies
├── .env                            # Environment variables (DATABASE_URL, OPENAI_API_KEY)
├── .gitignore                      # Git ignore rules
├── README.md                       # Project documentation (312 lines)
├── agentic_memory.json             # Runtime memory state (file-based cache)
├── .llm_model_cache                # Cached LLM model selection
├── othello.py                      # Othello safeguarding agent (60 lines)
├── fello.py                        # Fello agentic orchestrator (134 lines)
├── pineal_agent.py                 # Pineal agent module
├── main_agent.py                   # Main agent entry point
├── clear_goals.py                  # Utility to clear goals
├── run_tests.py                    # Test runner
├── simulate_test_run.py            # Simulation test utility
├── sim_user.py                     # User simulation script
├── full_emergence_simulation.py    # Full simulation runner
├── patch_insights.py               # Insights patching utility
├── test_json_write.py              # JSON write test
├── test_impatience_data.json       # Test data for impatience detection
├── pushme.ps1                      # Windows PowerShell push script
├── core/                           # Core application logic (18 modules)
├── db/                             # Database layer (11 modules)
├── modules/                        # Application modules (15 modules)
├── interface/                      # CLI and interface modules (12 modules)
├── utils/                          # Utility functions (9 modules)
├── data/                           # Local data storage (goals, plans, logs)
├── config/                         # Configuration files
├── scripts/                        # Deployment and utility scripts
├── tests/                          # Unit tests (17 test files)
├── build_docs/                     # Documentation (manifesto, blueprint, directive)
├── sim_logs/                       # Simulation logs (80+ JSON files)
├── summary_logs/                   # Summary logs
└── debug_logs/                     # Debug logs
```

### 1.2 Core Application Files

**Primary Entry Points:**
