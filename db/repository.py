from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from db.models import Base, SimulationRun, ProcessRecord
from core.scheduler import SimulationResult
from core.process import Process
from typing import List, Optional
import os

DB_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "simulations.db"
)

engine = create_engine(f"sqlite:///{DB_PATH}", echo=False)
SessionLocal = sessionmaker(bind=engine)

def init_db():
    """Create all tables if they don't exist."""
    Base.metadata.create_all(engine)

def save_run(
    algorithm: str,
    quantum: int,
    result: SimulationResult
) -> int:
    """Save a simulation run and return its ID."""
    session: Session = SessionLocal()
    try:
        run = SimulationRun(
            algorithm=algorithm,
            quantum=quantum,
            total_time=result.total_time,
            cpu_utilization=result.cpu_utilization,
            avg_waiting_time=result.avg_waiting_time,
            avg_turnaround=result.avg_turnaround_time,
            process_count=len(result.processes)
        )
        session.add(run)
        session.flush()

        for p in result.processes:
            record = ProcessRecord(
                run_id=run.id,
                name=p.name,
                process_type=p.process_type.value if hasattr(p.process_type, "value") else p.process_type,
                burst_time=p.burst_time,
                arrival_time=p.arrival_time,
                priority=p.priority,
                start_time=p.start_time,
                finish_time=p.finish_time,
                waiting_time=p.waiting_time,
                turnaround_time=p.turnaround_time
            )
            session.add(record)

        session.commit()
        return run.id
    finally:
        session.close()

def get_all_runs() -> List[SimulationRun]:
    """Retrieve all simulation runs ordered by newest first."""
    session: Session = SessionLocal()
    try:
        return session.query(SimulationRun)\
            .order_by(SimulationRun.created_at.desc())\
            .all()
    finally:
        session.close()

def get_run_with_processes(run_id: int) -> Optional[SimulationRun]:
    """Retrieve a single run with all its process records."""
    from sqlalchemy.orm import joinedload
    session: Session = SessionLocal()
    # try:
    #     return session.query(SimulationRun)\
    #         .filter(SimulationRun.id == run_id)\
    #         .first()
    # finally:
    #     session.close()
    try:
        run = session.query(SimulationRun)\
            .options(joinedload(SimulationRun.processes))\
            .filter(SimulationRun.id == run_id)\
            .first()
        if run:
            _ = run.processes
        return run
    finally:
        session.close()

def delete_run(run_id: int):
    """Delete a simulation run and its processes."""
    session: Session = SessionLocal()
    try:
        run = session.query(SimulationRun)\
            .filter(SimulationRun.id == run_id).first()
        if run:
            session.delete(run)
            session.commit()
    finally:
        session.close()