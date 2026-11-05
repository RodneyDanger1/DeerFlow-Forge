# W3-B recon — blind critic and verdict resolution

**Target:** implement the critic contract, not a vision model. It validates a blind critique, rejects
uncited/contradictory claims, and resolves critic vs gate vs human intent without letting the critic
override a failed gate.

- **Entry:** future `FAMILIES` episode pipeline after `forge_verifier.verify_artifact`.
- **Data:** brief + artifact refs (not gate report) -> critique JSON; gate verdict + critique + optional
  human decision -> final verdict.
- **Tests:** valid pass; missing crop; empty observation; pass with major defect; gate fail + critic
  pass; gate pass + critic fail -> needs_human; gate missing -> unverified; blind leak (`exit code`);
  human reject.
- **Unknowns:** no vision model/deepseek-flash accuracy measurement; no human rubric here.
- **Files:** `blueprint/files/forge_critic.py`, `tests/test_forge_critic.py`.
- **Non-goals:** no model call, no promotion, no production write.
