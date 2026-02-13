# 📊 Polymarket Skill for OpenClaw

Search prediction markets, get live odds, and find mispricings between Vegas lines and Polymarket.

## Features

- **Market Search** — Find active prediction markets by keyword or tag (politics, sports, crypto)
- **Live Odds** — Get bid/ask/last prices for any market
- **Sports Comparison** — Cross-reference ESPN spreads with Polymarket odds to spot edge
- **EV Calculator** — Calculate expected value when you find a mispricing

## Install

```bash
# OpenClaw
clawdhub install polymarket

# Manual
cp -r polymarket/ ~/.config/clawdbot/skills/
```

## Requirements

- `curl` and `python3` (no additional packages)
- No API keys needed — uses free Gamma API and ESPN API

## APIs Used

| API | Auth | Rate Limit | Data |
|-----|------|-----------|------|
| [Gamma API](https://gamma-api.polymarket.com) | None | Generous | Markets, odds, volume |
| [ESPN API](https://site.api.espn.com) | None | Generous | Scores, spreads, records |

## Usage Examples

Ask your agent:
- "What are the hottest prediction markets right now?"
- "Show me NBA games today with spreads"
- "Find mispricings between Vegas and Polymarket for tonight's games"
- "What are the odds on the next US election?"

## License

MIT
