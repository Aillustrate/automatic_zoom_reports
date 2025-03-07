import yaml
from pathlib import Path
from dataclasses import dataclass
from typing import List, Dict

@dataclass
class Section:
    id: str
    name: str
    prompt: str
    type: str

@dataclass
class Scenario:
    name: str
    system_context: str
    sections: List[Section]

class ScenarioManager:
    def __init__(self, scenarios_dir: str = "summarization/scenarios"):
        self.scenarios_dir = Path(scenarios_dir)
        self.scenarios: Dict[str, Scenario] = {}
        self._load_scenarios()
    
    def _load_scenarios(self):
        for scenario_file in self.scenarios_dir.glob("*.yaml"):
            with open(scenario_file, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                sections = [Section(**section) for section in data['sections']]
                scenario = Scenario(
                    name=data['name'],
                    system_context=data['system_context'],
                    sections=sections
                )
                self.scenarios[scenario_file.stem] = scenario
    
    def get_scenario(self, scenario_type: str) -> Scenario:
        if scenario_type not in self.scenarios:
            raise ValueError(f"Unknown scenario type: {scenario_type}")
        return self.scenarios[scenario_type] 