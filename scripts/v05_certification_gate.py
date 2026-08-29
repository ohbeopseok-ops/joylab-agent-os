from __future__ import annotations

import argparse
import json
import sys

from joylab_agent_os.v05_certification_gate import (
    V05CertificationGate,
    V05CertificationInputs,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ci-green", action="store_true")
    parser.add_argument("--regression-green", action="store_true")
    parser.add_argument("--required-certified-gold", type=int, default=64)
    args = parser.parse_args()

    inputs = V05CertificationInputs(
        python_ci_green=args.ci_green,
        regression_green=args.regression_green,
        gold_registry_path="gold_registry/GOLD_CASE_REGISTRY_V0.5.2.json",
        schema_paths=(
            "schemas/evidence_snapshot.schema.json",
            "schemas/evidence_graph_snapshot.schema.json",
        ),
        required_certified_gold=args.required_certified_gold,
    )
    result = V05CertificationGate().evaluate(inputs)
    print(json.dumps(
        {
            "passed": result.passed,
            "checks": result.checks,
            "reasons": result.reasons,
        },
        indent=2,
        sort_keys=True,
    ))
    return 0 if result.passed else 1


if __name__ == "__main__":
    sys.exit(main())
