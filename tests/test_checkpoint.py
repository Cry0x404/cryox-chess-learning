from cryox_chess.checkpoint import migrate_legacy


def test_legacy_counters_are_preserved():
    legacy = {
        "weights": {
            "material": 1.0,
            "mobility": 0.1,
            "center": 0.1,
            "king_safety": 0.1,
            "pawn_push": 0.1,
            "bishop_pair": 0.1,
            "rook_activity": 0.1,
            "queen_early": -0.1,
        },
        "best_weights": {
            "material": 1.05,
            "mobility": 0.1,
            "center": 0.1,
            "king_safety": 0.1,
            "pawn_push": 0.1,
            "bishop_pair": 0.1,
            "rook_activity": 0.1,
            "queen_early": -0.1,
        },
        "games": 1808,
        "generation": 47,
        "accepted": 46,
        "rejected": 89,
    }
    checkpoint = migrate_legacy(legacy)
    assert checkpoint.games == 1808
    assert checkpoint.generation == 47
    assert checkpoint.accepted == 46
    assert checkpoint.rejected == 89
