from datetime import datetime
from enum import Enum
from typing import List

from pydantic import BaseModel, Field, ValidationError, model_validator


class Rank(str, Enum):
    cadet = "cadet"
    officer = "officer"
    lieutenant = "lieutenant"
    captain = "captain"
    commander = "commander"


class CrewMember(BaseModel):
    member_id: str = Field(min_length=3, max_length=10)
    name: str = Field(min_length=2, max_length=50)
    rank: Rank = Field(...)
    age: int = Field(ge=18, le=80)
    specialization: str = Field(min_length=3, max_length=30)
    years_experience: int = Field(ge=0, le=50)
    is_active: bool = Field(default=True)


class SpaceMission(BaseModel):
    mission_id: str = Field(min_length=5, max_length=15)
    mission_name: str = Field(min_length=3, max_length=100)
    destination: str = Field(min_length=3, max_length=50)
    launch_date: datetime = Field(...)
    duration_days: int = Field(ge=1, le=3650)

    crew: List[CrewMember] = Field(min_length=1, max_length=12)

    mission_status: str = Field(default="planned")
    budget_millions: float = Field(ge=1.0, le=10000.0)

    @model_validator(mode='after')
    def validate_mission_rules(self) -> 'SpaceMission':

        if not self.mission_id.startswith("M"):
            raise ValueError(
                "Mission ID must start with 'M'"
            )

        has_leader = any(
            m.rank in (Rank.commander, Rank.captain)
            for m in self.crew
        )
        if not has_leader:
            raise ValueError(
                "Mission must have at least one Commander or Captain"
            )

        if self.duration_days > 365:
            total = len(self.crew)
            experienced_count = sum(
                1 for m in self.crew
                if m.years_experience >= 5
            )
            if experienced_count * 2 < total:
                raise ValueError(
                    "Long missions (> 365 days) require "
                    "at least 50% experienced crew (5+ years)"
                )

        inactive = [m.name for m in self.crew if not m.is_active]
        if inactive:
            raise ValueError(
                f"All crew members must be active. "
                f"Inactive members: {', '.join(inactive)}"
            )

        return self


def display_mission(mission: SpaceMission) -> None:
    print("Valid mission created:")
    print(f"Mission: {mission.mission_name}")
    print(f"ID: {mission.mission_id}")
    print(f"Destination: {mission.destination}")
    print(f"Duration: {mission.duration_days} days")
    print(f"Budget: ${mission.budget_millions}M")
    print(f"Crew size: {len(mission.crew)}")
    print("Crew members:")
    for member in mission.crew:
        print(
            f"  - {member.name} ({member.rank.value})"
            f" - {member.specialization}"
        )


def main() -> None:
    print("Space Mission Crew Validation")
    print("=" * 41)

    mission = SpaceMission(
        mission_id="M2024_MARS",
        mission_name="Mars Colony Establishment",
        destination="Mars",
        launch_date=datetime(2024, 6, 1),
        duration_days=900,
        budget_millions=2500.0,
        crew=[
            CrewMember(
                member_id="CM001",
                name="Sarah Connor",
                rank=Rank.commander,
                age=45,
                specialization="Mission Command",
                years_experience=20
            ),
            CrewMember(
                member_id="CM002",
                name="John Smith",
                rank=Rank.lieutenant,
                age=35,
                specialization="Navigation",
                years_experience=10
            ),
            CrewMember(
                member_id="CM003",
                name="Alice Johnson",
                rank=Rank.officer,
                age=28,
                specialization="Engineering",
                years_experience=6
            ),
        ]
    )
    display_mission(mission)

    print("\n" + "=" * 41)
    print("Expected validation error:")

    try:
        SpaceMission(
            mission_id="M2024_BAD",
            mission_name="Doomed Mission",
            destination="Venus",
            launch_date=datetime(2024, 7, 1),
            duration_days=200,
            budget_millions=500.0,
            crew=[
                CrewMember(
                    member_id="CM010",
                    name="Bob Cadet",
                    rank=Rank.cadet,
                    age=22,
                    specialization="Cleaning",
                    years_experience=0
                ),
                CrewMember(
                    member_id="CM011",
                    name="Jane Officer",
                    rank=Rank.officer,
                    age=30,
                    specialization="Science",
                    years_experience=3
                ),
            ]
        )
    except ValidationError as e:
        for error in e.errors():
            print(error["msg"])


if __name__ == "__main__":
    main()
