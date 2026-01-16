from dataclasses import dataclass


@dataclass
class TaskItem:
    task_id: int | None
    uuid: str
    description: str
    xtype: str
    note: str
    task_state: str
    xstatus: str
    link: str
    priority: str
    project: str
    due: str
    end: str
