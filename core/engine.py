"""Main synthetic data generation engine."""

from typing import List, Dict, Any
from .schema import FieldSchema
from .generators import (
    IntegerGenerator, FloatGenerator, StringGenerator, EmailGenerator,
    PhoneGenerator, DateGenerator, DateTimeGenerator, BooleanGenerator,
    UUIDGenerator, NameGenerator, AddressGenerator, CityGenerator,
    CountryGenerator, CompanyGenerator, URLGenerator, CategoryGenerator,
    CallDurationGenerator, WaitTimeGenerator, HoldTimeGenerator,
    CallTypeGenerator, CallChannelGenerator, CallDepartmentGenerator,
    AgentIdGenerator, CallPriorityGenerator, CallOutcomeGenerator,
    ResolutionStatusGenerator, SentimentGenerator, CSATScoreGenerator,
    NPSScoreGenerator, AgeGenerator, GenderGenerator, EthnicityGenerator,
    MaritalStatusGenerator, EducationLevelGenerator, EmploymentStatusGenerator,
    IncomeBracketGenerator, HouseholdSizeGenerator, LanguagePreferenceGenerator,
    GenerationGenerator,
)


class SyntheticDataEngine:
    """Core engine for generating synthetic data."""

    GENERATOR_MAP = {
        'integer': IntegerGenerator,
        'float': FloatGenerator,
        'string': StringGenerator,
        'email': EmailGenerator,
        'phone': PhoneGenerator,
        'date': DateGenerator,
        'datetime': DateTimeGenerator,
        'boolean': BooleanGenerator,
        'uuid': UUIDGenerator,
        'name': NameGenerator,
        'address': AddressGenerator,
        'city': CityGenerator,
        'country': CountryGenerator,
        'company': CompanyGenerator,
        'url': URLGenerator,
        'category': CategoryGenerator,
        # Call center metrics
        'call_duration': CallDurationGenerator,
        'wait_time': WaitTimeGenerator,
        'hold_time': HoldTimeGenerator,
        'call_type': CallTypeGenerator,
        'call_channel': CallChannelGenerator,
        'call_department': CallDepartmentGenerator,
        'agent_id': AgentIdGenerator,
        'call_priority': CallPriorityGenerator,
        'call_outcome': CallOutcomeGenerator,
        'resolution_status': ResolutionStatusGenerator,
        'sentiment': SentimentGenerator,
        'csat_score': CSATScoreGenerator,
        'nps_score': NPSScoreGenerator,
        # Demographics
        'age': AgeGenerator,
        'gender': GenderGenerator,
        'ethnicity': EthnicityGenerator,
        'marital_status': MaritalStatusGenerator,
        'education_level': EducationLevelGenerator,
        'employment_status': EmploymentStatusGenerator,
        'income_bracket': IncomeBracketGenerator,
        'household_size': HouseholdSizeGenerator,
        'language_preference': LanguagePreferenceGenerator,
        'generation': GenerationGenerator,
    }

    def __init__(self, fields: List[FieldSchema]):
        """Initialize engine with field schemas."""
        self.fields = fields
        self.generators = {}

        for field_schema in fields:
            field_schema.validate()
            generator_class = self.GENERATOR_MAP.get(field_schema.field_type)
            if not generator_class:
                raise ValueError(f"No generator found for type: {field_schema.field_type}")
            self.generators[field_schema.name] = generator_class(field_schema.constraints)

    def generate_row(self) -> Dict[str, Any]:
        """Generate a single row of data."""
        row = {}
        for field_schema in self.fields:
            generator = self.generators[field_schema.name]
            row[field_schema.name] = generator.generate()
        return row

    def generate(self, num_rows: int) -> List[Dict[str, Any]]:
        """Generate multiple rows of synthetic data."""
        if num_rows < 1:
            raise ValueError("Number of rows must be at least 1")

        return [self.generate_row() for _ in range(num_rows)]

    @classmethod
    def from_config(cls, config: Dict[str, Any]) -> 'SyntheticDataEngine':
        """Create engine from configuration dictionary."""
        fields = [FieldSchema.from_dict(f) for f in config.get('fields', [])]
        return cls(fields)
