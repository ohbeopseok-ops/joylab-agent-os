from __future__ import annotations

from importlib.metadata import PackageNotFoundError, version

from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from joylab_agent_os import CertificationPolicy


APP_NAME = "JoyLab Agent OS"
RUNTIME = "governed-learning"


def package_version() -> str:
    try:
        return version("joylab-agent-os")
    except PackageNotFoundError:
        return "0.6.5"


def capabilities_payload() -> dict[str, object]:
    return {
        "name": APP_NAME,
        "version": package_version(),
        "runtime": RUNTIME,
        "capabilities": [
            "skill-registry",
            "experience-logger",
            "evidence-builder",
            "certification-gate",
            "persistent-runtime-state",
            "scheduled-ingestion",
            "runtime-orchestrator",
            "persistent-lineage",
            "crash-reconciliation",
        ],
    }


def certification_policy_payload() -> dict[str, object]:
    policy = CertificationPolicy()
    return {
        "version": policy.version,
        "min_samples": policy.min_samples,
        "min_gold_cases": policy.min_gold_cases,
        "min_confidence": policy.min_confidence,
        "require_oos_pass": policy.require_oos_pass,
        "require_regression_pass": policy.require_regression_pass,
        "max_hard_gate_violations": policy.max_hard_gate_violations,
    }


app = FastAPI(
    title=APP_NAME,
    version=package_version(),
    description="Thin HTTP adapter for the governed JoyLab Agent OS runtime.",
)


@app.get("/api", tags=["runtime"])
def runtime_status() -> dict[str, object]:
    return {
        "name": APP_NAME,
        "version": package_version(),
        "status": "healthy",
        "runtime": RUNTIME,
    }


@app.get("/api/health", tags=["runtime"])
def health() -> dict[str, str]:
    return {"status": "healthy"}


@app.get("/api/version", tags=["runtime"])
def runtime_version() -> dict[str, str]:
    return {"name": APP_NAME, "version": package_version()}


@app.get("/api/capabilities", tags=["runtime"])
def capabilities() -> dict[str, object]:
    return capabilities_payload()


@app.get("/api/certification-policy", tags=["governance"])
def certification_policy() -> dict[str, object]:
    return certification_policy_payload()


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def dashboard() -> str:
    policy = certification_policy_payload()
    current_version = package_version()
    capability_count = len(capabilities_payload()["capabilities"])

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>JoyLab Agent OS</title>
  <style>
    :root {{ color-scheme: dark; font-family: Inter, ui-sans-serif, system-ui, sans-serif; }}
    body {{ margin:0; background:#07111f; color:#eaf2ff; }}
    main {{ max-width:1080px; margin:0 auto; padding:48px 24px 72px; }}
    h1 {{ margin:0 0 8px; font-size:clamp(32px,6vw,58px); letter-spacing:-.04em; }}
    .sub {{ color:#9bb0cc; margin-bottom:32px; }}
    .grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(220px,1fr)); gap:16px; }}
    .card {{ background:#0c1b2e; border:1px solid #17304d; border-radius:16px; padding:20px; }}
    .label {{ color:#8ca7c8; font-size:13px; text-transform:uppercase; letter-spacing:.08em; }}
    .value {{ font-size:26px; font-weight:700; margin-top:7px; }}
    .ok {{ color:#70e1a1; }}
    .pipeline {{ margin-top:18px; line-height:1.8; color:#c7d7eb; }}
    code {{ color:#8fc5ff; }}
    a {{ color:#8fc5ff; }}
  </style>
</head>
<body>
<main>
  <div class="label">Governed-learning runtime</div>
  <h1>JoyLab Agent OS</h1>
  <div class="sub">Evidence must verify. Gates decide. Certified skills never self-modify.</div>

  <section class="grid">
    <div class="card"><div class="label">Runtime</div><div class="value ok">HEALTHY</div></div>
    <div class="card"><div class="label">Version</div><div class="value">{current_version}</div></div>
    <div class="card"><div class="label">Capabilities</div><div class="value">{capability_count}</div></div>
    <div class="card"><div class="label">Certification Policy</div><div class="value">{policy["version"]}</div></div>
  </section>

  <section class="grid" style="margin-top:16px">
    <div class="card">
      <div class="label">Evidence Pipeline</div>
      <div class="pipeline">
        Experience Log → EvidenceBuilder → Evidence Snapshot → CertificationEvidence → Certification Gate
      </div>
    </div>
    <div class="card">
      <div class="label">Certification Gate</div>
      <div class="pipeline">
        Samples ≥ <strong>{policy["min_samples"]}</strong><br>
        Gold Cases ≥ <strong>{policy["min_gold_cases"]}</strong><br>
        Confidence ≥ <strong>{policy["min_confidence"]}</strong><br>
        OOS + Regression required<br>
        Hard-gate violations ≤ <strong>{policy["max_hard_gate_violations"]}</strong>
      </div>
    </div>
  </section>

  <section class="card" style="margin-top:16px">
    <div class="label">Runtime API</div>
    <div class="pipeline">
      <a href="/api/health"><code>/api/health</code></a> ·
      <a href="/api/version"><code>/api/version</code></a> ·
      <a href="/api/capabilities"><code>/api/capabilities</code></a> ·
      <a href="/api/certification-policy"><code>/api/certification-policy</code></a> ·
      <a href="/docs"><code>/docs</code></a>
    </div>
  </section>
</main>
</body>
</html>"""
