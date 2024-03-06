from typing import Mapping, Iterable, Any
import os
from tinydb import TinyDB, Query
from tinydb.database import Document

from .schema import Record

from thsr_helper.booking.constants import MODULE_DIR


class TinyDBManager:
    def __init__(self, db_path: str = None):
        if db_path is None:
            db_path = os.path.join(MODULE_DIR, ".db", "history.json")
        self.db_path = db_path
        db_dir = db_path[: db_path.rfind("/")]
        if not os.path.exists(db_dir):
            os.makedirs(db_dir)

    def save(self, record: Record) -> None:
        data = record._asdict()

        with TinyDB(self.db_path, sort_keys=True, indent=4) as db:
            hist = db.search(Query().personal_id == record.personal_id)
            if self._compare_history(data, hist) is None:
                db.insert(data)

    def _compare_history(
        self, data: Mapping[str, Any], hist: Iterable[Document]
    ) -> int:
        for idx, h in enumerate(hist):
            comp = [h[k] for k in data.keys() if h[k] == data[k]]
            if len(comp) == len(data):
                return idx
        return None
