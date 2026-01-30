# MH1 CLI Enhancement Plan

**Goal:** Make the CLI non-technical friendly with intuitive menus and Firebase-backed client management.

---

## User Journey Overview

```
┌────────────────────────────────────────────────────────────┐
│                     MH1 WELCOME SCREEN                     │
│                                                            │
│  ███╗   ███╗██╗  ██╗     ██╗                              │
│  ████╗ ████║██║  ██║    ███║                              │
│  ██╔████╔██║███████║    ╚██║                              │
│  ██║╚██╔╝██║██╔══██║     ██║                              │
│  ██║ ╚═╝ ██║██║  ██║     ██║                              │
│  ╚═╝     ╚═╝╚═╝  ╚═╝     ╚═╝                              │
│            AI-Powered Marketing Copilot                    │
│                                                            │
│  What would you like to do?                               │
│                                                            │
│  [1] Continue                                              │
│  [2] Create New Client                                     │
│  [3] Browse Skills                                         │
│  [4] Browse Agents                                         │
│  [5] Chat Mode                                             │
│                                                            │
│  [h] Help  [q] Quit                                        │
└────────────────────────────────────────────────────────────┘
```

---

## Phase 1: Enhanced Welcome Menu

### Task 1.1: Restructure Main Menu

**File:** `mh1` (main CLI)

Replace `show_copilot_menu()` for no-client-selected state:

```python
def show_welcome_menu():
    """Display the welcome menu with all options."""
    clear_screen()
    print(BANNER)

    print(f"{C.BOLD}What would you like to do?{C.END}\n")
    print(f"  {C.CYAN}[1]{C.END} Continue")
    print(f"  {C.CYAN}[2]{C.END} Create New Client")
    print(f"  {C.CYAN}[3]{C.END} Browse Skills")
    print(f"  {C.CYAN}[4]{C.END} Browse Agents")
    print(f"  {C.CYAN}[5]{C.END} Chat Mode")
    print()
    print(f"  {C.DIM}[h] Help  [q] Quit{C.END}")
    print()
```

---

### Task 1.2: Add Skills Browser

**New function:** `show_skills_browser()`

```python
def show_skills_browser():
    """Display all available skills with descriptions."""
    clear_screen()
    print(BANNER)
    print(f"{C.BOLD}Available Skills{C.END}\n")

    # Group by category
    categories = {
        "Research": ["research-company", "research-competitors", "research-founder"],
        "Content": ["ghostwrite-content", "create-assignment-brief", "email-copy-generator"],
        "Social Listening": ["linkedin-keyword-search", "twitter-keyword-search", "reddit-keyword-search"],
        "Analytics": ["lifecycle-audit", "churn-prediction", "at-risk-detection"],
        "Extraction": ["extract-pov", "extract-founder-voice", "extract-audience-persona"],
        "Data": ["firebase-bulk-upload", "firestore-nav", "get-client"],
    }

    # Display skills with descriptions from SKILL.md frontmatter
    for category, skills in categories.items():
        print(f"\n{C.CYAN}{category}{C.END}")
        for skill_name in skills:
            desc = get_skill_description(skill_name)  # Parse from SKILL.md
            print(f"  {C.BOLD}{skill_name}{C.END}")
            print(f"    {C.DIM}{desc[:60]}...{C.END}")
```

---

### Task 1.3: Add Agents Browser

**New function:** `show_agents_browser()`

```python
def show_agents_browser():
    """Display all available agents."""
    clear_screen()
    print(BANNER)
    print(f"{C.BOLD}Available Agents{C.END}\n")

    agents = {
        "Workers": [
            ("lifecycle-auditor", "Analyzes customer lifecycle stages and recommends improvements"),
            ("linkedin-ghostwriter", "Creates LinkedIn posts matching brand voice"),
            ("deep-research-agent", "Conducts comprehensive research on topics"),
            ("interview-agent", "Gathers information through structured questions"),
        ],
        "Evaluators": [
            ("fact-check-agent", "Validates claims and sources"),
            ("linkedin-qa-reviewer", "Quality checks LinkedIn content"),
        ],
    }

    for category, agent_list in agents.items():
        print(f"\n{C.CYAN}{category}{C.END}")
        for name, desc in agent_list:
            print(f"  {C.BOLD}{name}{C.END}")
            print(f"    {C.DIM}{desc}{C.END}")

    # Option to chat with agent
    print(f"\n{C.BOLD}Chat with an agent?{C.END}")
    print(f"  Type agent name or [b] to go back")
```

---

### Task 1.4: Add Chat Mode

**New function:** `run_chat_mode()`

```python
def run_chat_mode(client=None):
    """Pure chat mode - natural language interaction."""
    clear_screen()
    print(BANNER)

    if client:
        print(f"  {C.GREEN}●{C.END} Client: {client.display_name}")
    else:
        print(f"  {C.YELLOW}○{C.END} No client selected")

    print(f"\n{C.BOLD}Chat Mode{C.END}")
    print(f"{C.DIM}Type your questions or requests. Type 'exit' to return to menu.{C.END}\n")

    while True:
        user_input = safe_input(f"{C.CYAN}You:{C.END} ")
        if not user_input or user_input.lower() in ['exit', 'quit', 'back']:
            break

        # Process via Claude
        result = subprocess.run(
            ['claude', '-p', user_input, '--output-format', 'text'],
            capture_output=True,
            text=True,
            cwd=WORKSPACE
        )

        print(f"\n{C.GREEN}MH1:{C.END} {result.stdout}\n")
```

---

## Phase 2: Enhanced Client Creation

### Task 2.1: Create Client Flow with Validation

**New function:** `create_client_wizard()`

```python
def create_client_wizard(components: Dict) -> Optional[ActiveClient]:
    """Guided client creation with Firebase storage."""
    clear_screen()
    print(BANNER)
    print(f"{C.BOLD}Create New Client{C.END}\n")

    fb = get_firebase_client()

    # Step 1: Client Name with similarity check
    print(f"{C.CYAN}Step 1/7: Client Name{C.END}")
    client_name = safe_input("  Company name: ").strip()

    if not client_name:
        print(f"{C.RED}Company name is required{C.END}")
        return None

    # Check for similar names in Firebase
    existing = fb.get_collection("clients", limit=100)
    similar = find_similar_names(client_name, existing)

    if similar:
        print(f"\n{C.YELLOW}Did you mean one of these?{C.END}")
        for i, match in enumerate(similar[:3], 1):
            print(f"  {C.CYAN}[{i}]{C.END} {match['displayName']}")
        print(f"  {C.CYAN}[n]{C.END} No, create new")

        choice = safe_input(f"\n{C.BOLD}>{C.END} ")
        if choice.isdigit() and 1 <= int(choice) <= len(similar):
            # Select existing client
            return select_existing_client(similar[int(choice)-1])

    # Step 2: Website with duplicate check
    print(f"\n{C.CYAN}Step 2/7: Website{C.END}")
    website = safe_input("  Website URL: ").strip()

    if website and not website.startswith("http"):
        website = "https://" + website

    # Check for duplicate website
    existing_with_website = [c for c in existing if c.get("website") == website]
    if existing_with_website:
        print(f"{C.YELLOW}⚠ Website already exists for: {existing_with_website[0].get('displayName')}{C.END}")
        cont = safe_input("  Continue anyway? [y/N]: ")
        if cont.lower() != 'y':
            return None

    # Step 3: Industry
    print(f"\n{C.CYAN}Step 3/7: Industry{C.END}")
    industries = ["SaaS", "E-commerce", "Healthcare", "Finance", "Education", "Other"]
    for i, ind in enumerate(industries, 1):
        print(f"  {C.CYAN}[{i}]{C.END} {ind}")
    industry_choice = safe_input(f"\n{C.BOLD}>{C.END} ")

    if industry_choice.isdigit() and 1 <= int(industry_choice) <= len(industries):
        industry = industries[int(industry_choice)-1]
    else:
        industry = industry_choice.strip()

    # Step 4: Social Platforms (multi-select)
    print(f"\n{C.CYAN}Step 4/7: Social Platforms{C.END}")
    print(f"{C.DIM}Select all that apply (comma-separated, e.g., 1,2,4){C.END}")
    platforms = ["LinkedIn", "Twitter/X", "Instagram", "YouTube", "TikTok", "Facebook"]
    for i, plat in enumerate(platforms, 1):
        print(f"  {C.CYAN}[{i}]{C.END} {plat}")

    platform_choices = safe_input(f"\n{C.BOLD}>{C.END} ").strip()
    selected_platforms = []
    for c in platform_choices.split(","):
        c = c.strip()
        if c.isdigit() and 1 <= int(c) <= len(platforms):
            selected_platforms.append(platforms[int(c)-1])

    # Step 5: Social Links
    print(f"\n{C.CYAN}Step 5/7: Social Links{C.END}")
    social_links = {}
    for plat in selected_platforms:
        link = safe_input(f"  {plat} URL: ").strip()
        if link:
            social_links[plat.lower().replace("/", "_")] = link

    # Step 6: Founders
    print(f"\n{C.CYAN}Step 6/7: Founders/Executives{C.END}")
    founders = collect_founders()  # Reuse existing function

    # Step 7: Main Goal
    print(f"\n{C.CYAN}Step 7/7: Main Goal{C.END}")
    goals = [
        "Increase brand awareness",
        "Generate leads",
        "Build thought leadership",
        "Drive engagement",
        "Support sales team",
        "Other"
    ]
    for i, goal in enumerate(goals, 1):
        print(f"  {C.CYAN}[{i}]{C.END} {goal}")

    goal_choice = safe_input(f"\n{C.BOLD}>{C.END} ")
    if goal_choice.isdigit() and 1 <= int(goal_choice) <= len(goals):
        main_goal = goals[int(goal_choice)-1]
    else:
        main_goal = goal_choice.strip()

    # Create client in Firebase
    client_id = client_name.lower().replace(" ", "-").replace(".", "")
    client_data = {
        "displayName": client_name,
        "website": website,
        "industry": industry,
        "socialPlatforms": selected_platforms,
        "socialLinks": social_links,
        "founders": [f.__dict__ for f in founders] if founders else [],
        "mainGoal": main_goal,
        "_created_at": datetime.now(timezone.utc).isoformat(),
        "_updated_at": datetime.now(timezone.utc).isoformat(),
    }

    # Save to Firebase
    fb.set_document(f"clients/{client_id}", client_data)

    print(f"\n{C.GREEN}✓ Client created: {client_name}{C.END}")
    print(f"{C.DIM}ID: {client_id}{C.END}")

    # Create local directory structure
    create_client_directories(client_id)

    # Return as ActiveClient
    return ActiveClient(
        client_id=client_id,
        display_name=client_name,
        current_phase=WorkflowPhase.ONBOARDED,
        website=website,
        industry=industry,
    )


def find_similar_names(query: str, existing: List[Dict]) -> List[Dict]:
    """Find existing clients with similar names."""
    matches = []
    query_lower = query.lower()

    for client in existing:
        name = client.get("displayName", client.get("name", "")).lower()
        score = SequenceMatcher(None, query_lower, name).ratio()

        # Also check substring
        if query_lower in name or name in query_lower:
            score = max(score, 0.8)

        if score >= 0.5:
            matches.append({**client, "_score": score})

    return sorted(matches, key=lambda x: x["_score"], reverse=True)


def create_client_directories(client_id: str):
    """Create local directory structure for client."""
    base = CLIENTS_DIR / client_id
    dirs = [
        "metadata",
        "context/company-profile",
        "context/founder-profiles",
        "context/competitors",
        "signals",
        "modules/linkedin-ghostwriter/assignment-briefs",
        "modules/linkedin-ghostwriter/posts",
        "evaluations",
    ]
    for d in dirs:
        (base / d).mkdir(parents=True, exist_ok=True)
```

---

## Phase 3: Client-Selected Menu

### Task 3.1: Secondary Menu After Client Selection

```python
def show_client_menu(client: ActiveClient, components: Dict):
    """Display menu after client is selected."""
    clear_screen()
    print(BANNER)

    # Client header
    print(f"  {C.GREEN}●{C.END} {C.BOLD}{client.display_name}{C.END}")
    print(f"    {C.DIM}{client.website}{C.END}")

    # Show brief status
    state = get_workflow_state(client.client_id)
    if state:
        print(f"    Phase: {state.current_phase.value}")

    print(f"\n{C.BOLD}What would you like to do?{C.END}\n")
    print(f"  {C.CYAN}[1]{C.END} Start (Recommended Action)")
    print(f"  {C.CYAN}[2]{C.END} Make a Plan")
    print(f"  {C.CYAN}[3]{C.END} Run Skills")
    print(f"  {C.CYAN}[4]{C.END} Run Agents")
    print(f"  {C.CYAN}[5]{C.END} Query Data / Refresh Discovery")
    print(f"  {C.CYAN}[6]{C.END} Client Details")
    print(f"  {C.CYAN}[7]{C.END} History")
    print()
    print(f"  {C.DIM}[s] Switch Client  [b] Back  [q] Quit{C.END}")
    print()
```

---

## Phase 4: Context Loading on Client Selection

### Task 4.1: Load Full Client Context

```python
def load_client_context(client_id: str) -> Dict:
    """Load all client data from Firebase for context."""
    fb = get_firebase_client()

    context = {
        "client": fb.get_document(f"clients/{client_id}"),
        "signals": fb.get_collection(f"clients/{client_id}/signals", limit=100),
        "posts": fb.get_collection(f"clients/{client_id}/posts", limit=50),
        "briefs": fb.get_collection(f"clients/{client_id}/briefs", limit=50),
        "voice_contract": fb.get_document(f"clients/{client_id}/context/voice-contract"),
        "company_profile": fb.get_document(f"clients/{client_id}/context/company-profile"),
    }

    # Also sync to local for offline access
    sync = ContextSync(client_id)
    sync.sync_to_local()

    return context
```

---

## Implementation Checklist

### Phase 1: Welcome Menu (Priority 1)
- [ ] Refactor `show_copilot_menu()` → `show_welcome_menu()`
- [ ] Add `show_skills_browser()` with skill descriptions
- [ ] Add `show_agents_browser()` with agent list
- [ ] Add `run_chat_mode()` for pure chat
- [ ] Update main menu handler for new options

### Phase 2: Client Creation (Priority 1)
- [ ] Add `create_client_wizard()` with all 7 steps
- [ ] Add `find_similar_names()` for duplicate detection
- [ ] Add Firebase storage for new clients
- [ ] Add `create_client_directories()` for local structure

### Phase 3: Client Menu (Priority 2 - Structure Only)
- [ ] Add `show_client_menu()` with new options
- [ ] Wire up menu choices to existing/placeholder functions

### Phase 4: Context Loading (Priority 2)
- [ ] Add `load_client_context()` on client selection
- [ ] Trigger context sync when client is selected
- [ ] Cache context for session

---

## Files to Modify

| File | Changes |
|------|---------|
| `mh1` | Major restructure of menu system, add new functions |
| `lib/client_selector.py` | Add Firebase write on create |

## Files to Create

| File | Purpose |
|------|---------|
| `lib/skill_browser.py` | Helper to parse skills and return list |
| `lib/agent_browser.py` | Helper to parse agents and return list |

---

## Success Criteria

After implementation:
1. `./mh1` shows 5-option welcome menu
2. Option 1 lists Firebase clients for selection
3. Option 2 guides through 7-step client creation with duplicate checks
4. Option 3 shows categorized skills list
5. Option 4 shows agents with chat option
6. Option 5 opens chat mode
7. New clients are stored in Firebase
8. Client context is loaded on selection
