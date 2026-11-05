# UI/agent bug audit — gate and findings

## Control inventory (real built console, desktop + mobile)

| Section | Controls exercised | Verdict |
|---|---|---|
| Board | 5 route radios, 2 toggles, Run route, rerun | WIRED-AND-WORKS |
| Routes | 5 route sections, expansion | WIRED-AND-WORKS; open section does not collapse (intentional single-open? recorded, not fixed) |
| Sandbox | Open runner.py → Sources | WIRED-AND-WORKS |
| Playbook | MCP server, products.json, compose.yml → Sources | WIRED-AND-WORKS |
| Sources | 34 file buttons, mobile select, Copy, Download | navigation/select/download WIRED; Copy status was not observable in headless because Clipboard API stayed pending |
| Mobile | nav, source select, overflow | no overflow, no console/page/request errors |

The visual smoke passed both viewports with no console/page/request errors.

## Gate — logic-gatekeeper

```json
{
  "phase1": {
    "architecture": "CopyButton owns transient copy status via copyText; ForgeService owns /healthz and delegates to a repository; ForgeVerifier owns gate-report validation. No production service is deployed.",
    "dataFlow": "click -> copyText -> navigator.clipboard.writeText (may hang) -> fallback execCommand -> setStatus -> rendered label. healthz -> loop -> repo.health -> JSON. verifier -> checks object -> named result.",
    "edgeCases": [
      "clipboard writeText promise never settles; button must not stay 'Copy' forever",
      "repo.health returns false or raises; /healthz must not return ok:true",
      "report.checks contains a non-object value; verifier must return E_REPORT_INVALID, not crash",
      "download URL revoked too early; download content must still be complete"
    ],
    "rootCause": "Three seams trust an external promise/record shape without a bounded fallback or named validation: clipboard can hang, health is hard-coded true, and a malformed gate check raises instead of refusing."
  }
}
```

**Phase 2:** validation at the service/verifier entry; clipboard gets a bounded wait and fallback; no caller signature changes except an optional health method.
