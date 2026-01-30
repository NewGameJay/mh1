# /clients - List All Clients

Show all onboarded clients and their status.

---

## Usage

```
/clients
/clients --active      - Show only active clients
/clients --detailed    - Show more info per client
```

---

## Response Format

### Standard view:

> **Your Clients**
> 
> | Client | Status | Last Activity | Posts | Signals |
> |--------|--------|---------------|-------|---------|
> | MH-1 | Active | Today | 45 | 230 |
> | Acme Corp | Active | 3 days ago | 12 | 89 |
> | Beta Inc | Onboarding | 1 week ago | 0 | 0 |
> 
> **Quick actions:**
> - `/switch [client]` - Set as active client
> - `/status [client]` - See detailed status
> - `/quickstart` - Add a new client

---

### Detailed view (`--detailed`):

> **Your Clients (Detailed)**
> 
> ---
> **MH-1** (Active)
> - Website: marketerhire.com
> - Industry: B2B SaaS
> - Founders: Raaja Nemani (CEO)
> - Posts created: 45
> - Signals tracked: 230
> - Last post: 2 days ago
> - Last signal collection: Today
> 
> ---
> **Acme Corp** (Active)
> - Website: acme.com
> - Industry: B2B SaaS
> - Founders: Jane Doe (CEO), John Smith (CTO)
> - Posts created: 12
> - Signals tracked: 89
> - Last post: 5 days ago
> - Last signal collection: 3 days ago

---

## Data Source

Pull client list from Firebase:
```
Collection: clients
Fields: displayName, status, website, industry
```

Pull activity from Firebase:
```
Collection: clients/{clientId}/modules/linkedin-ghostwriter/posts
Collection: clients/{clientId}/signals
```

---

## No Clients Yet

If no clients found:

> **No clients yet**
> 
> Run `/quickstart` to onboard your first client.
