from app.database.database import SessionLocal
from app.database.models import Alert


def _to_dict(alert: Alert) -> dict:
    return {
        "id": alert.id,
        "symbol": alert.symbol,
        "indicator": alert.indicator,
        "comparison": alert.comparison,
        "threshold": alert.threshold,
        "active": bool(alert.active),
    }


class AlertService:
    def __init__(self):
        self.db = SessionLocal()

    def get_all(self):
        return [_to_dict(a) for a in self.db.query(Alert).all()]

    def add(self, symbol, indicator, comparison, threshold=0):
        alert = Alert(
            symbol=symbol.upper(),
            indicator=indicator,
            comparison=comparison,
            threshold=threshold,
            active=1,
        )
        self.db.add(alert)
        self.db.commit()
        self.db.refresh(alert)

        return self.get_all()

    def remove(self, alert_id):
        self.db.query(Alert).filter(Alert.id == alert_id).delete()
        self.db.commit()

        return self.get_all()

    def set_active(self, alert_id, active: bool):
        alert = self.db.query(Alert).filter(Alert.id == alert_id).first()
        if alert:
            alert.active = 1 if active else 0
            self.db.commit()

        return self.get_all()
