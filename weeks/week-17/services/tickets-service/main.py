from fastapi import FastAPI, HTTPException, Depends, status, Header
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime
from typing import Optional, List
import os
import logging
import httpx
import asyncio

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Tickets Service", version="1.0.0")

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://tickets_user:tickets_pass@localhost:5432/tickets_db")
USERS_SERVICE_URL = os.getenv("USERS_SERVICE_URL", "http://localhost:8125")
NOTIFICATION_SERVICE_URL = os.getenv("NOTIFICATION_SERVICE_URL", "localhost:50051")
ANALYTICS_SERVICE_URL = os.getenv("ANALYTICS_SERVICE_URL", "http://localhost:8126")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    status = Column(String(50), nullable=False, default="new")
    priority = Column(Integer, default=3)
    assignee_id = Column(Integer)
    reporter_id = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class TicketCreate(BaseModel):
    title: str
    description: Optional[str] = None
    status: str = "new"
    priority: int = 3
    assignee_id: Optional[int] = None
    reporter_id: int


class TicketUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[int] = None
    assignee_id: Optional[int] = None


class TicketResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    status: str
    priority: int
    assignee_id: Optional[int]
    reporter_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def verify_user_exists(user_id: int) -> bool:
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{USERS_SERVICE_URL}/api/users/{user_id}", timeout=5.0)
            return response.status_code == 200
    except Exception as e:
        logger.warning(f"Could not verify user {user_id}: {e}")
        return True


async def send_notification_async(user_id: int, title: str, message: str):
    try:
        logger.info(f"Notification queued for user {user_id}: {title}")
    except Exception as e:
        logger.error(f"Failed to send notification: {e}")


@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "tickets-service"}


@app.get("/ready")
def readiness_check(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        return {"status": "ready"}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Database not ready: {str(e)}")


@app.post("/api/tickets", response_model=TicketResponse, status_code=status.HTTP_201_CREATED)
async def create_ticket(ticket_data: TicketCreate, db: Session = Depends(get_db)):
    logger.info(f"Creating ticket: {ticket_data.title}")

    if ticket_data.status not in ["new", "in_progress", "resolved", "closed"]:
        raise HTTPException(status_code=400, detail="Invalid status")

    if ticket_data.priority < 1 or ticket_data.priority > 5:
        raise HTTPException(status_code=400, detail="Priority must be between 1 and 5")

    if not await verify_user_exists(ticket_data.reporter_id):
        raise HTTPException(status_code=400, detail="Reporter user not found")

    if ticket_data.assignee_id and not await verify_user_exists(ticket_data.assignee_id):
        raise HTTPException(status_code=400, detail="Assignee user not found")

    new_ticket = Ticket(
        title=ticket_data.title,
        description=ticket_data.description,
        status=ticket_data.status,
        priority=ticket_data.priority,
        assignee_id=ticket_data.assignee_id,
        reporter_id=ticket_data.reporter_id
    )

    db.add(new_ticket)
    db.commit()
    db.refresh(new_ticket)

    if ticket_data.assignee_id:
        asyncio.create_task(send_notification_async(
            ticket_data.assignee_id,
            "New Ticket Assigned",
            f"You have been assigned ticket #{new_ticket.id}: {new_ticket.title}"
        ))

    return TicketResponse.from_orm(new_ticket)


@app.get("/api/tickets", response_model=List[TicketResponse])
def list_tickets(
    status: Optional[str] = None,
    assignee_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    query = db.query(Ticket)

    if status:
        query = query.filter(Ticket.status == status)
    if assignee_id:
        query = query.filter(Ticket.assignee_id == assignee_id)

    tickets = query.offset(skip).limit(limit).all()
    return [TicketResponse.from_orm(ticket) for ticket in tickets]


@app.get("/api/tickets/{ticket_id}", response_model=TicketResponse)
def get_ticket(ticket_id: int, db: Session = Depends(get_db)):
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return TicketResponse.from_orm(ticket)


@app.put("/api/tickets/{ticket_id}", response_model=TicketResponse)
async def update_ticket(
    ticket_id: int,
    ticket_data: TicketUpdate,
    db: Session = Depends(get_db)
):
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    old_assignee = ticket.assignee_id
    old_status = ticket.status

    if ticket_data.title is not None:
        ticket.title = ticket_data.title
    if ticket_data.description is not None:
        ticket.description = ticket_data.description
    if ticket_data.status is not None:
        if ticket_data.status not in ["new", "in_progress", "resolved", "closed"]:
            raise HTTPException(status_code=400, detail="Invalid status")
        ticket.status = ticket_data.status
    if ticket_data.priority is not None:
        if ticket_data.priority < 1 or ticket_data.priority > 5:
            raise HTTPException(status_code=400, detail="Priority must be between 1 and 5")
        ticket.priority = ticket_data.priority
    if ticket_data.assignee_id is not None:
        if not await verify_user_exists(ticket_data.assignee_id):
            raise HTTPException(status_code=400, detail="Assignee user not found")
        ticket.assignee_id = ticket_data.assignee_id

    ticket.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(ticket)

    if ticket.assignee_id and ticket.assignee_id != old_assignee:
        asyncio.create_task(send_notification_async(
            ticket.assignee_id,
            "Ticket Assigned",
            f"Ticket #{ticket.id} has been assigned to you"
        ))

    if ticket.status != old_status and ticket.status == "resolved":
        asyncio.create_task(send_notification_async(
            ticket.reporter_id,
            "Ticket Resolved",
            f"Your ticket #{ticket.id} has been resolved"
        ))

    return TicketResponse.from_orm(ticket)


@app.patch("/api/tickets/{ticket_id}/status", response_model=TicketResponse)
async def update_ticket_status(
    ticket_id: int,
    status: str,
    db: Session = Depends(get_db)
):
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    if status not in ["new", "in_progress", "resolved", "closed"]:
        raise HTTPException(status_code=400, detail="Invalid status")

    old_status = ticket.status
    ticket.status = status
    ticket.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(ticket)

    if status == "resolved" and old_status != "resolved":
        asyncio.create_task(send_notification_async(
            ticket.reporter_id,
            "Ticket Resolved",
            f"Your ticket #{ticket.id} has been resolved"
        ))

    return TicketResponse.from_orm(ticket)


@app.delete("/api/tickets/{ticket_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_ticket(ticket_id: int, db: Session = Depends(get_db)):
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    db.delete(ticket)
    db.commit()
    return None


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8124)
