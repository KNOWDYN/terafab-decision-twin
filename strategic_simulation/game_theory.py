from __future__ import annotations

import itertools
from typing import Any, Dict, Iterable, List, Mapping, Sequence, Tuple


def _profile_key(profile: Mapping[str, str], actors: Sequence[str]) -> str:
    return "|".join(f"{actor}={profile[actor]}" for actor in actors)


def _profiles(actors: Sequence[str], strategies: Mapping[str, Sequence[str]]) -> Iterable[Dict[str, str]]:
    strategy_lists = [list(strategies[a]) for a in actors]
    for combo in itertools.product(*strategy_lists):
        yield dict(zip(actors, combo))


def _payoff_lookup(config: Mapping[str, Any], actors: Sequence[str]) -> Dict[str, Dict[str, float]]:
    lookup: Dict[str, Dict[str, float]] = {}
    raw = config.get("payoffs", [])
    if isinstance(raw, Mapping):
        for key, payoff in raw.items():
            lookup[str(key)] = {actor: float(payoff.get(actor, 0.0)) for actor in actors}
        return lookup
    for row in raw:
        profile = row.get("profile", {})
        payoff = row.get("payoff", {})
        lookup[_profile_key(profile, actors)] = {actor: float(payoff.get(actor, 0.0)) for actor in actors}
    return lookup


def _best_responses(actors: Sequence[str], strategies: Mapping[str, Sequence[str]], payoffs: Mapping[str, Mapping[str, float]]) -> Dict[str, List[Dict[str, Any]]]:
    responses: Dict[str, List[Dict[str, Any]]] = {actor: [] for actor in actors}
    all_profiles = list(_profiles(actors, strategies))
    for actor in actors:
        others = [a for a in actors if a != actor]
        contexts: Dict[Tuple[str, ...], List[Dict[str, str]]] = {}
        for profile in all_profiles:
            key = tuple(profile[o] for o in others)
            contexts.setdefault(key, []).append(profile)
        for context_key, candidates in contexts.items():
            scored = []
            for profile in candidates:
                key = _profile_key(profile, actors)
                scored.append((payoffs.get(key, {}).get(actor, 0.0), profile[actor], profile))
            best_value = max(score[0] for score in scored)
            best_strategies = sorted({strategy for value, strategy, _ in scored if value == best_value})
            responses[actor].append({
                "given": dict(zip(others, context_key)),
                "best_strategies": best_strategies,
                "payoff": best_value,
            })
    return responses


def _is_nash(profile: Mapping[str, str], actors: Sequence[str], strategies: Mapping[str, Sequence[str]], payoffs: Mapping[str, Mapping[str, float]]) -> bool:
    key = _profile_key(profile, actors)
    for actor in actors:
        current_payoff = payoffs.get(key, {}).get(actor, 0.0)
        for alternative in strategies[actor]:
            if alternative == profile[actor]:
                continue
            alt_profile = dict(profile)
            alt_profile[actor] = alternative
            alt_key = _profile_key(alt_profile, actors)
            if payoffs.get(alt_key, {}).get(actor, 0.0) > current_payoff:
                return False
    return True


def _conflict_index(payoffs_by_profile: Mapping[str, Mapping[str, float]], actors: Sequence[str]) -> float:
    if not payoffs_by_profile or len(actors) < 2:
        return 0.0
    profile_conflicts: List[float] = []
    all_values = [float(v) for payoff in payoffs_by_profile.values() for v in payoff.values()]
    denom = max(all_values) - min(all_values) if all_values else 0.0
    if denom == 0:
        return 0.0
    for payoff in payoffs_by_profile.values():
        vals = [float(payoff.get(actor, 0.0)) for actor in actors]
        profile_conflicts.append((max(vals) - min(vals)) / denom)
    return sum(profile_conflicts) / len(profile_conflicts)


def analyze_normal_form_game(config: Mapping[str, Any]) -> Dict[str, Any]:
    """Analyze a finite normal-form game with declared payoffs.

    This function intentionally does not infer stakeholder preferences. It
    evaluates strategies and payoffs supplied by the user or examples.
    """
    actors = list(config.get("actors", []))
    if len(actors) < 2:
        raise ValueError("Game analysis requires at least two actors")
    strategies = {actor: list(config.get("strategies", {}).get(actor, [])) for actor in actors}
    missing = [actor for actor, vals in strategies.items() if not vals]
    if missing:
        raise ValueError(f"Missing strategies for actors: {missing}")
    payoffs = _payoff_lookup(config, actors)
    all_profiles = list(_profiles(actors, strategies))
    missing_payoffs = [_profile_key(profile, actors) for profile in all_profiles if _profile_key(profile, actors) not in payoffs]
    if missing_payoffs:
        raise ValueError(f"Missing payoff rows for profiles: {missing_payoffs[:5]}" + (" ..." if len(missing_payoffs) > 5 else ""))
    nash = []
    for profile in all_profiles:
        if _is_nash(profile, actors, strategies, payoffs):
            key = _profile_key(profile, actors)
            nash.append({"profile": profile, "payoff": dict(payoffs[key])})
    total_payoff_ranking = []
    for profile in all_profiles:
        key = _profile_key(profile, actors)
        total_payoff_ranking.append({"profile": profile, "total_payoff": sum(payoffs[key].values()), "payoff": dict(payoffs[key])})
    total_payoff_ranking.sort(key=lambda row: row["total_payoff"], reverse=True)
    conflict = _conflict_index(payoffs, actors)
    return {
        "kind": "normal_form_game_result",
        "model_boundary": "Declared stakeholder-game assumptions; not observed stakeholder preference data.",
        "actors": actors,
        "strategies": strategies,
        "profile_count": len(all_profiles),
        "pure_strategy_nash_equilibria": nash,
        "best_responses": _best_responses(actors, strategies, payoffs),
        "conflict_index": conflict,
        "coordination_failure_warning": bool(nash and total_payoff_ranking and sum(nash[0]["payoff"].values()) < total_payoff_ranking[0]["total_payoff"]),
        "total_payoff_ranking": total_payoff_ranking[:10],
    }
