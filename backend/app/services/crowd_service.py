import datetime
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Dict, Any, Optional
from app.models.models import CrowdDataModel
from app.models.schemas import CrowdZoneResponse, CrowdAllResponse

class CrowdService:
    def __init__(self, db: Session):
        self.db = db

    def get_zone_density(self, zone_id: str) -> CrowdZoneResponse:
        """
        Get crowd information, including predictions and trends, for a specific zone.
        """
        # Fetch last 3 points to determine trend
        history = self.db.query(CrowdDataModel).filter(
            CrowdDataModel.zone_id == zone_id
        ).order_by(desc(CrowdDataModel.timestamp)).limit(3).all()

        if not history:
            # Fallback if no records found
            return CrowdZoneResponse(
                zone_id=zone_id,
                current_density=0.15,
                level="low",
                prediction_5min="low",
                prediction_15min="low",
                risk_level="low",
                suggested_alternative=None,
                trend="stable"
            )

        latest = history[0]
        
        # Calculate trend
        trend = "stable"
        if len(history) >= 2:
            prev = history[1]
            diff = latest.current_density - prev.current_density
            if diff > 0.02:
                trend = "rising"
            elif diff < -0.02:
                trend = "falling"

        # Predictions calculations
        density_5 = latest.current_density
        density_15 = latest.current_density
        
        if trend == "rising":
            density_5 = min(1.0, latest.current_density + 0.05)
            density_15 = min(1.0, latest.current_density + 0.15)
        elif trend == "falling":
            density_5 = max(0.0, latest.current_density - 0.05)
            density_15 = max(0.0, latest.current_density - 0.15)

        level_5 = self._get_level_str(density_5)
        level_15 = self._get_level_str(density_15)

        # Risk level calculation
        risk_level = "low"
        if latest.current_density >= 0.9 or trend == "rising" and latest.current_density >= 0.8:
            risk_level = "critical"
        elif latest.current_density >= 0.7:
            risk_level = "high"
        elif latest.current_density >= 0.4:
            risk_level = "medium"

        # Alternative suggested zone
        suggested_alternative = None
        if latest.current_density >= 0.7:
            # Recommend an alternative gate or concourse
            if "gate" in zone_id:
                # Suggest gate_d or gate_e which are typically less congested
                suggested_alternative = "gate_d" if zone_id != "gate_d" else "gate_e"
            elif "concourse" in zone_id:
                suggested_alternative = "concourse_3" if zone_id != "concourse_3" else "concourse_4"

        return CrowdZoneResponse(
            zone_id=latest.zone_id,
            current_density=round(latest.current_density, 2),
            level=latest.level,
            prediction_5min=level_5,
            prediction_15min=level_15,
            risk_level=risk_level,
            suggested_alternative=suggested_alternative,
            trend=trend
        )

    def get_all_zones(self) -> CrowdAllResponse:
        """
        Get latest crowd information for all unique zones in the database.
        """
        # Get unique zone_ids
        zone_ids = [z[0] for z in self.db.query(CrowdDataModel.zone_id).distinct().all()]
        
        zones_data = []
        for zone_id in zone_ids:
            zones_data.append(self.get_zone_density(zone_id))

        return CrowdAllResponse(
            zones=zones_data,
            timestamp=datetime.datetime.utcnow().isoformat()
        )

    def purge_old_data(self):
        """
        Auto-purge crowd data older than 24 hours.
        """
        cutoff = datetime.datetime.utcnow() - datetime.timedelta(hours=24)
        self.db.query(CrowdDataModel).filter(CrowdDataModel.timestamp < cutoff).delete()
        self.db.commit()

    def _get_level_str(self, density: float) -> str:
        if density >= 0.9:
            return "critical"
        elif density >= 0.7:
            return "high"
        elif density >= 0.3:
            return "medium"
        return "low"
