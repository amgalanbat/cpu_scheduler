from sqlalchemy import (
    Column, Integer, String, Float,
    DateTime, ForeignKey, create_engine
)
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

Base = declarative_base()

class SimulationRun(Base):
    __tablename__ = "simulation_runs"

    id            = Column(Integer, primary_key=True, autoincrement=True)
    algorithm     = Column(String, nullable=False)
    quantum       = Column(Integer, default=2)
    total_time    = Column(Integer)
    cpu_utilization  = Column(Float)
    avg_waiting_time = Column(Float)
    avg_turnaround   = Column(Float)
    process_count    = Column(Integer)
    created_at    = Column(DateTime, default=datetime.now)

    processes = relationship(
        "ProcessRecord",
        back_populates="run",
        cascade="all, delete-orphan"
    )

class ProcessRecord(Base):
    __tablename__ = "process_records"

    id           = Column(Integer, primary_key=True, autoincrement=True)
    run_id       = Column(Integer, ForeignKey("simulation_runs.id"))
    name         = Column(String)
    process_type = Column(String)
    burst_time   = Column(Integer)
    arrival_time = Column(Integer)
    priority     = Column(Integer)
    start_time   = Column(Integer)
    finish_time  = Column(Integer)
    waiting_time = Column(Integer)
    turnaround_time = Column(Integer)

    run = relationship("SimulationRun", back_populates="processes")