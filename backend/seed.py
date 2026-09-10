import os
import sys
import random
from datetime import datetime, timedelta

# Add backend dir to sys path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.database import SessionLocal, engine
from app.models.domain import (
    Base, User, RoleEnum, RequestStatus, RegistrationRequest, 
    VictimProfile, Case, CaseStatus, Assessment, DistressScore, 
    Alert, AlertLevel, Intervention
)
from app.core.security import get_password_hash

def seed_data():
    db = SessionLocal()
    
    # Check if we already have data
    if db.query(User).count() > 0:
        print("Database already seeded!")
        return

    print("Seeding database...")
    
    # 1. Create Users
    admin = User(
        email="admin@sahay.org",
        hashed_password=get_password_hash("admin123"),
        full_name="Admin User",
        role=RoleEnum.ADMIN.value,
        organization="SAHAY HQ"
    )
    
    ngo = User(
        email="ngo@sahay.org",
        hashed_password=get_password_hash("ngo123"),
        full_name="NGO Coordinator",
        role=RoleEnum.NGO.value,
        organization="Helping Hands"
    )

    responder = User(
        email="responder@sahay.org",
        hashed_password=get_password_hash("resp123"),
        full_name="First Responder",
        role=RoleEnum.RESPONDER.value,
        organization="Local Police"
    )
    
    therapist = User(
        email="therapist@sahay.org",
        hashed_password=get_password_hash("thera123"),
        full_name="Dr. Smith",
        role=RoleEnum.THERAPIST.value,
        organization="City Hospital"
    )
    
    db.add_all([admin, ngo, responder, therapist])
    db.commit()
    
    users = [admin, ngo, responder, therapist]

    # 2. Registration Requests
    req1 = RegistrationRequest(
        name="Pending NGO",
        email="pending@ngo.org",
        password_hash=get_password_hash("pass123"),
        role=RoleEnum.NGO.value,
        status=RequestStatus.PENDING.value
    )
    db.add(req1)

    # 3. Victims
    victims = []
    genders = ["Female", "Male", "Other"]
    for i in range(10):
        v = VictimProfile(
            first_name=f"Victim_{i}",
            last_name="Doe",
            age=random.randint(18, 65),
            gender=random.choice(genders),
            location=f"District {random.randint(1, 5)}"
        )
        db.add(v)
        victims.append(v)
    db.commit()

    # 4. Cases
    cases = []
    statuses = [CaseStatus.OPEN.value, CaseStatus.IN_PROGRESS.value, CaseStatus.RESOLVED.value, CaseStatus.CLOSED.value]
    for i in range(15):
        assigned = random.choice([None, ngo.id, responder.id, therapist.id])
        c = Case(
            title=f"Incident {i}",
            description=f"Description for incident {i} involving multiple factors.",
            status=random.choice(statuses),
            victim_id=random.choice(victims).id,
            assigned_to=assigned
        )
        db.add(c)
        cases.append(c)
    db.commit()

    # 5. Distress Scores, Assessments, Alerts, Interventions
    for c in cases:
        # Distress
        ds = DistressScore(
            victim_id=c.victim_id,
            score=random.uniform(10, 95),
            factors={"fear": random.random(), "stress": random.random()}
        )
        db.add(ds)

        # Assessment
        ass = Assessment(
            case_id=c.id,
            assessment_data={"question1": "yes", "question2": "no"},
            ai_summary="AI generated summary based on initial findings."
        )
        db.add(ass)

        # Alert
        if random.random() > 0.5:
            alt = Alert(
                case_id=c.id,
                level=random.choice([AlertLevel.LOW.value, AlertLevel.MEDIUM.value, AlertLevel.HIGH.value, AlertLevel.CRITICAL.value]),
                message="Elevated distress score detected."
            )
            db.add(alt)

        # Intervention
        if c.status in [CaseStatus.IN_PROGRESS.value, CaseStatus.RESOLVED.value, CaseStatus.CLOSED.value]:
            inv = Intervention(
                case_id=c.id,
                created_by=admin.id,
                action_taken="Follow up call conducted",
                outcome="Stable"
            )
            db.add(inv)

    db.commit()
    print("Database seeded successfully with demo data.")

if __name__ == "__main__":
    seed_data()
