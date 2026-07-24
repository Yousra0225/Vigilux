import random
from datetime import UTC, datetime, timedelta

from sqlmodel import Session, select

from app.core.db import engine
from app.core.security import get_password_hash
from app.models.competitor import Competitor, TrackingStatus
from app.models.event import Event, EventType
from app.models.project import Project
from app.models.user import PlanType, User


def seed_data():
    """Populate the database with test data."""
    print("🌱 Seeding data...")

    with Session(engine) as session:
        # --- Users ---
        users_data = [
            {
                "email": "starter@example.com",
                "password": "password123",
                "plan_type": PlanType.STARTER,
                "trial_start_date": None
            },
            {
                "email": "growth@example.com",
                "password": "password123",
                "plan_type": PlanType.GROWTH,
                "trial_start_date": datetime.now(UTC)
            },
            {
                "email": "ultimate@example.com",
                "password": "password123",
                "plan_type": PlanType.ULTIMATE,
                "trial_start_date": None
            }
        ]

        created_users = []
        for user_info in users_data:
            user_email = user_info["email"].lower()
            existing_user = session.exec(select(User).where(User.email == user_email)).first()
            if not existing_user:
                user = User(
                    email=user_email,
                    hashed_password=get_password_hash(user_info["password"]),
                    plan_type=user_info["plan_type"],
                    trial_start_date=user_info["trial_start_date"],
                    is_verified=True
                )
                session.add(user)
                created_users.append(user)
                print(f"Created user: {user.email}")
            else:
                created_users.append(existing_user)
                print(f"User already exists: {existing_user.email}")
        
        session.commit()
        for user in created_users:
            session.refresh(user)

        # --- Projects ---
        created_projects = []
        for user in created_users:
            # Check if user already has a project to avoid duplicates on re-run
            existing_project = session.exec(select(Project).where(Project.user_id == user.id)).first()
            
            if not existing_project:
                project = Project(
                    user_id=user.id,
                    url=f"https://{user.plan_type.value}-app.com",
                    description=f"Main project for {user.plan_type.value} user",
                )
                session.add(project)
                created_projects.append(project)
                print(f"Created project for user: {user.email}")
            else:
                created_projects.append(existing_project)
                print(f"Project already exists for user: {user.email}")

        session.commit()
        for project in created_projects:
            session.refresh(project)

        # --- Competitors & Events ---
        competitor_names = [
            "Competitor A", "Competitor B", "Competitor C", "Rival X", "Nemesis Y", 
            "Challenger Z", "Market Leader", "Niche Player", "Upstart", "Legacy Corp"
        ]
        
        event_descriptions = {
            EventType.PRICE: ["Decreased pricing by 10%", "Launched a new enterprise tier", "Changed to subscription model", "Offered lifetime deal"],
            EventType.FEATURE: ["Released API v2", "Added dark mode", "Integrated with Slack", "Launched mobile app", "Removed legacy feature"],
            EventType.HEALTH: ["Server downtime reported", "CEO resigned", "Acquired by BigCorp", "Layoffs announced", "Funding round raised"],
            EventType.NEW_ENTRANT: ["Just launched on ProductHunt", "Beta access opened", "Stealth mode exit"]
        }

        for project in created_projects:
            # Check if project already has competitors
            existing_competitors_count = session.exec(select(Competitor).where(Competitor.project_id == project.id)).all()
            if len(existing_competitors_count) > 0:
                print(f"Competitors already exist for project {project.id}, skipping generation.")
                continue

            num_competitors = random.randint(5, 10)
            print(f"Generating {num_competitors} competitors for project {project.id}...")

            for i in range(num_competitors):
                comp_name = f"{random.choice(competitor_names)} {random.randint(1, 100)}"
                competitor = Competitor(
                    project_id=project.id,
                    name=comp_name,
                    url=f"https://{comp_name.lower().replace(' ', '')}.com",
                    score=random.randint(0, 100),
                    status=TrackingStatus.ACTIVE
                )
                session.add(competitor)
                session.commit()
                session.refresh(competitor)

                # Generate Events for this Competitor
                num_events = random.randint(3, 8)
                for _ in range(num_events):
                    e_type = random.choice(list(EventType))
                    score_val = random.randint(1, 10)
                    
                    # Ensure some high scores (>7)
                    if random.random() < 0.2:
                        score_val = random.randint(8, 10)
                    
                    description = random.choice(event_descriptions[e_type])
                    
                    event = Event(
                        competitor_id=competitor.id,
                        type=e_type,
                        description=description,
                        score=score_val,
                        timestamp=datetime.now(UTC) - timedelta(days=random.randint(0, 30))
                    )
                    session.add(event)
        
        session.commit()
        print("✅ Seeding complete.")

if __name__ == "__main__":
    seed_data()
