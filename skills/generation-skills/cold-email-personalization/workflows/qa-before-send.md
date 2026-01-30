<objective>
Run the 11-point QA checklist before sending any cold email. All items must pass before shipping.
</objective>

<checklist>
<item_1>
**First Line = Specific Signal**

Check: Does the first line reference a specific signal?
- Custom research signal with {{variable}}, OR
- AI-generated insight based on their company, OR
- Whole-offer strategy (subject + preview = full offer)

**Pass examples:**
- "Saw you hired 4 SEs last quarter—building custom workflows for every deal?"
- "Noticed you posted about {{ai_generation}}—seems like it was {{days}} days since the one before."

**Fail examples:**
- "I saw you're growing fast" (vague, unverifiable)
- "I noticed you're in the SaaS industry" (obvious, not specific)

**If fail:** Add specific signal from research OR switch to whole-offer strategy.
</item_1>

<item_2>
**No Hallucinations**

Check: Is every fact verifiable?
- Can you point to where you found each piece of information?
- Are you inventing: job titles, metrics, dates, technologies, company details?

**If you can't verify it, remove it.**

Don't invent:
- "Your team has been growing 40%" (unless you have data)
- "You recently launched a new product" (unless confirmed)
- Specific numbers you haven't verified
</item_2>

<item_3>
**Variables Formatted Correctly**

Check: All variables use `{{double_braces}}`
- {{first_name}} ✅
- {first_name} ❌ (single braces)
- {{firstName}} ❌ (use snake_case, not camelCase)

Also check:
- No typos in variable names
- Variables match your data source (Clay column names)
- All braces are closed
</item_3>

<item_4>
**No Banned Phrases**

Search and delete if found:

**Generic openers:**
- "I hope this email finds you well"
- "I wanted to reach out"
- "I hope you're doing well"
- "Just wanted to touch base"

**Weak value props:**
- "We help companies..." (unless followed immediately by case study proof)
- "Our solution..."
- "I wanted to show you..."

**High-pressure CTAs:**
- "Would love to schedule..."
- "Let's hop on a call"
- "Can I get 15 minutes on your calendar?"

**If found:** Delete and rewrite. Start with their situation, not about you.
</item_4>

<item_5>
**Recipient:Sender Ratio ≥ 2:1**

Count sentences:
- About THEM (situation, pain, goals): ____
- About US (product, features, ask): ____

**Target:** At least 2:1 (them:us)

**Good:**
```
Saw you hired 4 SEs (THEM)
Most teams hit a wall at deal #30 (INSIGHT)
Worth a look? (CTA)
Ratio: 2:1 ✅
```

**Bad:**
```
We help companies build workflows (US)
Our platform is used by 500+ companies (US)
We'd love to show you (US)
Ratio: 0:3 ❌
```

**If fail:** Rewrite to focus on them, not you.
</item_5>

<item_6>
**Word Count: 50-90 Words**

Count words (not including signature).

- **Under 50:** Might be too sparse—ensure all elements present
- **50-90:** Perfect range ✅
- **91-120:** Acceptable but try to cut
- **Over 120:** Too long—cut ruthlessly

**The 20-Second Rule:** Read aloud. If it takes longer than 20 seconds, it's too long.

**Cutting checklist:**
- [ ] Remove greeting ("I hope this finds you well")
- [ ] Remove "I wanted to" phrases
- [ ] Remove redundant context
- [ ] Combine sentences where possible
- [ ] Replace long phrases with short ones
- [ ] Delete adjectives unless they're specific data
</item_6>

<item_7>
**CTA = Low-Effort**

Check: Can they reply in 5 words or less?

**Good CTAs:**
- "Worth a quick look?" ✅
- "Is this still the case?" ✅
- "Curious—are you already doing X?" ✅
- "Just confirm [example] or any others" ✅

**Bad CTAs:**
- "Can we schedule 15 minutes next week?" ❌ (requires calendar check)
- "Let me know your thoughts" ❌ (vague)
- "Would you be interested in learning more?" ❌ (requires thinking)

**If asking for meeting, add value-exchange:**
- "...so I can show you the engagers of your competitor's last 10 posts"
- "...to walk you through 3 custom ideas for {{company}}"
</item_7>

<item_8>
**Reads Naturally Aloud**

Read the email out loud.

Check:
- Does it sound like a human wrote it?
- Or does it sound like a template/robot?
- Are there awkward phrases?
- Does the flow make sense?

**Common issues:**
- Too formal/stiff
- Run-on sentences
- Choppy/disconnected thoughts
- Obvious template language
</item_8>

<item_9>
**Em Dashes Consistent**

Check punctuation:
- Use: "—" (proper em dash) ✅
- Not: "--" (double hyphen) ❌
- Not: "–" (en dash) ❌

**Spacing:** No spaces around em dash
- "research—not just" ✅
- "research — not just" ❌

Also check:
- No double spaces (find/replace "  " → " ")
- Variables closed correctly
</item_9>

<item_10>
**Subject Line = 2-4 Words OR Whole Offer**

**Approach A: 2-4 Words (Intrigue)**
- "Partnership?" ✅
- "Quick question" ✅
- "Competitor insights" ✅
- "Quick question about your infrastructure roadmap" ❌ (too long, explaining)

**Approach B: Whole Offer**
- "Ever chase renters to pay on time?" ✅
- Only use this approach if first line completes the offer

**Test:** Could a colleague or customer send this subject? If yes, good.
</item_10>

<item_11>
**"Would I Reply?" Test**

Put yourself in recipient's shoes. Ask honestly:

1. Do they understand MY specific situation? (not just industry)
2. Is there a non-obvious insight I didn't know? (not just claims)
3. Is it low-effort to reply? (not big commitment)
4. Is there a good reason to engage NOW? (not just "someday")

**If any answer is "no":** Rewrite before sending.

This is the most important check. Everything else can pass, but if you wouldn't reply, neither will they.
</item_11>
</checklist>

<autofix_rules>
When fixing issues, apply these:

**Punctuation:**
- Replace "–" with "—" (en dash → em dash)
- Replace "--" with "—" (double hyphen → em dash)
- Trim double spaces globally

**Variables:**
- If format wrong `{single}` → fix to `{{double}}`
- If first line lacks variable → add signal OR flag for review

**Banned phrases:**
- Delete and rewrite surrounding sentence
- "I hope this finds you well" → Delete, start with situation
- "We help companies..." → Rewrite as "We helped [customer type] achieve [metric]"

**Length:**
- If >90 words → Apply cutting passes until under 90

**CTA:**
- If "15 minutes" or "30 minutes" → Change to "quick look?" or "worth exploring?"
</autofix_rules>

<scoring_sheet>
| Criteria | Pass | Fail | Notes |
|----------|------|------|-------|
| 1. First line = specific signal | ☐ | ☐ | |
| 2. No hallucinations | ☐ | ☐ | |
| 3. Variables formatted correctly | ☐ | ☐ | |
| 4. No banned phrases | ☐ | ☐ | |
| 5. Ratio ≥ 2:1 (them:us) | ☐ | ☐ | |
| 6. 50-90 words | ☐ | ☐ | Count: ___ |
| 7. CTA = low-effort | ☐ | ☐ | |
| 8. Reads naturally aloud | ☐ | ☐ | |
| 9. Em dashes consistent | ☐ | ☐ | |
| 10. Subject 2-4 words OR whole offer | ☐ | ☐ | |
| 11. "Would I reply?" = YES | ☐ | ☐ | |

**All boxes must be ✅ Pass before shipping.**
</scoring_sheet>

<output_format>
```json
{
  "qa_results": {
    "1_specific_signal": {"pass": true, "notes": ""},
    "2_no_hallucinations": {"pass": true, "notes": ""},
    "3_variables_formatted": {"pass": true, "notes": ""},
    "4_no_banned_phrases": {"pass": true, "notes": ""},
    "5_ratio": {"pass": true, "notes": "Ratio: 3:1"},
    "6_word_count": {"pass": true, "notes": "72 words"},
    "7_low_effort_cta": {"pass": true, "notes": ""},
    "8_reads_naturally": {"pass": true, "notes": ""},
    "9_em_dashes": {"pass": true, "notes": ""},
    "10_subject_line": {"pass": true, "notes": "3 words"},
    "11_would_i_reply": {"pass": true, "notes": ""}
  },
  "all_pass": true,
  "issues_found": [],
  "fixes_applied": [],
  "final_verdict": "SHIP IT"
}
```
</output_format>

<success_criteria>
- All 11 items pass
- Any failures are fixed before shipping
- Final email scores 85+ on rubric
- "Would I reply?" = YES
</success_criteria>
