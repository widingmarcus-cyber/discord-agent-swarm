---
name: polymarket
description: Search prediction markets, get live odds, and compare sports lines on Polymarket.
homepage: https://polymarket.com
metadata: {"clawdbot":{"emoji":"📊","requires":{"bins":["curl","python3"]}}}
---

# Polymarket 📊

Search prediction markets, get live odds, and cross-reference sports betting lines. No API key required.

## Tools

### Market Search

Find active markets by keyword:

```bash
curl -s "https://gamma-api.polymarket.com/events?active=true&closed=false&limit=10&order=volume24hr" | python3 -c "
import sys, json
for e in json.load(sys.stdin):
    title = e.get('title','')
    vol = e.get('volume24hr', 0)
    liq = e.get('liquidity', 0)
    end = e.get('endDate','')[:10]
    print(f'{title}')
    print(f'  Vol24h: \${vol:,.0f} | Liquidity: \${liq:,.0f} | Ends: {end}')
    for m in e.get('markets', [])[:3]:
        q = m.get('question','')
        last = m.get('lastTradePrice', 0)
        bid = m.get('bestBid', 0)
        ask = m.get('bestAsk', 0)
        print(f'  → {q[:70]} | Last: {last} | Bid/Ask: {bid}/{ask}')
    print()
"
```

Filter by topic — add `&tag=` parameter:
- Sports: `&tag=NBA`, `&tag=NFL`, `&tag=NHL`
- Politics: `&tag=Politics`
- Crypto: `&tag=Crypto`

### Get Odds for Specific Market

```bash
# Get market by condition ID or slug
curl -s "https://gamma-api.polymarket.com/markets?slug=will-trump-win-2028" | python3 -c "
import sys, json
for m in json.load(sys.stdin):
    print(f\"Question: {m.get('question','')}\")
    print(f\"Last: {m.get('lastTradePrice',0)} | Bid: {m.get('bestBid',0)} | Ask: {m.get('bestAsk',0)}\")
    print(f\"Volume: \${m.get('volume',0):,.0f} | Liquidity: \${m.get('liquidity',0):,.0f}\")
"
```

### Sports Line Comparison (ESPN vs Polymarket)

Cross-reference Vegas spreads with Polymarket odds to find mispricings:

```bash
# NBA games today with spreads
curl -s "https://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard" | python3 -c "
import sys, json
d = json.load(sys.stdin)
for ev in d.get('events', []):
    comps = ev.get('competitions',[{}])[0]
    teams = comps.get('competitors',[])
    odds = comps.get('odds',[{}])
    home = away = None
    for t in teams:
        info = {'name': t['team']['displayName'], 'record': t.get('records',[{}])[0].get('summary',''), 'home': t['homeAway']=='home'}
        if info['home']: home = info
        else: away = info
    spread = odds[0].get('details','') if odds else ''
    ou = odds[0].get('overUnder','') if odds else ''
    if home and away:
        print(f\"{away['name']} ({away['record']}) @ {home['name']} ({home['record']})\")
        print(f'  Spread: {spread} | O/U: {ou}')
        print()
"
```

**Other sports:**
- NFL: `.../football/nfl/scoreboard`
- NHL: `.../hockey/nhl/scoreboard`
- MLB: `.../baseball/mlb/scoreboard`

### EV Calculator

When you have both Vegas implied probability and Polymarket price, calculate expected value:

```
Vegas implied prob = 0.65 (team -190 favorite)
Polymarket price  = 0.58 (buy YES at 58c)
EV = (0.65 × $0.42) - (0.35 × $0.58) = $0.07 per share (positive = good bet)
```

Only bet when EV > $0.05 (covers fees + slippage).

## Key Concepts

- **Polymarket odds** = market price (0.00-1.00). Price of YES share = implied probability.
- **Spread** = point handicap from Vegas. Negative = favored team.
- **Mispricing** = when Polymarket odds diverge significantly from Vegas/ESPN data.
- **Gamma API** = free, no auth required. Rate limited but generous.
- **ESPN API** = free, no auth required. Real-time scores and spreads.

## Limitations

- Gamma API `tag` filter is unreliable — use keyword search in results instead
- ESPN API only shows current day's games on scoreboard endpoint
- Polymarket requires wallet connection to actually trade (not covered by this skill)
- Sports markets are time-sensitive — odds change rapidly near game time
