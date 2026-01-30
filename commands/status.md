# /status - Client Status

Check the setup status and recent activity for a client.

---

## Usage

```
/status [client]       - Status for specific client
/status                - Status for active client
/status --all          - Quick status for all clients
```

---

## Response Format

### Full status for one client:

> **Status: [Client Name]**
> 
> **Setup Completion**
> - [x] Client record created
> - [x] Company research complete
> - [x] Competitors identified (5)
> - [x] Founder research: Raaja Nemani
> - [x] Interview questions generated
> - [ ] Interview results incorporated
> - [x] Signal listeners configured
> - [x] Notion dashboard created
> 
> **Content Stats**
> | Metric | Count | Last Updated |
> |--------|-------|--------------|
> | Posts created | 45 | 2 days ago |
> | Briefs ready | 8 | Today |
> | Signals tracked | 230 | Today |
> | Leads qualified | 12 | 3 days ago |
> 
> **Health**
> - Signal collection: Running (last: 4 hours ago)
> - Voice contract: Valid
> - Notion sync: Connected
> 
> **Next suggested action:**
> Run `/ghostwrite` - You have 8 briefs ready for content

---

### If setup incomplete:

> **Status: [Client Name]** (Incomplete)
> 
> **Setup Progress: 60%**
> - [x] Client record created
> - [x] Company research complete
> - [x] Competitors identified
> - [ ] Founder research (pending)
> - [ ] Interview questions (pending)
> - [ ] Interview results (pending)
> 
> **Next step:**
> Run `/quickstart [client] --resume` to continue setup

---

### Quick status (--all):

> **All Clients Status**
> 
> | Client | Setup | Posts | Signals | Last Active |
> |--------|-------|-------|---------|-------------|
> | MH-1 | 100% | 45 | 230 | Today |
> | Acme Corp | 100% | 12 | 89 | 3 days |
> | Beta Inc | 60% | 0 | 0 | 1 week |

---

## Data Sources

Pull from Firebase:
- `clients/{clientId}` - Basic info
- `clients/{clientId}/modules/linkedin-ghostwriter/posts` - Post count
- `clients/{clientId}/modules/linkedin-ghostwriter/assignment-briefs` - Brief count
- `clients/{clientId}/signals` - Signal count
- `clients/{clientId}/leads` - Leads count

Check setup completion by verifying existence of:
- Company profile doc
- Competitor docs
- Founder research docs
- Voice contracts
- Interview results

---

## Error States

**Client not found:**
> Client "[name]" not found. Run `/clients` to see available clients.

**No active client and no client specified:**
> No client specified. Either:
> - Run `/status [client name]`
> - Set active client: `/switch [client]`
