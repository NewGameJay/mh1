# /quickstart - Fast Client Onboarding

Set up a new client in ~10 minutes with guided prompts.

---

## Usage

```
/quickstart
/quickstart [company name]
```

---

## Flow

### Step 1: Company Basics (1 min)

**If no company name provided, ask:**
> "What company are you onboarding?"

**Then ask:**
> "What's their website? (e.g., acme.com)"

**Auto-detect from website:**
- Industry
- Company stage (if possible)
- Basic description

**Confirm:**
> "I found [Company Name] - a [industry] company that [description]. Is this right?"

---

### Step 2: Founders (2 min)

**Ask:**
> "Who are the founders we'll be ghostwriting for?
> 
> Please provide:
> - Name
> - Role (CEO, CTO, etc.)
> - LinkedIn URL (optional but recommended)"

**If LinkedIn provided:**
- Auto-fetch profile data
- Extract voice patterns from recent posts

**If no LinkedIn:**
> "No problem. We'll gather voice data from the interview instead."

---

### Step 3: Quick Research (3 min)

**Announce:**
> "I'm now researching [Company]. This takes about 2-3 minutes..."

**Run in parallel:**
1. Company research (from website + public sources)
2. Competitor identification (3-5 competitors)
3. Founder research (if LinkedIn provided)

**Show progress:**
> "- Company research... done
> - Finding competitors... done  
> - Researching [Founder Name]... done"

---

### Step 4: Interview Questions (1 min)

**Generate based on research gaps:**
> "I've prepared 10 interview questions to fill in what I couldn't find online.
> 
> Key topics:
> - Voice and communication style
> - Target audience specifics
> - Competitive positioning
> - Content preferences
> 
> Ready to see the questions?"

**Show questions grouped by topic**

---

### Step 5: Optional Extras (2 min)

**Ask:**
> "A few optional things that help create better content:
> 
> 1. Do you have any existing content samples? (past LinkedIn posts, blog posts, etc.)
> 2. Any specific competitors to track? (I found [list], any others?)
> 3. Keywords or hashtags to monitor for signals?
> 
> Type 'skip' to set these up later."

---

### Step 6: Setup Complete (1 min)

**Create in Firebase:**
- Client record
- Research documents
- Default signal configuration

**Create Notion dashboard (if configured)**

**Announce:**
> "[Company Name] is ready!
> 
> **Next steps:**
> 1. Conduct the interview using the questions above
> 2. Run `/interview [company]` to add interview results
> 3. Run `/ghostwrite [company]` to create your first posts
> 
> **Quick commands:**
> - `/signals [company]` - Start collecting social signals
> - `/status [company]` - Check setup status
> - `/help` - See all commands"

---

## Checkpoints

The flow saves progress after each step. If interrupted:

```
/quickstart [company] --resume
```

Picks up where you left off.

---

## Quick Mode

Skip optional steps for fastest setup:

```
/quickstart [company] --quick
```

This skips:
- Competitor research
- Signal configuration
- Notion dashboard setup

Just creates the client with basic research. You can add the rest later.

---

## Behind the Scenes

This command orchestrates:
- `skills/research-company/` 
- `skills/research-competitors/`
- `skills/research-founder/`
- `skills/generate-interview-questions/`
- `tools/create-client.js`
- `tools/create-notion-dashboard.js` (if configured)

All using the `deep-research-agent` and `interview-agent`.

---

## Examples

**Standard onboarding:**
```
User: /quickstart
AI: What company are you onboarding?
User: Acme Corp
AI: What's their website?
User: acme.com
AI: I found Acme Corp - a B2B SaaS company that provides project management tools. Is this right?
User: Yes
AI: Who are the founders we'll be ghostwriting for?
User: Jane Doe, CEO, linkedin.com/in/janedoe
AI: Great! I'm now researching Acme Corp...
[2 minutes later]
AI: Research complete! I've prepared 10 interview questions...
```

**Quick mode:**
```
User: /quickstart Acme Corp --quick
AI: What's Acme Corp's website?
User: acme.com
AI: Got it. Running quick setup...
[1 minute later]
AI: Acme Corp is ready with basic research. Run /status Acme to see what's set up.
```
