import yaml
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Any, List

@dataclass
class ScenarioSection:
    id: str
    name: str
    type: str
    prompt: str

@dataclass
class Scenario:
    name: str
    system_context: str
    sections: List[ScenarioSection]

class ScenarioManager:
    def __init__(self, scenarios_dir: str = None):
        if scenarios_dir is None:
            self.scenarios_dir = Path(__file__).parent / "scenarios"
        else:
            self.scenarios_dir = Path(scenarios_dir)

    def get_scenario(self, scenario_type: str) -> Scenario:
        scenario_path = self.scenarios_dir / f"{scenario_type}.yaml"
        if not scenario_path.exists():
            raise FileNotFoundError(f"Scenario file not found: {scenario_path}")

        with open(scenario_path, "r", encoding="utf-8") as f:
            scenario_data = yaml.safe_load(f)
            return Scenario(
                name=scenario_data["name"],
                system_context=scenario_data["system_context"],
                sections=[ScenarioSection(**section) for section in scenario_data["sections"]]
            ) 