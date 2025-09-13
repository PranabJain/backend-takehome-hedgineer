from __future__ import annotations

import io
from typing import Any, Dict, List

import pandas as pd


def export_excel_bytes(
    performance_rows: List[Dict[str, Any]],
    composition_rows: List[Dict[str, Any]],
    changes_rows: List[Dict[str, Any]],
) -> bytes:
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
        if performance_rows:
            df_perf = pd.DataFrame(performance_rows)
            df_perf.to_excel(writer, sheet_name="Performance", index=False)
        if composition_rows:
            df_compo = pd.DataFrame(composition_rows)
            df_compo.to_excel(writer, sheet_name="Composition", index=False)
        if changes_rows:
            # normalize lists to comma-separated strings for Excel
            df_changes = pd.DataFrame(changes_rows)
            if not df_changes.empty:
                if "entered" in df_changes:
                    df_changes["entered"] = df_changes["entered"].apply(
                        lambda x: ", ".join(x) if isinstance(x, list) else x
                    )
                if "exited" in df_changes:
                    df_changes["exited"] = df_changes["exited"].apply(
                        lambda x: ", ".join(x) if isinstance(x, list) else x
                    )
            df_changes.to_excel(writer, sheet_name="Changes", index=False)
    return buffer.getvalue()


