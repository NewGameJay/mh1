---
name: product-positioning-matrix
description: |
  Generate product positioning matrices for competitive differentiation and tier-based value propositions.
  Use when asked to 'create positioning matrix', 'build competitive positioning', 'map value props by tier',
  'compare product tiers', or 'generate positioning framework'.
license: Proprietary
compatibility:
  - Any CRM (for product/tier data)
  - Research documents (competitor analysis)
  - Interview transcripts (customer insights)
metadata:
  author: mh1-engineering
  version: "1.0.0"
  status: experimental
  created: "2026-01-28"
  estimated_runtime: "2-5min"
  max_cost: "$1.00"
  client_facing: true
  requires_human_review: true
  tags:
    - positioning
    - strategy
    - product
    - competitive-analysis
    - marketing
allowed-tools: Read Write CallMcpTool
---

# Product Positioning Matrix Skill

Generate strategic product positioning matrices that map value propositions across product tiers, customer segments, and competitive alternatives.

## When to Use

Use this skill when you need to:
- Create positioning frameworks for multi-tier products
- Map value propositions to customer segments
- Build competitive positioning matrices
- Define differentiation by tier or segment
- Prepare positioning documentation for marketing

Do NOT use when:
- You lack competitor research (run `research-competitors` first)
- You lack ICP/persona data (run `extract-audience-persona` first)
- You're doing general product strategy (this is specifically for positioning matrices)

---

## Dependencies

| Type | Skill/Resource | Purpose | Required |
|------|---------------|---------|----------|
| Skill | `research-competitors` | Competitive landscape data | Recommended |
| Skill | `extract-audience-persona` | ICP/persona data | Recommended |
| Skill | `extract-pov` | Brand POV context | Optional |
| Input | Product/tier information | Tier definitions, pricing | Required |

---

## Inputs

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `client_id` | string | yes | - | Client identifier |
| `products` | array | yes | - | Product tiers to position |
| `competitors` | array | no | auto-load | Competitors to position against |
| `target_segments` | array | no | auto-load | ICP segments to address |
| `positioning_dimensions` | array | no | default set | Dimensions to compare |
| `include_messaging` | boolean | no | true | Generate sample messaging |

### Product Tier Structure

```yaml
products:
  - tier_name: "Free"
    pricing: "$0/month"
    key_features: ["Feature A", "Feature B"]
    target_use_case: "Individuals, trial users"

  - tier_name: "Pro"
    pricing: "$29/month"
    key_features: ["Everything in Free", "Feature C", "Feature D"]
    target_use_case: "Small teams, growing businesses"

  - tier_name: "Enterprise"
    pricing: "Custom"
    key_features: ["Everything in Pro", "Feature E", "SSO", "SLA"]
    target_use_case: "Large organizations, regulated industries"
```

---

## Positioning Dimensions (Default Set)

| Dimension | Description | Sample Values |
|-----------|-------------|---------------|
| `price_value` | Price-to-value positioning | "Premium", "Value", "Budget" |
| `target_company_size` | Company size fit | "SMB", "Mid-Market", "Enterprise" |
| `complexity` | Product complexity | "Simple", "Moderate", "Complex" |
| `support_level` | Support offering | "Self-serve", "Standard", "White-glove" |
| `customization` | Customization options | "Standard", "Configurable", "Fully Custom" |
| `use_case_focus` | Primary use case | "Operational", "Strategic", "Both" |
| `integration_depth` | Integration capabilities | "Basic", "Moderate", "Deep" |
| `time_to_value` | Onboarding speed | "Instant", "Days", "Weeks" |

---

## Process

### Step 1: Load Research Context

```python
# Load competitor research if available
competitors_path = f"clients/{client_id}/research/competitors.md"
competitors = load_if_exists(competitors_path)

# Load ICP/persona data if available
personas_path = f"clients/{client_id}/research/personas.md"
personas = load_if_exists(personas_path)

# Load company POV if available
pov_path = f"clients/{client_id}/research/pov.md"
pov = load_if_exists(pov_path)
```

### Step 2: Build Product Tier Matrix

For each product tier, evaluate across all positioning dimensions:

```python
def build_tier_matrix(products, dimensions):
    matrix = {}

    for tier in products:
        matrix[tier["tier_name"]] = {
            dim: evaluate_dimension(tier, dim)
            for dim in dimensions
        }

    return matrix
```

### Step 3: Build Competitive Matrix

Position each tier against competitors:

```python
def build_competitive_matrix(products, competitors, dimensions):
    matrix = []

    for product in products + competitors:
        row = {
            "name": product["name"],
            "type": "our_product" if product in products else "competitor"
        }

        for dim in dimensions:
            row[dim] = evaluate_dimension(product, dim)

        matrix.append(row)

    return matrix
```

### Step 4: Map Value Props to Segments

For each ICP segment, identify best-fit tier and key messaging:

```python
def map_segments_to_tiers(products, segments):
    mapping = []

    for segment in segments:
        best_tier = find_best_tier(products, segment)

        mapping.append({
            "segment": segment["name"],
            "recommended_tier": best_tier["tier_name"],
            "key_value_props": generate_value_props(best_tier, segment),
            "primary_pain_point": segment["pain_points"][0],
            "messaging_angle": generate_messaging_angle(best_tier, segment)
        })

    return mapping
```

### Step 5: Generate Differentiation Summary

Identify key differentiators for each tier:

```python
def generate_differentiators(products, competitors):
    differentiators = []

    for tier in products:
        tier_diffs = {
            "tier": tier["tier_name"],
            "vs_competitors": [],
            "vs_other_tiers": []
        }

        # Compare against competitors at similar price point
        for comp in competitors:
            if is_similar_price_point(tier, comp):
                tier_diffs["vs_competitors"].append({
                    "competitor": comp["name"],
                    "advantage": find_advantage(tier, comp),
                    "gap": find_gap(tier, comp)
                })

        # Compare against other tiers
        for other in products:
            if other != tier:
                tier_diffs["vs_other_tiers"].append({
                    "tier": other["tier_name"],
                    "upgrade_reason": get_upgrade_reason(tier, other)
                })

        differentiators.append(tier_diffs)

    return differentiators
```

### Step 6: Generate Sample Messaging (Optional)

```python
def generate_messaging(tier, segment):
    return {
        "headline": f"{tier['tier_name']}: {generate_headline(tier, segment)}",
        "subheadline": generate_subheadline(tier, segment),
        "key_benefits": [
            generate_benefit(tier, segment, b)
            for b in tier["key_features"][:3]
        ],
        "cta": generate_cta(tier, segment)
    }
```

---

## Output Schema

```json
{
  "positioning_matrix": {
    "products": [
      {
        "tier_name": "string",
        "pricing": "string",
        "dimensions": {
          "price_value": "string",
          "target_company_size": "string",
          "complexity": "string",
          "support_level": "string"
        }
      }
    ],
    "competitive_comparison": [
      {
        "name": "string",
        "type": "our_product | competitor",
        "dimensions": {}
      }
    ]
  },
  "segment_mapping": [
    {
      "segment": "string",
      "recommended_tier": "string",
      "key_value_props": ["string"],
      "primary_pain_point": "string",
      "messaging_angle": "string"
    }
  ],
  "differentiators": [
    {
      "tier": "string",
      "vs_competitors": [
        {
          "competitor": "string",
          "advantage": "string",
          "gap": "string"
        }
      ],
      "vs_other_tiers": [
        {
          "tier": "string",
          "upgrade_reason": "string"
        }
      ]
    }
  ],
  "messaging": [
    {
      "tier": "string",
      "segment": "string",
      "headline": "string",
      "subheadline": "string",
      "key_benefits": ["string"],
      "cta": "string"
    }
  ],
  "_meta": {
    "client_id": "string",
    "generated_at": "ISO timestamp",
    "research_sources": ["string"]
  }
}
```

---

## Quality Criteria

- [ ] All product tiers are represented in the matrix
- [ ] All specified dimensions are evaluated
- [ ] Competitive positioning is factual (based on research)
- [ ] Segment mapping is actionable
- [ ] Differentiators are specific (not generic claims)
- [ ] Messaging aligns with brand voice (if POV available)

---

## Example Usage

**Generate positioning matrix for membership tiers:**
```
Create product positioning matrix for client_id=ffc with tiers: Free, Member, Founding
```

**Full positioning with competitive analysis:**
```
Build positioning matrix for ffc including competitors: [Brand A, Brand B]
```

**Positioning with segment mapping:**
```
Generate positioning matrix for ffc mapping to segments: [Solo Founders, Growth Stage, Established]
```

---

## Sample Output

```json
{
  "positioning_matrix": {
    "products": [
      {
        "tier_name": "Community (Free)",
        "pricing": "$0/month",
        "dimensions": {
          "price_value": "Entry",
          "target_company_size": "Solo/Early-stage",
          "complexity": "Simple",
          "support_level": "Self-serve",
          "time_to_value": "Instant"
        }
      },
      {
        "tier_name": "Member",
        "pricing": "$99/month",
        "dimensions": {
          "price_value": "Value",
          "target_company_size": "Growth-stage",
          "complexity": "Moderate",
          "support_level": "Standard",
          "time_to_value": "Days"
        }
      },
      {
        "tier_name": "Founding",
        "pricing": "$499/month",
        "dimensions": {
          "price_value": "Premium",
          "target_company_size": "Established",
          "complexity": "Comprehensive",
          "support_level": "Concierge",
          "time_to_value": "Weeks (high-touch)"
        }
      }
    ]
  },
  "segment_mapping": [
    {
      "segment": "Solo Founders",
      "recommended_tier": "Community (Free)",
      "key_value_props": [
        "Access to community forums",
        "Monthly virtual events",
        "Resource library"
      ],
      "primary_pain_point": "Isolation and lack of peer support",
      "messaging_angle": "You're not alone. Join 10,000+ founders."
    },
    {
      "segment": "Growth-Stage Founders",
      "recommended_tier": "Member",
      "key_value_props": [
        "Mastermind groups",
        "Expert office hours",
        "Partner discounts"
      ],
      "primary_pain_point": "Scaling challenges without experienced guidance",
      "messaging_angle": "Accelerate growth with proven playbooks."
    }
  ],
  "differentiators": [
    {
      "tier": "Member",
      "vs_competitors": [
        {
          "competitor": "Generic Business Network",
          "advantage": "Curated for female founders only",
          "gap": "Smaller total network size"
        }
      ],
      "vs_other_tiers": [
        {
          "tier": "Founding",
          "upgrade_reason": "Access to 1:1 coaching and executive events"
        }
      ]
    }
  ]
}
```

---

## Human Review Required

This skill requires human review for:
- [ ] Competitive claims accuracy
- [ ] Messaging tone and brand alignment
- [ ] Pricing strategy sensitivity
- [ ] Segment-tier fit validation

---

## Notes

- **Research first**: Best results when competitor and persona research is complete
- **Iterate**: Positioning matrices should be revisited quarterly
- **Output location**: `clients/{client_id}/strategy/positioning-matrix.md`
- **Dependencies**: Works best with `research-competitors` and `extract-audience-persona` outputs

---

## Changelog

### v1.0.0 (2026-01-28)
- Initial release
- Multi-tier product positioning
- Competitive matrix generation
- Segment-to-tier mapping
- Sample messaging generation
