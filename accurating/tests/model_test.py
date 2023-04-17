import accurating
import json

import jax.numpy as jnp
import numpy as np
from numpy.testing import assert_array_equal


def get_test_data(true_elos) -> accurating.MatchResultArrays:
    p1s = []
    p2s = []
    p1_win_probs = []
    seasons = []
    player_count, season_count = true_elos.shape
    for p1 in range(player_count):
        for p2 in range(player_count):
            for season in range(season_count):
                p1s.append(p1)
                p2s.append(p2)
                p1_win_prob = accurating.win_prob(
                    true_elos[p1][season], true_elos[p2][season])
                p1_win_probs.append(p1_win_prob)
                seasons.append(season)

    return accurating.MatchResultArrays(
        p1=jnp.array(p1s),
        p2=jnp.array(p2s),
        p1_win_prob=jnp.array(p1_win_probs),
        season=jnp.array(seasons),
        player_name=None,
    )


def test_fit():
    true_elos = jnp.array([[8.0, 4.0], [2.0, 3.0], [0.0, 0.0],])
    test_data = get_test_data(true_elos)
    config = accurating.Config(
        season_rating_stability=0.0,
        smoothing=0.0,
        max_steps=300,
        do_log=True,
    )
    model = accurating.fit(test_data, config)
    elos = model.rating
    elos = elos - jnp.min(elos, axis=0, keepdims=True)
    err = jnp.linalg.norm(elos - jnp.array(true_elos))
    assert err < 0.000001, f'FAIL err={err}; results={model}'


def test_data_from_dicts():
    json_str = """
    [
      {
        "p1": "Leon",
        "p2": "Caesar",
        "winner": "Leon",
        "season": 0
      },
      {
        "p1": "Caesar",
        "p2": "Alusia",
        "winner": "Caesar",
        "season": 1
      },
      {
        "p1": "Leon",
        "p2": "Alusia",
        "winner": "Alusia",
        "season": 1
      }
    ]
    """
    matches = json.loads(json_str)
    data = accurating.data_from_dicts(matches)

    player_name = ['Alusia', 'Caesar', 'Leon']
    p1 = np.array([2, 1, 2])
    p2 = np.array([1, 0, 0])
    p1_win_prob = np.array([1., 1., 0])
    season = np.array([0, 1, 1])

    assert data.player_name == player_name
    assert_array_equal(data.p1, p1)
    assert_array_equal(data.p2, p2)
    assert_array_equal(data.p1_win_prob, p1_win_prob)
    assert_array_equal(data.season, season)

    cfg = accurating.Config(season_rating_stability=0.5,
                            smoothing=0.1, max_steps=5, do_log=True, initial_lr=1.0,)
    model = accurating.fit(data, cfg)
    del model
