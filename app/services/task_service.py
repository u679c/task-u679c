import json
import subprocess
from typing import List

from app.models import TaskItem


TASK_RC_OVERRIDES = [
    "rc.uda.xstatus.type=string",
    "rc.uda.xstatus.label=状态",
    "rc.uda.link.type=string",
    "rc.uda.link.label=链接",
    "rc.uda.xdesc.type=string",
    "rc.uda.xdesc.label=描述",
]


class TaskService:
    def _run_task(self, args):
        cmd = ["task"] + TASK_RC_OVERRIDES + args
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(result.stderr.strip() or "Taskwarrior command failed")
        return result.stdout

    def fetch_tasks(self, filter_name: str) -> List[TaskItem]:
        filter_args = ["status.not:deleted"]
        if filter_name == "pending":
            filter_args = ["status:pending"]
        elif filter_name == "completed":
            filter_args = ["status:completed"]

        output = self._run_task(filter_args + ["export"])
        raw_tasks = json.loads(output) if output.strip() else []
        tasks: List[TaskItem] = []
        for item in raw_tasks:
            tasks.append(
                TaskItem(
                    task_id=item.get("id"),
                    uuid=item.get("uuid", ""),
                    description=item.get("description", ""),
                    note=item.get("xdesc", ""),
                    task_state=item.get("status", ""),
                    xstatus=item.get("xstatus", ""),
                    link=item.get("link", ""),
                    priority=item.get("priority", ""),
                    project=item.get("project", ""),
                    due=item.get("due", ""),
                    end=item.get("end", ""),
                )
            )
        return tasks

    def add_task(self, description: str, priority: str = "L") -> None:
        self._run_task(["add", description, f"priority:{priority}"])

    def update_task(
        self,
        task_ref: str,
        description: str,
        note: str,
        xstatus: str,
        link: str,
        priority: str,
        due: str,
    ) -> None:
        mods = [f"description:{description}"]
        if note:
            mods.append(f"xdesc:{note}")
        else:
            mods.append("xdesc:")
        if xstatus:
            mods.append(f"xstatus:{xstatus}")
        else:
            mods.append("xstatus:")
        if link:
            mods.append(f"link:{link}")
        else:
            mods.append("link:")
        if not priority:
            priority = "L"
        mods.append(f"priority:{priority}")
        if due:
            mods.append(f"due:{_build_due_value(due)}")
        else:
            mods.append("due:")

        self._run_task([str(task_ref), "modify"] + mods)

    def complete_task(self, task_ref: str) -> None:
        self._run_task([str(task_ref), "done"])

    def reopen_task(self, task_ref: str) -> None:
        self._run_task([str(task_ref), "modify", "status:pending"])

    def delete_task(self, task_ref: str) -> None:
        self._run_task(["rc.confirmation=off", str(task_ref), "delete"])


def _build_due_value(due_date: str) -> str:
    if len(due_date) == 10 and due_date[4] == "-" and due_date[7] == "-":
        return f"{due_date}T12:00:00"
    return due_date
