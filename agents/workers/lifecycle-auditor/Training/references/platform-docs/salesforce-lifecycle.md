# Platform Reference: Salesforce Lifecycle Stages

## Overview

**Platform**: Salesforce CRM
**Connection Method**: MCP Server (salesforce) or API
**Rate Limits**: API limits vary by edition (see below)

## Authentication

```yaml
# Required credentials
credentials:
  - name: SF_CLIENT_ID
    type: oauth_client
    source: environment
  - name: SF_CLIENT_SECRET
    type: secret
    source: environment
  - name: SF_REFRESH_TOKEN
    type: oauth_refresh
    source: environment
  - name: SF_INSTANCE_URL
    type: url
    source: environment
```

## Lifecycle Model Differences

Unlike HubSpot's unified lifecycle stage field, Salesforce uses different models depending on the object:

| Object | Lifecycle Field | Notes |
|--------|-----------------|-------|
| Lead | `Status` | Standard picklist |
| Contact | Custom field required | Usually `Lifecycle_Stage__c` |
| Account | Custom field required | Usually `Customer_Stage__c` |
| Opportunity | `StageName` | Pipeline stages, not lifecycle |

## Lead Status Model (Standard)

### Default Lead Statuses

| Status | Internal Value | Description |
|--------|----------------|-------------|
| Open - Not Contacted | Open | New lead, no outreach |
| Working - Contacted | Working | In active conversation |
| Closed - Converted | Converted | Became Contact/Opportunity |
| Closed - Not Converted | Closed | Disqualified or lost |

### Lead Conversion

When a Lead converts in Salesforce:
1. Lead record becomes read-only
2. Contact record created (or existing matched)
3. Account record created (or existing matched)
4. Opportunity optionally created

**Important for Audits**: Converted leads must be queried separately:
```sql
SELECT Id, Status, ConvertedDate, ConvertedContactId
FROM Lead
WHERE IsConverted = true
```

## Custom Lifecycle Stage Model

Most Salesforce implementations create a custom `Lifecycle_Stage__c` field on Contact.

### Common Custom Stages

| Stage | Description | Equivalent HubSpot |
|-------|-------------|-------------------|
| Prospect | Identified but not engaged | Subscriber |
| Engaged | Showing interest | Lead |
| MQL | Marketing qualified | Marketing Qualified Lead |
| SAL | Sales accepted | (HubSpot doesn't have) |
| SQL | Sales qualified | Sales Qualified Lead |
| Opportunity | Active deal | Opportunity |
| Customer | Closed-won | Customer |
| Champion | Active promoter | Evangelist |

### Stage Discovery

Always discover actual stage values before analysis:

```python
# Query picklist values for custom field
def get_lifecycle_stages(field_name="Lifecycle_Stage__c"):
    result = mcp.salesforce.describe_sobject("Contact")
    field = next(f for f in result["fields"] if f["name"] == field_name)
    return [option["value"] for option in field["picklistValues"] if option["active"]]
```

## Key Endpoints/Operations

### Operation 1: Query Contacts by Lifecycle Stage

**Purpose**: Get contacts in a specific lifecycle stage

**Request (SOQL)**:
```sql
SELECT Id, Email, FirstName, LastName, AccountId, Account.Name,
       Lifecycle_Stage__c, CreatedDate, Lifecycle_Stage_Date__c
FROM Contact
WHERE Lifecycle_Stage__c = 'Customer'
LIMIT 500
```

**Via MCP**:
```python
result = mcp.salesforce.query("""
    SELECT Id, Email, FirstName, LastName, AccountId, Account.Name,
           Lifecycle_Stage__c, CreatedDate
    FROM Contact
    WHERE Lifecycle_Stage__c = 'Customer'
    LIMIT 500
""")
```

**Response**:
```json
{
  "totalSize": 127,
  "done": true,
  "records": [
    {
      "Id": "003xxx",
      "Email": "jane@acme.com",
      "FirstName": "Jane",
      "LastName": "Doe",
      "AccountId": "001xxx",
      "Account": {"Name": "Acme Corp"},
      "Lifecycle_Stage__c": "Customer",
      "CreatedDate": "2024-03-15T10:30:00.000+0000"
    }
  ]
}
```

### Operation 2: Get Stage Distribution (Aggregate Query)

**Purpose**: Count contacts in each lifecycle stage

**Request**:
```sql
SELECT Lifecycle_Stage__c, COUNT(Id) contact_count
FROM Contact
WHERE Lifecycle_Stage__c != null
GROUP BY Lifecycle_Stage__c
```

**Response**:
```json
{
  "totalSize": 6,
  "done": true,
  "records": [
    {"Lifecycle_Stage__c": "Prospect", "contact_count": 450},
    {"Lifecycle_Stage__c": "MQL", "contact_count": 180},
    {"Lifecycle_Stage__c": "SQL", "contact_count": 120},
    {"Lifecycle_Stage__c": "Opportunity", "contact_count": 85},
    {"Lifecycle_Stage__c": "Customer", "contact_count": 95}
  ]
}
```

### Operation 3: Query with Opportunity Data

**Purpose**: Join Contact lifecycle with Opportunity pipeline

**Request**:
```sql
SELECT Id, Email, Lifecycle_Stage__c,
       (SELECT Id, StageName, Amount, CloseDate FROM Opportunities WHERE IsClosed = false)
FROM Contact
WHERE Lifecycle_Stage__c IN ('SQL', 'Opportunity')
```

## Data Models

### Contact Object (Lifecycle-relevant fields)

```json
{
  "Id": "string (18-char Salesforce ID)",
  "Email": "string",
  "FirstName": "string",
  "LastName": "string",
  "AccountId": "string (reference to Account)",
  "Lifecycle_Stage__c": "picklist (custom)",
  "Lifecycle_Stage_Date__c": "datetime (custom)",
  "CreatedDate": "datetime",
  "LastActivityDate": "date",
  "LastModifiedDate": "datetime"
}
```

### Lead Object (Pre-conversion lifecycle)

```json
{
  "Id": "string",
  "Email": "string",
  "FirstName": "string",
  "LastName": "string",
  "Company": "string",
  "Status": "picklist",
  "LeadSource": "picklist",
  "CreatedDate": "datetime",
  "ConvertedDate": "datetime (null if not converted)",
  "ConvertedContactId": "string (null if not converted)",
  "IsConverted": "boolean"
}
```

## Query Patterns

### Pattern 1: Combined Lead + Contact Funnel

```sql
-- Pre-conversion funnel (Leads)
SELECT Status stage, COUNT(Id) count, 'Lead' object_type
FROM Lead
WHERE IsConverted = false AND Status != 'Closed - Not Converted'
GROUP BY Status

UNION ALL

-- Post-conversion funnel (Contacts)
SELECT Lifecycle_Stage__c stage, COUNT(Id) count, 'Contact' object_type
FROM Contact
WHERE Lifecycle_Stage__c != null
GROUP BY Lifecycle_Stage__c
```

**Note**: UNION not supported in standard SOQL; requires two queries and client-side merge.

### Pattern 2: Cohort by Created Date

```sql
SELECT Lifecycle_Stage__c,
       COUNT(Id) contact_count,
       CALENDAR_MONTH(CreatedDate) created_month,
       CALENDAR_YEAR(CreatedDate) created_year
FROM Contact
WHERE CreatedDate >= 2024-01-01T00:00:00Z
GROUP BY Lifecycle_Stage__c, CALENDAR_MONTH(CreatedDate), CALENDAR_YEAR(CreatedDate)
ORDER BY CALENDAR_YEAR(CreatedDate), CALENDAR_MONTH(CreatedDate)
```

### Pattern 3: At-Risk Customers (No Recent Activity)

```sql
SELECT Id, Email, FirstName, LastName, Account.Name, LastActivityDate
FROM Contact
WHERE Lifecycle_Stage__c = 'Customer'
  AND (LastActivityDate < LAST_N_DAYS:45 OR LastActivityDate = null)
ORDER BY LastActivityDate NULLS FIRST
LIMIT 200
```

### Pattern 4: Conversion Velocity

```sql
SELECT Id, Email, CreatedDate, Lifecycle_Stage_Date__c,
       Account.Name, Lifecycle_Stage__c
FROM Contact
WHERE Lifecycle_Stage__c = 'Customer'
  AND Lifecycle_Stage_Date__c >= 2024-01-01T00:00:00Z
```

Calculate velocity client-side:
```python
velocity_days = (contact["Lifecycle_Stage_Date__c"] - contact["CreatedDate"]).days
```

## API Limits by Edition

| Edition | Daily API Requests | Query Rows/Request |
|---------|-------------------|-------------------|
| Professional | 15,000 + (users x 15) | 50,000 |
| Enterprise | 100,000 + (users x 100) | 50,000 |
| Unlimited | 100,000 + (users x 200) | 50,000 |

**For Lifecycle Audits**: Typically need 5-20 API calls per audit (well within limits)

## Best Practices

1. **Use SOQL queries** - More efficient than REST API for bulk data
2. **Paginate large results** - Use `queryMore()` for >2000 records
3. **Include relationship queries** - Get Account data in same call (reduce API usage)
4. **Check field-level security** - Some fields may not be queryable for all profiles
5. **Handle null stages** - Many contacts may have empty lifecycle fields

## MH1-Specific Usage

### Via MCP

```python
from lib.mcp_client import SalesforceClient

sf = SalesforceClient()

# Get stage distribution
distribution = sf.query("""
    SELECT Lifecycle_Stage__c, COUNT(Id) cnt
    FROM Contact
    WHERE Lifecycle_Stage__c != null
    GROUP BY Lifecycle_Stage__c
""")

# Get detailed contacts for analysis
contacts = sf.query("""
    SELECT Id, Email, FirstName, LastName, AccountId, Account.Name,
           Lifecycle_Stage__c, CreatedDate, LastActivityDate
    FROM Contact
    WHERE Lifecycle_Stage__c IN ('MQL', 'SQL', 'Opportunity', 'Customer')
    LIMIT 2000
""")
```

### Field Name Discovery

Salesforce field names vary by org. Use this pattern:

```python
def discover_lifecycle_field(sf_client):
    # Check common custom field names
    candidates = [
        "Lifecycle_Stage__c",
        "LifecycleStage__c",
        "Contact_Lifecycle__c",
        "Customer_Stage__c",
        "Contact_Status__c"
    ]

    contact_fields = sf_client.describe_sobject("Contact")["fields"]
    field_names = [f["name"] for f in contact_fields]

    for candidate in candidates:
        if candidate in field_names:
            return candidate

    # Not found - return None and handle in calling code
    return None
```

## Troubleshooting

### Issue: Custom lifecycle field not found

**Symptoms**: Query fails with "No such column" error

**Cause**: Custom field name differs from expected, or field doesn't exist

**Solution**:
1. Run `describe_sobject("Contact")` to list all fields
2. Search for fields containing "lifecycle", "stage", or "status"
3. Update query with correct field name

### Issue: Missing Account relationships

**Symptoms**: AccountId is null for many Contacts

**Cause**: Salesforce allows Contacts without Account (private contacts)

**Solution**:
1. Filter to Contacts with AccountId != null for B2B analysis
2. Or include private contacts but segment results

### Issue: Lead conversion not tracked

**Symptoms**: Can't trace Lead to Contact journey

**Cause**: Need to query Lead with ConvertedContactId

**Solution**:
```sql
-- Get converted leads and their contact IDs
SELECT Id, Email, Status, ConvertedDate, ConvertedContactId
FROM Lead
WHERE IsConverted = true AND ConvertedDate >= 2024-01-01T00:00:00Z
```

Then join client-side with Contact data.

## Mapping HubSpot to Salesforce

For multi-CRM clients or migrations:

| HubSpot Stage | Salesforce Lead Status | Salesforce Contact Stage |
|---------------|------------------------|--------------------------|
| subscriber | Open - Not Contacted | Prospect |
| lead | Working - Contacted | Engaged |
| marketingqualifiedlead | Working - Contacted | MQL |
| salesqualifiedlead | (Lead converted) | SQL |
| opportunity | (Lead converted) | Opportunity |
| customer | (Lead converted) | Customer |
| evangelist | (Lead converted) | Champion |

## Changelog

| Date | Change | Impact |
|------|--------|--------|
| 2024-03 | SOQL query timeout increased | Larger queries possible |
| 2024-09 | New Person Account model | May need different query patterns |
| 2025-01 | Einstein Activity Capture | More activity data available |
