from __future__ import annotations

from typing import Any, Dict, List, Optional, Union
from datetime import date
import datetime as dt

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from .db import init_db
from .cache import cache
from .services.index_service import (
    build_index,
    get_index_composition,
    get_index_performance,
    get_composition_changes,
    _normalize_date,  # import for normalization
)
from .utils.exporter import export_excel_bytes


class BuildIndexRequest(BaseModel):
    start_date: Union[str, date]
    end_date: Optional[Union[str, date]] = None


class ExportRequest(BaseModel):
    start_date: Union[str, date]
    end_date: Optional[Union[str, date]] = None


app = FastAPI(title="Equal-Weighted Top-100 Index API")


@app.on_event("startup")
def startup() -> None:
    init_db()


@app.post("/build-index")
def api_build_index(req: BuildIndexRequest):
    try:
        return build_index(req.start_date, req.end_date)
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/index-performance")
def api_index_performance(
    start_date: Union[str, date], end_date: Optional[Union[str, date]] = None
) -> List[Dict[str, Any]]:
    try:
        start_str = _normalize_date(start_date)
        end_str = _normalize_date(end_date) or start_str

        cache_key = f"perf:{start_str}:{end_str}"
        cached = cache.get_json(cache_key)
        if cached is not None:
            return cached

        rows = get_index_performance(start_str, end_str)
        cache.set_json(cache_key, rows, 3600)
        return rows
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/index-composition")
def api_index_composition(date: Union[str, date]) -> List[Dict[str, Any]]:
    try:
        date_str = _normalize_date(date)
        cache_key = f"compo:{date_str}"
        cached = cache.get_json(cache_key)
        if cached is not None:
            return cached

        rows = get_index_composition(date_str)
        cache.set_json(cache_key, rows, 3600)
        return rows
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/composition-changes")
def api_composition_changes(
    start_date: Union[str, date], end_date: Union[str, date]
) -> List[Dict[str, Any]]:
    try:
        start_str = _normalize_date(start_date)
        end_str = _normalize_date(end_date)

        cache_key = f"changes:{start_str}:{end_str}"
        cached = cache.get_json(cache_key)
        if cached is not None:
            return cached

        rows = get_composition_changes(start_str, end_str)
        cache.set_json(cache_key, rows, 3600)
        return rows
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/export-data")
def api_export(req: ExportRequest):
    start = req.start_date
    end = req.end_date or start

    perf = get_index_performance(start, end)
    start_dt = start if isinstance(start, date) else dt.date.fromisoformat(str(start))
    end_dt = end if isinstance(end, date) else dt.date.fromisoformat(str(end))

    dates = [start_dt + dt.timedelta(days=i) for i in range((end_dt - start_dt).days + 1)]
    compo_rows: List[Dict[str, Any]] = []
    for d in dates:
        rows = get_index_composition(d)
        for r in rows:
            compo_rows.append({"date": d.isoformat(), **r})

    changes = get_composition_changes(start, end)

    xlsx_bytes = export_excel_bytes(perf, compo_rows, changes)
    from fastapi.responses import Response

    return Response(
        content=xlsx_bytes,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": "attachment; filename=index_export.xlsx"
        },
    )
