# answer, at Intelligence Pick

The cohort format `answer` (first approved at RoomRacer, everfields/roomracer#40), in Intelligence Pick's own look and with its own questions and picks. **Not approved here yet:** `format.json` has `"approved": null` until Carlos answers this company's strategy gate in everfields/intelligence-ranking, which also asks him to change the charter's "bot-run social posting" line.

- **Audience:** US adults about to buy something in a category the site covers, who search YouTube for "best X" or "which X should I buy".
- **Promise:** one question a buyer asks before paying, answered in about 20 seconds with the pick the live page shows that day: the product, the reason, who it is not for, the picks by need and the criteria, in the page's own words.
- **Hook (first second):** the buyer's question in large type, read by the voice ("Which over-ear headphones should you buy?").
- **Payoff:** the AI pick as the page shows it ("AI pick (line)", the product, "Not for: …"), then the page of ours that has the rest. Never a store link, never Amazon.
- **Why follow:** each Short is the next category a buyer searches, with a dated answer from a named model.
- **What is said about the model:** "an AI model" and its name, Claude Opus 5.5, with "from its trained knowledge, without web search" and "not a hands-on test". The .com shows one model's pick, so no video says anything about models agreeing or disagreeing (decisions D-005 and D-009 in the company repo). If a market site with two seats is ever used, a split is written neutrally: "Claude chooses X; GPT names another brand: Y".
- **Which picks:** only released pages of tranche 1, and only picks the dated current-product check marks `current` (`data/fresh/us/`). A pick marked `newer_generation`, `line_gone` or `unclear` is not used.
- **Look:** the site's dark theme (`#151513`, text `#ecebe7`, the green `#5fc795`, the violet `#a99bff` kept for the AI pick pill), Inter, the one-colour wordmark. `brand.json`.
- **Scenes:** `hook`, `verdict` (added here: the page's pick card), `facts` (picks by need, or criteria), `compare` (`wide` for words such as "Filament" and "Resin"), `end`. No prices: the site shows none until they come from Amazon's API. Vary the scene order from one post to the next so no two posts share a sequence.
- **Voice:** Kokoro `am_michael`, a stock synthetic voice, different from RoomRacer's and Every Little Room's; the fine print says so. Plain and calm, like the site.
- **Sound:** the voice and the engine's quiet bed.
- **Fine print, on every frame:** "Chosen by an AI model (Claude Opus 5.5) from its trained knowledge, without web search. Not a hands-on test. Synthetic voice. As an Amazon Associate I earn from qualifying purchases."
- **Never appears:** logos, product or brand photos, star ratings, "Top 10", deal badges, prices, a claim of testing, a claim about models agreeing, faces, fake urgency.
- **YouTube:** the title is the buyer's search; the description links to the page with UTM tags and carries the disclosure; "not made for kids".
