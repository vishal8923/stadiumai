"""Crowd density tracking, predictions, and risk assessment service."""
import datetime
from collections import defaultdict
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from app.models.models import CrowdDataModel
from app.models.schemas import CrowdZoneResponse, CrowdAllResponse


class CrowdService:
    """Service for querying crowd density, computing trends, and suggesting alternatives."""

    def __init__(self, db: Session):
        self.db = db

    def get_zone_density(self, zone_id: str) -> CrowdZoneResponse:
        """Get crowd information, including predictions and trends, for a specific zone."""
        history = self.db.query(CrowdDataModel).filter(
            CrowdDataModel.zone_id == zone_id,
        ).order_by(desc(CrowdDataModel.timestamp)).limit(3).all()

        if not history:
            return CrowdZoneResponse(
                zone_id=zone_id, current_density=0.15, level="low",
                prediction_5min="low", prediction_15min="low",
                risk_level="low", suggested_alternative=None, trend="stable",
            )

        return self._build_zone_response(history)

    def get_all_zones(self) -> CrowdAllResponse:
        """Get latest crowd information for all zones using a single DB round-trip.

        Fetches the most-recent record per zone via a grouped subquery,
        then fetches a second record per zone for trend analysis — all in
        two queries total regardless of zone count.
        """
        # Query 1: latest record per zone (single grouped subquery)
        subq = (
            self.db.query(
                CrowdDataModel.zone_id,
                func.max(CrowdDataModel.id).label("max_id"),
            )
            .group_by(CrowdDataModel.zone_id)
            .subquery()
        )
        latest_records = (
            self.db.query(CrowdDataModel)
            .join(subq, CrowdDataModel.id == subq.c.max_id)
            .all()
        )

        if not latest_records:
            return CrowdAllResponse(
                zones=[],
                timestamp=datetime.datetime.now(datetime.timezone.utc).isoformat(),
            )

        zone_ids = [r.zone_id for r in latest_records]

        # Query 2: fetch up to 2 most-recent records per zone for trend
        all_recent = (
            self.db.query(CrowdDataModel)
            .filter(CrowdDataModel.zone_id.in_(zone_ids))
            .order_by(desc(CrowdDataModel.timestamp))
            .all()
        )
        by_zone: dict[str, list] = defaultdict(list)
        for r in all_recent:
            if len(by_zone[r.zone_id]) < 2:
                by_zone[r.zone_id].append(r)

        zones_data = []
        for zone_id in zone_ids:
            history = by_zone.get(zone_id, [])
            if not history:
                zones_data.append(CrowdZoneResponse(
                    zone_id=zone_id, current_density=0.15, level="low",
                    prediction_5min="low", prediction_15min="low",
                    risk_level="low", suggested_alternative=None, trend="stable",
                ))
                continue
            zones_data.append(self._build_zone_response(history))

        return CrowdAllResponse(
            zones=zones_data,
            timestamp=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        )

    def _build_zone_response(self, history: list) -> CrowdZoneResponse:
        """Build a CrowdZoneResponse from a list of historical records (newest first)."""
        latest = history[0]

        trend = "stable"
        if len(history) >= 2:
            diff = latest.current_density - history[1].current_density
            if diff > 0.02:
                trend = "rising"
            elif diff < -0.02:
                trend = "falling"

        density_5 = latest.current_density + (0.05 if trend == "rising" else (-0.05 if trend == "falling" else 0))
        density_15 = latest.current_density + (0.15 if trend == "rising" else (-0.15 if trend == "falling" else 0))
        density_5 = max(0.0, min(1.0, density_5))
        density_15 = max(0.0, min(1.0, density_15))

        risk_level = "low"
        if latest.current_density >= 0.9 or (trend == "rising" and latest.current_density >= 0.8):
            risk_level = "critical"
        elif latest.current_density >= 0.7:
            risk_level = "high"
        elif latest.current_density >= 0.4:
            risk_level = "medium"

        suggested_alternative = None
        if latest.current_density >= 0.7:
            if "gate" in latest.zone_id:
                suggested_alternative = "gate_d" if latest.zone_id != "gate_d" else "gate_e"
            elif "concourse" in latest.zone_id:
                suggested_alternative = "concourse_3" if latest.zone_id != "concourse_3" else "concourse_4"

        return CrowdZoneResponse(
            zone_id=latest.zone_id,
            current_density=round(latest.current_density, 2),
            level=latest.level,
            prediction_5min=self._get_level_str(density_5),
            prediction_15min=self._get_level_str(density_15),
            risk_level=risk_level,
            suggested_alternative=suggested_alternative,
            trend=trend,
        )

    def purge_old_data(self):
        """Auto-purge crowd data older than 24 hours. Call infrequently."""
        cutoff = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=24)
        self.db.query(CrowdDataModel).filter(CrowdDataModel.timestamp < cutoff).delete()
        self.db.commit()

    @staticmethod
    def _get_level_str(density: float) -> str:
        """Convert numeric density to categorical level string."""
        if density >= 0.9:
            return "critical"
        if density >= 0.7:
            return "high"
        if density >= 0.3:
            return "medium"
        return "low"
