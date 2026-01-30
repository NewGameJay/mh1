# /help - MH1 Command Reference

Show available commands and how to use them.

---

## Usage

```
/help                  - Show all commands
/help [command]        - Get details for a specific command
```

---

## Response Format

### When showing all commands:

> **MH1 Commands**
> 
> **Getting Started**
> - `/quickstart` - Set up a new client (10 min guided flow)
> - `/help` - Show this reference
> 
> **Client Management**
> - `/clients` - List all clients
> - `/switch [client]` - Set active client for session
> - `/status [client]` - Check client setup status
> 
> **Content Creation**
> - `/ghostwrite [client]` - Create LinkedIn posts
> - `/briefs [client]` - Create assignment briefs from signals
> - `/signals [client]` - Collect social signals
> 
> **After Interview**
> - `/interview [client]` - Add interview results to research
> 
> **Analytics**
> - `/icp-report [client]` - ICP engagement analysis (weekly)
> - `/leads [client]` - View qualified leads
> - `/sync [client]` - Sync to Notion dashboard
> 
> **Admin**
> - `/health` - System status
> - `/budgets` - Cost tracking
> 
> Type `/help [command]` for details on any command.

---

### When showing specific command:

Pull the content from the corresponding `commands/[command].md` file.

Show:
1. Purpose (first line after title)
2. Usage examples
3. Options/flags
4. Common scenarios

---

## Command Routing

| Input | Route To |
|-------|----------|
| `/help` | This file |
| `/help quickstart` | `commands/quickstart.md` |
| `/help ghostwrite` | `commands/ghostwrite-content.md` |
| `/help briefs` | `commands/curate-assignment-briefs.md` |
| `/help signals` | `commands/collect-signals.md` |
| `/help onboard` | `commands/onboard-client.md` |
| `/help interview` | `commands/incorporate-interview.md` |
| `/help icp-report` | `commands/analyze-icp-performance.md` |
| `/help [unknown]` | "Command not found. Run /help to see available commands." |

---

## Natural Language Fallback

If user asks something that's not a command:

> "I'm not sure what you mean. Here are some things you can do:
> 
> - **Set up a new client:** `/quickstart`
> - **Create content:** `/ghostwrite [client]`
> - **Check status:** `/status [client]`
> 
> What would you like to do?"

---

## Context Awareness

If a client is active (set via `/switch` or from `inputs/active_client.md`):

> "Active client: **[Client Name]**
> 
> You can run commands without specifying the client:
> - `/ghostwrite` instead of `/ghostwrite [client]`"

If no client is active:

> "No active client set. Either:
> - Specify client: `/ghostwrite Acme`
> - Set active client: `/switch Acme`"
