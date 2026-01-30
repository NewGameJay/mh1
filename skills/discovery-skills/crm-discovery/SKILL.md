---
name: crm-discovery
description: |
  Query CRM systems for contacts, companies, deals, and activity data.
  Use when asked to 'query CRM', 'find contacts', 'check deals', 'explore CRM',
  'search companies', 'get sales pipeline', or 'analyze CRM data'.
license: MIT
compatibility:
  - HubSpot MCP (user-hubspot)
  - Salesforce API
  - Pipedrive API
  - Zoho CRM API
  - Microsoft Dynamics 365 API
metadata:
  author: mh1-engineering
  version: "2.0.0"
  status: active
  estimated_runtime: "30s-2min"
  max_cost: "$0.25"
  client_facing: false
  requires_human_review: false
  tags:
    - crm
    - data-discovery
    - sales
    - hubspot
    - salesforce
    - pipedrive
    - zoho
    - dynamics
allowed-tools: Read Write CallMcpTool Shell
---

# CRM Discovery Skill

Query CRM systems for contacts, companies, deals, and activity data across multiple platforms.

## When to Use

Use this skill when you need to:
- Search for contacts by email, name, or properties
- Find companies and their details
- Query deals and pipeline status
- Analyze sales activity by owner
- Get contact lifecycle distribution
- Identify churn risk contacts

## Supported Platforms

| Platform | Connection Method | Authentication |
|----------|------------------|----------------|
| **HubSpot** | MCP (`user-hubspot`) | Private App Token |
| **Salesforce** | REST API | OAuth 2.0 / Connected App |
| **Pipedrive** | REST API | API Token |
| **Zoho CRM** | REST API | OAuth 2.0 |
| **Microsoft Dynamics 365** | REST API (OData) | OAuth 2.0 / Azure AD |

## Configuration

Configure your CRM connection in `clients/{clientId}/config/crm.yaml`:

```yaml
crm:
  type: "{crm_type}"  # hubspot | salesforce | pipedrive | zoho | dynamics
  
  # Connection settings (platform-specific)
  hubspot:
    access_token: "{HUBSPOT_ACCESS_TOKEN}"
    portal_id: "{HUBSPOT_PORTAL_ID}"
    
  salesforce:
    instance_url: "{SF_INSTANCE_URL}"
    client_id: "{SF_CLIENT_ID}"
    client_secret: "{SF_CLIENT_SECRET}"
    username: "{SF_USERNAME}"
    security_token: "{SF_SECURITY_TOKEN}"
    
  pipedrive:
    api_token: "{PIPEDRIVE_API_TOKEN}"
    company_domain: "{PIPEDRIVE_DOMAIN}"
    
  zoho:
    client_id: "{ZOHO_CLIENT_ID}"
    client_secret: "{ZOHO_CLIENT_SECRET}"
    refresh_token: "{ZOHO_REFRESH_TOKEN}"
    api_domain: "{ZOHO_API_DOMAIN}"  # e.g., www.zohoapis.com
    
  dynamics:
    tenant_id: "{AZURE_TENANT_ID}"
    client_id: "{AZURE_CLIENT_ID}"
    client_secret: "{AZURE_CLIENT_SECRET}"
    resource_url: "{DYNAMICS_URL}"  # e.g., https://org.crm.dynamics.com

  # Entity mapping (customize per client)
  entities:
    contacts: "{contacts_object}"       # contacts, Contact, Person
    companies: "{companies_object}"     # companies, Account, Organization
    deals: "{deals_object}"             # deals, Opportunity, Deal
    activities: "{activities_object}"   # engagements, Task, Activity
    
  # Pipeline configuration
  pipelines:
    sales: "{sales_pipeline_id}"
    renewal: "{renewal_pipeline_id}"
```

## API Endpoints Reference

### HubSpot
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/crm/v3/objects/contacts` | GET | List/search contacts |
| `/crm/v3/objects/companies` | GET | List/search companies |
| `/crm/v3/objects/deals` | GET | List/search deals |
| `/crm/v3/objects/contacts/search` | POST | Advanced contact search |
| `/crm/v3/properties/contacts` | GET | Contact property definitions |

### Salesforce
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/services/data/v58.0/sobjects/Contact` | GET | Query contacts |
| `/services/data/v58.0/sobjects/Account` | GET | Query accounts |
| `/services/data/v58.0/sobjects/Opportunity` | GET | Query opportunities |
| `/services/data/v58.0/query?q={SOQL}` | GET | Execute SOQL query |

### Pipedrive
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/v1/persons` | GET | List persons (contacts) |
| `/v1/organizations` | GET | List organizations |
| `/v1/deals` | GET | List deals |
| `/v1/persons/search` | GET | Search persons |

### Zoho CRM
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/crm/v3/Contacts` | GET | List contacts |
| `/crm/v3/Accounts` | GET | List accounts |
| `/crm/v3/Deals` | GET | List deals |
| `/crm/v3/coql` | POST | Execute COQL query |

### Microsoft Dynamics 365
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/data/v9.2/contacts` | GET | Query contacts |
| `/api/data/v9.2/accounts` | GET | Query accounts |
| `/api/data/v9.2/opportunities` | GET | Query opportunities |

## Generic Query Templates

### Sales Pipeline Queries

| Query ID | Description | Parameters |
|----------|-------------|------------|
| `crm_pipeline_deals` | Open deals in specified pipeline | `{pipeline_id}` |
| `crm_deals_by_owner` | Pipeline grouped by owner | `{owner_field}` |
| `crm_deals_by_stage` | Deal count and value by stage | `{pipeline_id}` |
| `crm_deal_velocity` | Average time in each stage | `{pipeline_id}` |

### Contact Queries

| Query ID | Description | Parameters |
|----------|-------------|------------|
| `crm_search_contacts` | Search contacts by criteria | `email`, `name`, `company` |
| `crm_churn_risk_contacts` | Contacts with churn indicators | `{churn_indicator_field}` |
| `crm_inactive_customers` | Dormant paying customers | `days_inactive` |
| `crm_lifecycle_distribution` | Contacts by lifecycle stage | `{lifecycle_field}` |

### Company Queries

| Query ID | Description | Parameters |
|----------|-------------|------------|
| `crm_companies_by_segment` | Companies grouped by segment | `{segment_field}` |
| `crm_companies_by_owner` | Companies per sales owner | `{owner_field}` |
| `crm_company_details` | Full company profile | `company_id` |

## Process

### Step 1: Identify Platform and Connect

**HubSpot (via MCP):**
```
Call: hubspot_list_contact_properties to verify connection
```

**Salesforce (via API):**
```python
from simple_salesforce import Salesforce
sf = Salesforce(
    username="{SF_USERNAME}",
    password="{SF_PASSWORD}",
    security_token="{SF_SECURITY_TOKEN}",
    instance_url="{SF_INSTANCE_URL}"
)
```

**Pipedrive (via API):**
```python
import requests
base_url = "https://{PIPEDRIVE_DOMAIN}.pipedrive.com/api/v1"
params = {"api_token": "{PIPEDRIVE_API_TOKEN}"}
```

**Zoho CRM (via API):**
```python
headers = {
    "Authorization": f"Zoho-oauthtoken {access_token}",
    "Content-Type": "application/json"
}
base_url = "https://{ZOHO_API_DOMAIN}/crm/v3"
```

**Dynamics 365 (via API):**
```python
headers = {
    "Authorization": f"Bearer {access_token}",
    "OData-MaxVersion": "4.0",
    "OData-Version": "4.0"
}
base_url = "{DYNAMICS_URL}/api/data/v9.2"
```

### Step 2: Search or List Data

**HubSpot:**
```
Call: hubspot_search_contacts
Parameters:
  - email: "user@example.com" (optional)
  - limit: 100
  - properties: ["firstname", "lastname", "email", "lifecyclestage", "hs_lead_status"]
```

**Salesforce (SOQL):**
```sql
SELECT Id, FirstName, LastName, Email, Account.Name 
FROM Contact 
WHERE Email = 'user@example.com'
LIMIT 100
```

**Pipedrive:**
```
GET /v1/persons/search?term=user@example.com&fields=email
```

**Zoho (COQL):**
```sql
SELECT First_Name, Last_Name, Email, Account_Name 
FROM Contacts 
WHERE Email = 'user@example.com'
```

**Dynamics (OData):**
```
GET /api/data/v9.2/contacts?$filter=emailaddress1 eq 'user@example.com'&$select=firstname,lastname,emailaddress1
```

### Step 3: Query Deals/Opportunities

**HubSpot:**
```json
{
  "filterGroups": [{
    "filters": [{
      "propertyName": "pipeline",
      "operator": "EQ",
      "value": "{pipeline_id}"
    }, {
      "propertyName": "dealstage",
      "operator": "NEQ", 
      "value": "closedwon"
    }]
  }],
  "properties": ["dealname", "amount", "closedate", "dealstage", "hubspot_owner_id"]
}
```

**Salesforce:**
```sql
SELECT Id, Name, Amount, CloseDate, StageName, OwnerId 
FROM Opportunity 
WHERE StageName != 'Closed Won' AND Pipeline__c = '{pipeline_id}'
```

**Pipedrive:**
```
GET /v1/deals?pipeline_id={pipeline_id}&status=open
```

**Zoho:**
```sql
SELECT Deal_Name, Amount, Closing_Date, Stage, Owner 
FROM Deals 
WHERE Stage != 'Closed Won' AND Pipeline = '{pipeline_id}'
```

**Dynamics:**
```
GET /api/data/v9.2/opportunities?$filter=statecode eq 0&$select=name,estimatedvalue,estimatedclosedate,stepname
```

### Step 4: Format Results

Return structured output with:
- Total count
- Key metrics (total amount, average deal size)
- Top records

## Common Property/Field Mappings

### Contact Properties

| Concept | HubSpot | Salesforce | Pipedrive | Zoho | Dynamics |
|---------|---------|------------|-----------|------|----------|
| First Name | `firstname` | `FirstName` | `first_name` | `First_Name` | `firstname` |
| Last Name | `lastname` | `LastName` | `last_name` | `Last_Name` | `lastname` |
| Email | `email` | `Email` | `email[0].value` | `Email` | `emailaddress1` |
| Phone | `phone` | `Phone` | `phone[0].value` | `Phone` | `telephone1` |
| Company | `company` | `Account.Name` | `org_id` | `Account_Name` | `parentcustomerid` |
| Lifecycle | `lifecyclestage` | `Status__c` | `label` | `Contact_Status` | `statecode` |
| Owner | `hubspot_owner_id` | `OwnerId` | `owner_id` | `Owner` | `ownerid` |

### Company/Account Properties

| Concept | HubSpot | Salesforce | Pipedrive | Zoho | Dynamics |
|---------|---------|------------|-----------|------|----------|
| Name | `name` | `Name` | `name` | `Account_Name` | `name` |
| Domain | `domain` | `Website` | `- (custom)` | `Website` | `websiteurl` |
| Industry | `industry` | `Industry` | `- (custom)` | `Industry` | `industrycode` |
| Revenue | `annualrevenue` | `AnnualRevenue` | `- (custom)` | `Annual_Revenue` | `revenue` |
| Employees | `numberofemployees` | `NumberOfEmployees` | `people_count` | `Employees` | `numberofemployees` |

### Deal/Opportunity Properties

| Concept | HubSpot | Salesforce | Pipedrive | Zoho | Dynamics |
|---------|---------|------------|-----------|------|----------|
| Name | `dealname` | `Name` | `title` | `Deal_Name` | `name` |
| Amount | `amount` | `Amount` | `value` | `Amount` | `estimatedvalue` |
| Close Date | `closedate` | `CloseDate` | `expected_close_date` | `Closing_Date` | `estimatedclosedate` |
| Stage | `dealstage` | `StageName` | `stage_id` | `Stage` | `stepname` |
| Pipeline | `pipeline` | `- (record type)` | `pipeline_id` | `Pipeline` | `- (custom)` |
| Owner | `hubspot_owner_id` | `OwnerId` | `user_id` | `Owner` | `ownerid` |

## Output Schema

```json
{
  "query_type": "string",
  "platform": "{crm_type}",
  "executed_at": "ISO timestamp",
  "total_count": "number",
  "results": [
    {
      "id": "string",
      "properties": {
        "property_name": "value"
      }
    }
  ],
  "summary": {
    "total_records": "number",
    "key_metrics": {}
  }
}
```

## Rate Limiting

| Platform | Rate Limit | Recommendation |
|----------|-----------|----------------|
| **HubSpot** | 100 req/10s (private apps) | 100ms delay between requests |
| **Salesforce** | 100,000/day, 25/sec (burst) | Batch queries with SOQL |
| **Pipedrive** | 100 req/10s | 100ms delay between requests |
| **Zoho** | 60 req/min (standard) | 1s delay for bulk operations |
| **Dynamics** | 60,000/5min | Use batch requests for bulk |

## Quality Criteria

- [ ] Query executes without error
- [ ] Results match expected schema
- [ ] No rate limit errors
- [ ] Proper pagination for large result sets
- [ ] No PII exposed unnecessarily

## Platform-Specific Notes

### HubSpot
- Properties must be explicitly requested
- Use search endpoint for complex filtering
- Pipeline IDs are numeric strings

### Salesforce
- SOQL has 100 record default limit, max 2000
- Relationship queries for related objects
- Custom fields end with `__c`

### Pipedrive
- Filter IDs required for custom filtering
- Persons vs Organizations (not Contacts vs Companies)
- Pagination via `start` and `limit` params

### Zoho
- COQL for complex queries (like SQL)
- Module names are pluralized
- Custom fields use API names

### Microsoft Dynamics
- OData query syntax
- Use `$expand` for related records
- Entity names are lowercase and pluralized

## Known Limitations

1. **Custom fields vary** - always check client's specific field names
2. **Write operations** may require elevated permissions
3. **Email tracking** may need additional modules/licenses
4. **Rate limits** differ significantly between platforms

## Notes

- Always verify entity/field names from client configuration
- Use `properties` parameter (where available) to reduce response size
- Check owner/user IDs for ownership analysis
- Test queries with small limits before bulk operations
