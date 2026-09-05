import modules.optimisation as optimisation


def _patch_candidate_generation(monkeypatch, candidates):
    iterator = iter(candidates)

    def fake_generate(*args, **kwargs):
        return next(iterator)

    def fake_ec(*args, **kwargs):
        return {"uls_status": "PASS ✅"}

    def fake_randint(a, b):
        return 1000

    monkeypatch.setattr(optimisation, "generate_spatial_model", fake_generate)
    monkeypatch.setattr(optimisation, "run_eurocode_analysis", fake_ec)
    monkeypatch.setattr(optimisation.random, "randint", fake_randint)


def test_valid_candidate_beats_cheaper_fallback(monkeypatch):
    valid = {"planning": {"status": "OK"}, "id": "valid"}
    fallback = {"planning": {"status": "FALLBACK"}, "id": "fallback"}
    _patch_candidate_generation(monkeypatch, [fallback] * 19 + [valid])

    def fake_boq(design, country):
        return (100.0 if design["id"] == "valid" else 50.0, 0.0, 1.0, {})

    monkeypatch.setattr(optimisation, "compute_boq", fake_boq)
    best, cost = optimisation.optimise_cost(
        "Residential", "Housing", "Uganda", "Clay", ["Bedroom"], min_gfa=500
    )

    assert best["id"] == "valid"
    assert cost == 100.0
    assert best["optimisation"]["status"] == "VALID"
    assert best["optimisation"]["confidence"] == "HIGH"
    assert best["optimisation"]["candidate_count"] == 20
    assert best["optimisation"]["valid_candidate_count"] == 1
    assert best["optimisation"]["fallback_candidate_count"] == 19


def test_fallback_is_explicit_when_no_valid_candidate_exists(monkeypatch):
    fallback = {"planning": {"status": "FALLBACK"}, "id": "fallback"}
    _patch_candidate_generation(monkeypatch, [fallback] * 20)
    monkeypatch.setattr(
        optimisation,
        "compute_boq",
        lambda design, country: (75.0, 0.0, 1.0, {}),
    )

    best, cost = optimisation.optimise_cost(
        "Industrial", "Factory", "Uganda", "Clay", ["Manufacturing"], min_gfa=500
    )

    assert best["id"] == "fallback"
    assert cost == 75.0
    assert best["optimisation"]["status"] == "FALLBACK"
    assert best["optimisation"]["confidence"] == "LOW"
    assert "No valid metric-planned candidate" in best["optimisation"]["reason"]
    assert best["optimisation"]["candidate_count"] == 20
    assert best["optimisation"]["valid_candidate_count"] == 0
    assert best["optimisation"]["fallback_candidate_count"] == 20


def test_returns_empty_result_when_no_structural_candidate_passes(monkeypatch):
    valid_shape = {"planning": {"status": "OK"}, "id": "candidate"}
    _patch_candidate_generation(monkeypatch, [valid_shape] * 20)
    monkeypatch.setattr(
        optimisation,
        "run_eurocode_analysis",
        lambda *args, **kwargs: {"uls_status": "FAIL ❌"},
    )

    best, cost = optimisation.optimise_cost(
        "Residential", "Housing", "Uganda", "Clay", ["Bedroom"], min_gfa=500
    )

    assert best is None
    assert cost == float("inf")
