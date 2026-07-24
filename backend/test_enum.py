from enum import Enum


class PlanType(str, Enum):
    STARTER = "starter"

print(f"str(PlanType.STARTER): {PlanType.STARTER!s}")
print(f"PlanType.STARTER.value: {PlanType.STARTER.value}")
print(f"f-string: {PlanType.STARTER}")
