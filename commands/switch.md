# /switch - Set Active Client

Set the active client for your session. This lets you run commands without specifying the client name each time.

---

## Usage

```
/switch [client]
/switch                - Show current active client
/switch --clear        - Clear active client
```

---

## How It Works

When you set an active client:
1. Updates `inputs/active_client.md` with the client info
2. All subsequent commands use this client by default

---

## Examples

**Set active client:**
```
User: /switch Acme Corp
AI: Active client set to **Acme Corp**
    
    You can now run:
    - /ghostwrite (instead of /ghostwrite Acme Corp)
    - /signals (instead of /signals Acme Corp)
    - /status (instead of /status Acme Corp)
```

**Check current client:**
```
User: /switch
AI: Current active client: **Acme Corp**
    
    To change: /switch [other client]
    To clear: /switch --clear
```

**Clear active client:**
```
User: /switch --clear
AI: Active client cleared. You'll need to specify the client in commands.
```

---

## Response Format

### On successful switch:

> **Active client: [Client Name]**
> 
> Firebase ID: `{clientId}`
> Default founder: [Founder Name] (if set)
> 
> Ready to run commands. Try:
> - `/ghostwrite` - Create posts
> - `/signals` - Collect signals
> - `/status` - Check status

---

### If client not found:

> Client "[name]" not found.
> 
> Did you mean one of these?
> - Acme Corp
> - Acme Industries
> 
> Or run `/clients` to see all clients.

---

## Updates `inputs/active_client.md`

```markdown
# Active Client Configuration

CLIENT_ID = {firebase_document_id}
CLIENT_NAME = {display_name}
DEFAULT_FOUNDER = {founder_name or blank}
```

This file is read by skills and tools to know which client to operate on.
