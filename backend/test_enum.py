from enum import Enum

class PlanType(str, Enum):
    STARTER = "starter"

print(f"str(PlanType.STARTER): {str(PlanType.STARTER)}")
print(f"PlanType.STARTER.value: {PlanType.STARTER.value}")
print(f"f-string: {PlanType.STARTER}")
