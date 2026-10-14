import matplotlib.pyplot as plt
import matplotlib.dates as mdates


def plot_elo_history(engine, save_path="elo_history.png"): #line chart of every team's elo over the season
    by_team = {}
    for snap in engine.history:
        if snap.date is None:
            continue
        by_team.setdefault(snap.team, {"dates": [], "ratings": []})
        by_team[snap.team]["dates"].append(snap.date)
        by_team[snap.team]["ratings"].append(snap.rating)

    fig, ax = plt.subplots(figsize=(9, 5.5))
    for team, series in sorted(by_team.items(), key=lambda kv: kv[1]["ratings"][-1], reverse=True):
        ax.plot(series["dates"], series["ratings"], marker="o", markersize=3, label=team, linewidth=2)

    ax.axhline(1500, color="gray", linestyle="--", linewidth=1, alpha=0.5) #starting rating line
    ax.set_title("Elo Rating by Team — Regular Season", fontsize=13, fontweight="bold")
    ax.set_ylabel("Elo Rating")
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %d"))
    ax.legend(loc="upper left", fontsize=8, ncol=2, frameon=False)
    fig.autofmt_xdate()
    fig.tight_layout()
    fig.savefig(save_path, dpi=150)
    plt.close(fig)
    return save_path


def plot_championship_probs(probs, save_path="championship_odds.png"): #bar chart of each team's championship odds
    items = sorted(probs.items(), key=lambda kv: kv[1])
    teams = [t for t, _ in items]
    values = [p * 100 for _, p in items]

    fig, ax = plt.subplots(figsize=(8, 4.5))
    colors = ["#1F4E79" if v == max(values) else "#8FAADC" for v in values]
    bars = ax.barh(teams, values, color=colors)
    for bar, v in zip(bars, values):
        ax.text(v + 0.5, bar.get_y() + bar.get_height() / 2, f"{v:.1f}%", va="center", fontsize=9)

    ax.set_title("Championship Probability — 20,000 Simulated Playoffs", fontsize=13, fontweight="bold")
    ax.set_xlabel("Probability (%)")
    fig.tight_layout()
    fig.savefig(save_path, dpi=150)
    plt.close(fig)
    return save_path


def plot_player_trend(league, player, save_path=None, recent_window=3): #bar chart of one player's eff per game, last 3 games highlighted
    games = league.player_games_for(player)
    if not games:
        raise ValueError(f"No recorded games for '{player}'")

    effs = [g.eff for g in games]
    labels = [g.date.strftime("%m/%d") for g in games]
    season_avg = sum(effs) / len(effs)

    colors = ["#1F4E79" if i >= len(effs) - recent_window else "#B7C6DC" for i in range(len(effs))]

    fig, ax = plt.subplots(figsize=(7.5, 4.5))
    ax.bar(labels, effs, color=colors)
    ax.axhline(season_avg, color="#E0362E", linestyle="--", linewidth=1.5,
               label=f"Season avg ({season_avg:.1f})")
    ax.set_title(f"{player} — EFF per Game", fontsize=13, fontweight="bold")
    ax.set_ylabel("EFF (PTS+REB+AST+STL+BLK)")
    ax.legend(loc="upper left", fontsize=9, frameon=False)
    fig.tight_layout()

    save_path = save_path or f"player_{player.replace(' ', '_')}.png"
    fig.savefig(save_path, dpi=150)
    plt.close(fig)
    return save_path
