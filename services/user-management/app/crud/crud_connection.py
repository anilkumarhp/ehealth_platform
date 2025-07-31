import uuid
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.db import models
from app.core.exceptions import ConnectionNotFoundException

def get_connection_by_id(db: Session, connection_id: uuid.UUID, raise_exception: bool = False) -> models.FamilyConnection | None:
    """
    Retrieves a connection by its ID.
    If raise_exception is True, it will raise ConnectionNotFoundException instead of returning None.
    """
    connection = db.query(models.FamilyConnection).filter(models.FamilyConnection.id == connection_id).first()
    if not connection and raise_exception:
        raise ConnectionNotFoundException()
    return connection

def get_connections_for_user(db: Session, user_id: uuid.UUID) -> list[models.FamilyConnection]:
    """Get all connections where the user is either the requester or the approver."""
    return db.query(models.FamilyConnection).filter(
        or_(models.FamilyConnection.requester_id == user_id, models.FamilyConnection.approver_id == user_id)
    ).all()

def create_connection(db: Session, *, requester_id: uuid.UUID, approver_id: uuid.UUID, relationship_type: str) -> models.FamilyConnection:
    """Create a new PENDING connection request."""
    db_connection = models.FamilyConnection(
        requester_id=requester_id,
        approver_id=approver_id,
        relationship_type=relationship_type,
        status=models.ConnectionStatus.VERIFICATION_PENDING # Default to pending verification
    )
    db.add(db_connection)
    db.commit()
    db.refresh(db_connection)
    return db_connection

def update_connection_status(db: Session, connection: models.FamilyConnection, status: models.ConnectionStatus) -> models.FamilyConnection:
    """Update the status of a connection."""
    connection.status = status
    db.add(connection)
    db.commit()
    db.refresh(connection)
    return connection

def delete_connection(db: Session, connection: models.FamilyConnection):
    """Delete a connection from the database."""
    db.delete(connection)
    db.commit()
    return True