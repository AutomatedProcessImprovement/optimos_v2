from dataclasses import dataclass

from dataclass_wizard import JSONWizard


@dataclass(frozen=True)
class Probability(JSONWizard):
    """Probability of taking a specific path at a gateway."""

    path_id: str
    value: float


@dataclass(frozen=True)
class GatewayBranchingProbability(JSONWizard):
    """Collection of probabilities for paths from a gateway."""

    gateway_id: str
    probabilities: list[Probability]
