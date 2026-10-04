from conflicts import find_conflicts


def make(name, actives):
    return {"name": name, "actives": actives}


def test_retinol_and_glycolic_conflict():
    routine = [make("Retinol Serum", ["retinoid"]), make("Glow Toner", ["aha"])]
    conflicts = find_conflicts(routine)
    assert len(conflicts) == 1
    assert conflicts[0]["actives"] == ["aha", "retinoid"]


def test_niacinamide_and_vitamin_c_are_fine():
    # A common myth: these are safe to use together.
    routine = [make("C Serum", ["vitamin_c"]), make("Niacinamide", ["niacinamide"])]
    assert find_conflicts(routine) == []


def test_no_actives_no_conflicts():
    routine = [make("Cleanser", []), make("Moisturizer", [])]
    assert find_conflicts(routine) == []


def test_order_does_not_matter():
    a, b = make("BP Wash", ["benzoyl_peroxide"]), make("Retinol", ["retinoid"])
    assert len(find_conflicts([a, b])) == len(find_conflicts([b, a])) == 1

def test_same_exfoliant_twice_is_flagged():
    routine = [make("BHA Serum", ["bha"]), make("BHA Cream", ["bha", "niacinamide"])]
    conflicts = find_conflicts(routine)
    assert len(conflicts) == 1
    assert conflicts[0]["actives"] == ["bha"]


def test_niacinamide_twice_is_fine():
    routine = [make("A", ["niacinamide"]), make("B", ["niacinamide"])]
    assert find_conflicts(routine) == []
