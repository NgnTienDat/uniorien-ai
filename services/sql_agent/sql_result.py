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

    def to_human_text(self) -> str:
        """
        Chuyển kết quả SQL sang dạng text dễ đọc cho người dùng.
        Không suy luận, không thêm thông tin mới.

        Với câu hỏi phức tạp:
            đưa SQLAgentResult + question → LLM
            LLM diễn giải thành tiếng Việt tự nhiên hơn
        """

        if not self.rows:
            return "Not found any data."

        # Case 1: 1 row, 1 column
        if len(self.rows) == 1 and len(self.columns) == 1:
            col = self.columns[0]
            value = self.rows[0].get(col)
            return str(value)

        # Case 2: nhiều dòng → list ngắn gọn
        lines = []
        for idx, row in enumerate(self.rows, start=1):
            parts = [f"{col}: {row.get(col)}" for col in self.columns]
            lines.append(f"{idx}. " + ", ".join(parts))

        return "\n".join(lines)

