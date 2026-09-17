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
        "games": 120,
        "generation": 8,
        "accepted": 5,
        "rejected": 3,
    }
    checkpoint = migrate_legacy(legacy)
    assert checkpoint.games == 120
    assert checkpoint.generation == 8
    assert checkpoint.accepted == 5
    assert checkpoint.rejected == 3
