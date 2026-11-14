# Formats: the creative engine. The mechanics travel inside a cohort; the content never does

A format is a hypothesis: who it is for, the hook in the first second, the payoff, and why someone would follow. A new caption is not a new format. **It must pass the buyer test:** the first second is a question the buyer asks before paying, and the post ends at what the company sells that answers it. For a store, that is the product on the shelf, never the site's own tech demo (RoomRacer's Hot Laps were rejected for that, D-007). Each one lives in its own folder:

- `brief.md`: the approved direction: audience, promise, hook, look, voice, sound, and what never appears. Carlos approves it with 3 sample renders, in a strategy gate.
- `make.py`: the generator, run by `engine/pc/render.py`. It defines `make(post, out_dir, kit)` and returns `{"file": <path of the 9:16 mp4>, "ai": {"generated": bool, "realistic": bool}}`. `kit` gives it the image and video models, the voice, type and the final cut.
- `format.json`:
  - `"gpu": false` lets `social-render.yml` render it on GitHub's free runner when a batch lands in `batches/`. Without it, the format is the PC's.
  - `"approved"`: this company's own gate (`owner/repo#N`). Until it is set, every batch that uses the format is refused whole: a format the founder has not approved, or has rejected, never reaches the queue.
  - `"cohorts"`: the kinds of business the mechanics fit.
- `../brand.json` (the repo's root): the company's name, colours, site, currency, units and voice. A format reads it, so the same mechanics look and sound like each company.
- `samples/`: the renders the founder approved.

`answer` is a ready, code-only cohort format for any store or affiliate, first approved at RoomRacer (everfields/roomracer#40). It answers one question per video with the store's own numbers, using type, a to-scale plan and a stock voice. Copy it from the skill's `engine/social/templates/formats/answer/`, fill `brand.json`, and write its specs from the company's own pages. The registry of cohort formats, with what each did, is the skill's `knowledge/social-formats.md`.

Code holds the layout, the type and the brand; open models add images, motion, voice and music; Claude writes the scripts. Every post carries something new: new pixels around the same content are not new content.
