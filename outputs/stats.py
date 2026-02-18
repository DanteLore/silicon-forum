def compute(rows: list[dict]) -> dict:
    """Compute aggregate statistics from a list of per-run row dicts."""
    completed = [r for r in rows if r.get("premise_upheld") is not None]
    upheld    = [r for r in completed if r["premise_upheld"]]
    rejected  = [r for r in completed if not r["premise_upheld"]]
    overall_uphold_rate = len(upheld) / len(completed) if completed else None

    # --- debater stats ---
    _agents: dict = {}
    for row in rows:
        for side_key, name_key in [("for", "agent_for"), ("against", "agent_against")]:
            name = row.get(name_key)
            if not name:
                continue
            if name not in _agents:
                _agents[name] = {"n": 0, "wins": 0, "score_sum": 0, "score_n": 0, "side": side_key}
            d = _agents[name]
            d["n"] += 1
            if row.get("winner") == name:
                d["wins"] += 1
            s = row.get("scores", {}).get(name)
            if s is not None:
                d["score_sum"] += s
                d["score_n"]   += 1
    agents = sorted([
        {
            "name": name,
            "n":         d["n"],
            "wins":      d["wins"],
            "win_rate":  d["wins"] / d["n"] if d["n"] else None,
            "avg_score": round(d["score_sum"] / d["score_n"], 1) if d["score_n"] else None,
            "side":      d["side"],
        }
        for name, d in _agents.items()
    ], key=lambda x: (x["win_rate"] or 0), reverse=True)

    # --- judge stats ---
    _judges: dict = {}
    for row in rows:
        judge = row.get("judge")
        if not judge:
            continue
        if judge not in _judges:
            _judges[judge] = {"n": 0, "upheld": 0, "rejected": 0}
        d = _judges[judge]
        d["n"] += 1
        if row.get("premise_upheld") is True:
            d["upheld"]   += 1
        elif row.get("premise_upheld") is False:
            d["rejected"] += 1
    judges = []
    for name, d in sorted(_judges.items(), key=lambda x: x[1]["n"], reverse=True):
        comp = d["upheld"] + d["rejected"]
        rate = d["upheld"] / comp if comp else None
        bias = (rate - overall_uphold_rate) if (rate is not None and overall_uphold_rate is not None) else None
        judges.append({
            "name":        name,
            "n":           d["n"],
            "upheld":      d["upheld"],
            "rejected":    d["rejected"],
            "completed":   comp,
            "uphold_rate": rate,
            "bias":        round(bias, 3) if bias is not None else None,
        })

    # --- speaking order ---
    order_rows = [r for r in rows if r.get("first_speaker") and r.get("winner")]
    order = None
    if order_rows:
        first_wins  = sum(1 for r in order_rows if r["winner"] == r["first_speaker"])
        second_wins = len(order_rows) - first_wins
        n = len(order_rows)
        order = {
            "n":               n,
            "first_wins":      first_wins,
            "first_win_rate":  first_wins  / n,
            "second_wins":     second_wins,
            "second_win_rate": second_wins / n,
        }

    # --- model debater stats ---
    _model_debaters: dict = {}
    for row in rows:
        for model_key, name_key in [("model_for", "agent_for"), ("model_against", "agent_against")]:
            model = row.get(model_key)
            name  = row.get(name_key)
            if not model:
                continue
            if model not in _model_debaters:
                _model_debaters[model] = {"n": 0, "wins": 0, "score_sum": 0, "score_n": 0}
            d = _model_debaters[model]
            d["n"] += 1
            if row.get("winner") == name:
                d["wins"] += 1
            s = row.get("scores", {}).get(name)
            if s is not None:
                d["score_sum"] += s
                d["score_n"]   += 1
    model_debaters = sorted([
        {
            "name":      model,
            "n":         d["n"],
            "wins":      d["wins"],
            "win_rate":  d["wins"] / d["n"] if d["n"] else None,
            "avg_score": round(d["score_sum"] / d["score_n"], 1) if d["score_n"] else None,
        }
        for model, d in _model_debaters.items()
    ], key=lambda x: (x["win_rate"] or 0), reverse=True)

    # --- model judge stats ---
    _model_judges: dict = {}
    for row in rows:
        model = row.get("model_judge")
        if not model:
            continue
        if model not in _model_judges:
            _model_judges[model] = {"n": 0, "upheld": 0, "rejected": 0}
        d = _model_judges[model]
        d["n"] += 1
        if row.get("premise_upheld") is True:
            d["upheld"]   += 1
        elif row.get("premise_upheld") is False:
            d["rejected"] += 1
    model_judges = []
    for name, d in sorted(_model_judges.items(), key=lambda x: x[1]["n"], reverse=True):
        comp = d["upheld"] + d["rejected"]
        rate = d["upheld"] / comp if comp else None
        bias = (rate - overall_uphold_rate) if (rate is not None and overall_uphold_rate is not None) else None
        model_judges.append({
            "name":        name,
            "n":           d["n"],
            "upheld":      d["upheld"],
            "rejected":    d["rejected"],
            "completed":   comp,
            "uphold_rate": rate,
            "bias":        round(bias, 3) if bias is not None else None,
        })

    # --- side effect ---
    side_rows    = [r for r in rows if r.get("winner")]
    for_wins     = sum(1 for r in side_rows if r.get("winner") == r.get("agent_for"))
    against_wins = sum(1 for r in side_rows if r.get("winner") == r.get("agent_against"))
    n = len(side_rows)
    sides = {
        "n":            n,
        "for_wins":     for_wins,
        "for_win_rate": for_wins     / n if n else None,
        "against_wins": against_wins,
        "against_win_rate": against_wins / n if n else None,
    }

    return {
        "total":          len(rows),
        "completed":      len(completed),
        "upheld":         len(upheld),
        "rejected":       len(rejected),
        "uphold_rate":    overall_uphold_rate,
        "agents":         agents,
        "judges":         judges,
        "model_debaters": model_debaters,
        "model_judges":   model_judges,
        "order":          order,
        "sides":          sides,
    }
