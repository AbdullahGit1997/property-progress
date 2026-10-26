"""A small, dependency-free property progress tracker. Python 3.10+."""
import argparse
import json
from datetime import date
from pathlib import Path


def load_case(path):
    case = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(case, dict) or not isinstance(case.get("property"), str):
        raise ValueError("Case must contain a property name.")
    tasks = case.get("tasks")
    if not isinstance(tasks, list) or not tasks:
        raise ValueError("Case must contain at least one task.")
    ids = set()
    for task in tasks:
        if not isinstance(task, dict):
            raise ValueError("Each task must be an object.")
        task_id = task.get("id")
        if not isinstance(task_id, str) or not task_id or task_id in ids:
            raise ValueError("Task IDs must be unique, non-empty strings.")
        ids.add(task_id)
        for field in ("title", "owner"):
            if not isinstance(task.get(field), str) or not task[field].strip():
                raise ValueError(f"Task {task_id} needs a {field}.")
        if task.get("status") not in ("pending", "complete"):
            raise ValueError(f"Invalid status for {task_id}.")
        date.fromisoformat(task["due"])
    return case


def report(case, today):
    tasks = case["tasks"]
    complete = sum(task["status"] == "complete" for task in tasks)
    pending = sorted((t for t in tasks if t["status"] == "pending"), key=lambda t: t["due"])
    lines = [f"Property: {case['property']}", f"As of: {today.isoformat()}",
             f"Progress: {complete}/{len(tasks)} milestones complete", ""]
    for task in pending:
        overdue = date.fromisoformat(task["due"]) < today
        label = "OVERDUE" if overdue else "PENDING"
        lines.append(f"[{label}] {task['id']}: {task['title']} | {task['owner']} | due {task['due']}")
    lines.append("")
    if pending:
        next_task = pending[0]
        lines.append(f"Next action: Follow up with {next_task['owner']} about {next_task['title'].lower()}.")
    else:
        lines.append("All tracked milestones are complete.")
    lines.append("Demo checklist only; milestone completion does not confirm legal readiness.")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("case", type=Path, help="Path to a case JSON file")
    parser.add_argument("--today", type=date.fromisoformat, default=date.today(), help="YYYY-MM-DD; defaults to today")
    parser.add_argument("--complete", metavar="TASK_ID", help="Mark one milestone complete and save")
    args = parser.parse_args()
    try:
        case = load_case(args.case)
        if args.complete:
            task = next((t for t in case["tasks"] if t["id"] == args.complete), None)
            if task is None:
                raise ValueError(f"Unknown task ID: {args.complete}")
            task["status"] = "complete"
            temporary = args.case.with_suffix(args.case.suffix + ".tmp")
            temporary.write_text(json.dumps(case, indent=2) + "\n", encoding="utf-8")
            temporary.replace(args.case)
        print(report(case, args.today))
    except (OSError, ValueError, KeyError, TypeError) as error:
        parser.exit(1, f"Error: {error}\n")


if __name__ == "__main__":
    main()
