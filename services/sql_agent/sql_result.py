from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional


@dataclass(slots=True)
class SQLAgentResult:
    """
    Kết quả chuẩn hóa của SQL Agent.
    - Không chứa logic nghiệp vụ
    - Không diễn giải dữ liệu
    - Chỉ mang dữ liệu + metadata cần thiết cho tầng trên
    """

    # SQL đã được sinh và thực thi
    sql: str

    # Danh sách tên cột (giữ thứ tự)
    columns: List[str]

    # Dữ liệu trả về dạng structured rows
    # Mỗi row là dict: {column_name: value}
    rows: List[Dict[str, Any]]

    # Optional metadata (debug, timing, source, etc.)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def is_empty(self) -> bool:
        """
        Kiểm tra kết quả có dữ liệu hay không.
        """
        return not self.rows

    def row_count(self) -> int:
        """
        Số lượng dòng kết quả.
        """
        return len(self.rows)

    def first_row(self) -> Optional[Dict[str, Any]]:
        """
        Lấy dòng đầu tiên (nếu có).
        """
        return self.rows[0] if self.rows else None

    def to_human_text(self, max_rows: int = 5, compact: bool = False) -> str:
        """
        Chuyển SQL result thành text trung lập.
        compact=True chỉ dùng cho SQL-only intent.
        """

        if not self.rows:
            return "Không có dữ liệu phù hợp trong cơ sở dữ liệu."

        # Compact mode: 1 row, 1 column
        if compact and len(self.rows) == 1 and len(self.columns) == 1:
            col = self.columns[0]
            return str(self.rows[0].get(col))

        lines = []
        rows = self.rows[:max_rows]

        for row in rows:
            parts = [
                f"{col}: {row[col]}"
                for col in self.columns
                if col in row
            ]
            lines.append("- " + ", ".join(parts))

        if len(self.rows) > max_rows:
            lines.append(f"... và {len(self.rows) - max_rows} dòng khác")

        return "\n".join(lines)


