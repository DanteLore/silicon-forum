from outputs import stats as stats_mod


def _bias_str(bias) -> str:
    if bias is None:
        return "—"
    sign = "+" if bias >= 0 else ""
    return f"{sign}{bias:.0%}"


class TerminalStats:
    """Accumulates per-run rows and prints a stats summary block on finalize()."""

    def __init__(self):
        self.rows: list[dict] = []

    def add_row(self, row: dict) -> None:
        self.rows.append(row)

    def finalize(self) -> None:
        s = stats_mod.compute(self.rows)
        sep = "=" * 60
        print(f"\n{sep}")
        print(f"  STATISTICS  ({s['total']} run{'s' if s['total'] != 1 else ''})")
        print()

        if s["completed"]:
            rate = f"  ({s['uphold_rate']:.0%})" if s["uphold_rate"] is not None else ""
            print(f"  Premise result: {s['upheld']} upheld / {s['rejected']} rejected{rate}")
            print()

        if s["agents"]:
            print("  DEBATER PERFORMANCE")
            print(f"  {'Name':<20} {'Side':<8} {'n':>3}  {'Wins':>4}  {'Win%':>5}  {'Avg score':>9}")
            for a in s["agents"]:
                win_pct = f"{a['win_rate']:.0%}" if a["win_rate"] is not None else "—"
                avg     = str(a["avg_score"])    if a["avg_score"] is not None else "—"
                print(f"  {a['name']:<20} {a['side']:<8} {a['n']:>3}  {a['wins']:>4}  {win_pct:>5}  {avg:>9}")
            print()

        if s["judges"]:
            print("  JUDGE PROFILE")
            print(f"  {'Name':<20} {'n':>3}  {'Upheld':>6}  {'Rejected':>8}  {'Uphold%':>7}  {'Bias':>6}")
            for j in s["judges"]:
                rate_str = f"{j['uphold_rate']:.0%}" if j["uphold_rate"] is not None else "—"
                print(f"  {j['name']:<20} {j['n']:>3}  {j['upheld']:>6}  {j['rejected']:>8}"
                      f"  {rate_str:>7}  {_bias_str(j['bias']):>6}")
            print()

        if s["model_debaters"]:
            print("  MODEL PERFORMANCE (as debater)")
            print(f"  {'Model':<30} {'n':>3}  {'Wins':>4}  {'Win%':>5}  {'Avg score':>9}")
            for m in s["model_debaters"]:
                win_pct = f"{m['win_rate']:.0%}" if m["win_rate"] is not None else "—"
                avg     = str(m["avg_score"])    if m["avg_score"] is not None else "—"
                print(f"  {m['name']:<30} {m['n']:>3}  {m['wins']:>4}  {win_pct:>5}  {avg:>9}")
            print()

        if s["model_judges"]:
            print("  MODEL PERFORMANCE (as judge)")
            print(f"  {'Model':<30} {'n':>3}  {'Upheld':>6}  {'Rejected':>8}  {'Uphold%':>7}  {'Bias':>6}")
            for j in s["model_judges"]:
                rate_str = f"{j['uphold_rate']:.0%}" if j["uphold_rate"] is not None else "—"
                print(f"  {j['name']:<30} {j['n']:>3}  {j['upheld']:>6}  {j['rejected']:>8}"
                      f"  {rate_str:>7}  {_bias_str(j['bias']):>6}")
            print()

        if s["order"]:
            o = s["order"]
            print(f"  SPEAKING ORDER  (n={o['n']} runs with a winner)")
            print(f"  First speaker:   {o['first_wins']} wins  ({o['first_win_rate']:.0%})")
            print(f"  Second speaker:  {o['second_wins']} wins  ({o['second_win_rate']:.0%})")
            print()

        if s["sides"]["n"]:
            d = s["sides"]
            for_pct     = f"{d['for_win_rate']:.0%}"     if d["for_win_rate"]     is not None else "—"
            against_pct = f"{d['against_win_rate']:.0%}" if d["against_win_rate"] is not None else "—"
            print(f"  SIDE EFFECT  (n={d['n']} runs with a winner)")
            print(f"  FOR:     {d['for_wins']} wins  ({for_pct})")
            print(f"  AGAINST: {d['against_wins']} wins  ({against_pct})")
            print()

        print(sep)
