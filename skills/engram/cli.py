#!/usr/bin/env python3
"""Engram CLI — a hippocampus for AI agents."""

import argparse
import json
import sys
from datetime import date
from pathlib import Path

from . import __version__
from .config import load_config
from .recall import recall, list_entities


def cmd_extract(args):
    """Extract entities from daily log files."""
    from .core import process_date
    cfg = load_config(args.config)
    
    if args.all:
        import glob
        files = sorted(cfg.memory_dir.glob("2*-*-*.md"))
        import re
        for f in files:
            if re.match(r'^\d{4}-\d{2}-\d{2}$', f.stem):
                process_date(f.stem)
    elif args.date:
        process_date(args.date)
    else:
        process_date(date.today().isoformat())


def cmd_surprise(args):
    """Run surprise scoring with two-stage prediction error."""
    cfg = load_config(args.config)
    date_str = args.date or date.today().isoformat()
    
    if args.legacy:
        # Use simple single-prompt scoring
        from .core import run_surprise
        run_surprise(date_str)
    else:
        # Use two-stage prediction error engine
        from .prediction_error import PredictionErrorEngine
        from .providers import get_provider
        
        llm = get_provider(cfg.extraction.provider, model=cfg.extraction.model)
        engine = PredictionErrorEngine(llm, cfg.memory_dir, cfg.long_term_memory)
        result = engine.compute_sync(date_str)
        
        print(f"\n🧠 Prediction Error Report — {date_str}")
        print(f"   Mean PE: {result.mean_surprise:.2f}")
        print(f"   Predictions made: {len(result.predictions)}")
        print(f"   Events scored: {len(result.errors)}")
        
        if result.high_surprise:
            print(f"\n🔴 High surprise ({len(result.high_surprise)}):")
            for e in result.high_surprise:
                print(f"   [{e.prediction_error:.2f}] {e.event}")
                print(f"         → {e.reason}")
        
        if result.medium_surprise:
            print(f"\n🟡 Medium surprise ({len(result.medium_surprise)}):")
            for e in result.medium_surprise:
                print(f"   [{e.prediction_error:.2f}] {e.event}")
        
        if result.model_updates:
            print(f"\n📝 Suggested world model updates:")
            for u in result.model_updates:
                print(f"   - {u}")


def cmd_consolidate(args):
    """Run full sleep cycle: PE scoring → MEMORY.md update."""
    cfg = load_config(args.config)
    date_str = args.date or date.today().isoformat()
    
    if args.legacy:
        from .core import run_consolidate
        run_consolidate()
    else:
        from .consolidator import Consolidator
        from .providers import get_provider
        
        llm = get_provider(cfg.extraction.provider, model=cfg.extraction.model)
        consolidator = Consolidator(llm, cfg.memory_dir, cfg.long_term_memory)
        result = consolidator.run_sync(date_str)
        print(result)


def cmd_recall(args):
    """Query the knowledge graph."""
    cfg = load_config(args.config)
    result = recall(args.query, cfg, hops=args.hops)
    print(result)


def cmd_entities(args):
    """List all known entities."""
    cfg = load_config(args.config)
    entities = list_entities(cfg)
    
    if args.json:
        print(json.dumps(entities, indent=2))
    else:
        # Group by type
        by_type: dict[str, list] = {}
        for e in entities:
            by_type.setdefault(e["type"], []).append(e)
        
        for entity_type, items in sorted(by_type.items()):
            print(f"\n{entity_type.upper()} ({len(items)})")
            for item in items:
                entries = item["timeline_entries"]
                print(f"  {item['name']} ({entries} entries)")


def cmd_decay(args):
    """Archive stale entities, show what's going cold."""
    cfg = load_config(args.config)
    from .decay import DecayConfig, scan_stale, archive_entity
    
    dc = DecayConfig(archive_after_days=args.days)
    stale = scan_stale(cfg.entities_dir, dc)
    
    if not stale:
        print("🟢 No stale entities. Knowledge graph is fresh.")
        return
    
    print(f"🔍 Found {len(stale)} stale entities (>{args.days} days inactive):")
    for entity in stale:
        print(f"  ⚠️  {entity['name']} — last referenced {entity.get('days_inactive', '?')} days ago")
    
    if args.dry_run:
        print(f"\nDry run — would archive {len(stale)} entities to memory/entities/archive/")
    else:
        archived = 0
        for entity in stale:
            if archive_entity(cfg.entities_dir, entity['name']):
                archived += 1
        print(f"\n📦 Archived {archived} entities to memory/entities/archive/")


def cmd_merge(args):
    """Merge duplicate entities or detect potential duplicates."""
    cfg = load_config(args.config)
    from .aliases import merge_entities, detect_duplicates
    
    if args.detect:
        dupes = detect_duplicates(cfg.entities_dir)
        if dupes:
            print("🔍 Potential duplicates:")
            for a, b, conf in dupes:
                print(f"  [{conf:.0%}] {a} ↔ {b}")
            print(f"\nMerge with: engram merge \"source\" \"target\"")
        else:
            print("No duplicates detected.")
    elif args.source and args.target:
        merge_entities(cfg.entities_dir, args.source, args.target)
    else:
        print("Usage: engram merge \"source\" \"target\"")
        print("       engram merge --detect")


def cmd_viz(args):
    """Visualize the knowledge graph as Mermaid."""
    cfg = load_config(args.config)
    
    if not cfg.graph_file.exists():
        print("No graph data yet. Run 'engram extract' first.")
        return
    
    seen = set()
    print("graph LR")
    for line in cfg.graph_file.read_text().strip().split("\n"):
        if not line:
            continue
        try:
            t = json.loads(line)
            s = t["subject"].replace(" ", "_").replace("#", "Nr").replace(".", "")
            o = t["object"].replace(" ", "_").replace("#", "Nr").replace(".", "")
            p = t["predicate"]
            key = f"{s}-{p}-{o}"
            if key not in seen:
                seen.add(key)
                print(f"    {s} -->|{p}| {o}")
        except:
            continue


def cmd_stats(args):
    """Show engram statistics."""
    cfg = load_config(args.config)
    
    entities = list_entities(cfg)
    
    # Count triplets
    triplet_count = 0
    if cfg.graph_file.exists():
        triplet_count = sum(1 for line in cfg.graph_file.read_text().strip().split("\n") if line)
    
    # Count surprises
    surprise_count = 0
    if cfg.surprise_file.exists():
        surprise_count = sum(1 for line in cfg.surprise_file.read_text().strip().split("\n") if line)
    
    # Count daily files
    import re
    daily_count = sum(1 for f in cfg.memory_dir.glob("*.md") 
                      if re.match(r'^\d{4}-\d{2}-\d{2}$', f.stem))
    
    print(f"🧠 Engram Stats")
    print(f"  Entities:      {len(entities)}")
    print(f"  Triplets:      {triplet_count}")
    print(f"  Surprises:     {surprise_count}")
    print(f"  Daily files:   {daily_count}")
    print(f"  Workspace:     {cfg.workspace}")
    
    if entities:
        types = {}
        for e in entities:
            types[e["type"]] = types.get(e["type"], 0) + 1
        print(f"\n  Entity types:")
        for t, c in sorted(types.items(), key=lambda x: -x[1]):
            print(f"    {t}: {c}")


def main():
    parser = argparse.ArgumentParser(
        prog="engram",
        description="🧠 Engram — A hippocampus for AI agents",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    parser.add_argument("--config", "-c", help="Path to engram.yaml config file")
    
    sub = parser.add_subparsers(dest="command", help="Available commands")
    
    # extract
    p_extract = sub.add_parser("extract", help="Extract entities from daily logs")
    p_extract.add_argument("--date", "-d", help="Specific date (YYYY-MM-DD)")
    p_extract.add_argument("--all", action="store_true", help="Process all daily files")
    p_extract.set_defaults(func=cmd_extract)
    
    # surprise
    p_surprise = sub.add_parser("surprise", help="Run two-stage prediction error scoring")
    p_surprise.add_argument("--date", "-d", help="Date to score (default: today)")
    p_surprise.add_argument("--legacy", action="store_true", help="Use simple single-prompt scoring")
    p_surprise.set_defaults(func=cmd_surprise)
    
    # consolidate
    p_consolidate = sub.add_parser("consolidate", help="Run sleep cycle: PE → MEMORY.md")
    p_consolidate.add_argument("--date", "-d", help="Date to consolidate (default: today)")
    p_consolidate.add_argument("--legacy", action="store_true", help="Use simple consolidation")
    p_consolidate.set_defaults(func=cmd_consolidate)
    
    # recall
    p_recall = sub.add_parser("recall", help="Query the knowledge graph")
    p_recall.add_argument("query", help="What to look up")
    p_recall.add_argument("--hops", type=int, default=1, help="Graph traversal depth")
    p_recall.set_defaults(func=cmd_recall)
    
    # entities
    p_entities = sub.add_parser("entities", help="List all known entities")
    p_entities.add_argument("--json", action="store_true", help="Output as JSON")
    p_entities.set_defaults(func=cmd_entities)
    
    # decay
    p_decay = sub.add_parser("decay", help="Archive stale entities, reinforce active ones")
    p_decay.add_argument("--dry-run", action="store_true", help="Show what would be archived")
    p_decay.add_argument("--days", type=int, default=30, help="Archive after N days inactive")
    p_decay.set_defaults(func=cmd_decay)
    
    # merge
    p_merge = sub.add_parser("merge", help="Merge duplicate entities")
    p_merge.add_argument("source", nargs="?", help="Source entity to merge FROM")
    p_merge.add_argument("target", nargs="?", help="Target entity to merge INTO")
    p_merge.add_argument("--detect", action="store_true", help="Auto-detect potential duplicates")
    p_merge.set_defaults(func=cmd_merge)
    
    # viz
    p_viz = sub.add_parser("viz", help="Visualize knowledge graph (Mermaid)")
    p_viz.set_defaults(func=cmd_viz)
    
    # stats
    p_stats = sub.add_parser("stats", help="Show engram statistics")
    p_stats.set_defaults(func=cmd_stats)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    args.func(args)


if __name__ == "__main__":
    main()
