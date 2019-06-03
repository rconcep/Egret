import json
import os
import math
from datetime import datetime
from typing import List, Dict, Union, Tuple
from enum import Enum

from pydantic import Schema, BaseModel, Json, validator, ValidationError
from pydantic.dataclasses import dataclass

current_dir = os.path.dirname(os.path.abspath(__file__))


class NumericQuantity(BaseModel):
    """Numeric quantity with a specified unit."""
    value: Union[int, float] = None
    units: str


class TimeSeries(BaseModel):
    """Time series dictionary-like objects."""
    data_type: str = 'time_series'
    values: Dict[Union[int, datetime], float] = None
    units: str


class CostCurveType(str, Enum):
    """Cost curve type."""
    piecewise = 'piecewise'
    polynomial = 'polynomial'


class CostCurve(BaseModel):
    """Cost curve dictionary-like objects."""
    data_type: str = 'cost_curve'
    cost_curve_type: CostCurveType
    values: Union[Dict[str, float], List]

    # @validator('values')
    # def values_match_cost_curve_type(cls, v, values, **kwargs):
    #     if 'values' in values and values['values']:
    #         print(values['cost_curve_type'])
    #     return v



class Bus(BaseModel):
    """Bus."""
    matpower_bustype: str = None
    base_kv: float = None
    v_min: float = None
    v_max: float = None

    vm: TimeSeries = None
    va: TimeSeries = None
    p_balance_violation: TimeSeries = None
    q_balance_violation: TimeSeries = None
    lmp: TimeSeries = None
    q_lmp: TimeSeries = None


class Load(BaseModel):
    """Load."""
    bus: Union[int, str] = None
    area: Union[int, str] = None
    zone: Union[int, str] = None
    owner: Union[int, str] = None
    in_service: bool = None

    p_load: TimeSeries = None
    q_load: TimeSeries = None
    p_load_shed: TimeSeries = None
    q_load_shed: TimeSeries = None


class FuelSupply(BaseModel):
    pass


class Generator(BaseModel):
    """Generator."""
    p_min: Union[NumericQuantity, TimeSeries] = None
    p_max: Union[NumericQuantity, TimeSeries] = None
    power_factor: float = None
    in_service: bool = None
    fuel: str
    bus: Union[int, str]
    area: Union[int, str] = None
    zone: Union[int, str] = None
    owner: Union[int, str] = None

    q_min: float = None
    q_max: float = None
    p_cost: CostCurve = None
    q_cost: CostCurve = None
    startup_cost: List[Tuple[int, float]] = None
    shutdown_cost: NumericQuantity = None
    startup_capacity: NumericQuantity = None
    shutdown_capacity: NumericQuantity = None
    ramp_up_60min: float = None
    ramp_down_60min: float = None
    min_up_time: Union[float, int] = None
    min_down_time: Union[float, int] = None
    initial_status: Union[float, int] = None
    initial_p_output: NumericQuantity = None
    initial_q_output: float = None
    pg: Union[float, TimeSeries] = None
    qg: Union[float, TimeSeries] = None
    rg: Union[float, TimeSeries] = None
    fast_start: bool = None
    supplemental_start: bool = None
    agc_capable: bool = None
    ramp_agc: float = None
    p_min_agc: float = None
    p_max_agc: float = None
    agc_fixed_cost: float = None
    agc_marginal_cost: float = None
    spinning_cost: float = None
    spinning_capacity: float = None
    non_spinning_cost: float = None
    non_spinning_capacity: float = None
    supplemental_cost: float = None
    supplemental_spinning_capacity: float = None
    supplemental_non_spinning_capacity: float = None
    reg_provider: Union[float, TimeSeries] = None
    reg_up_supplied: Union[float, TimeSeries] = None
    reg_down_supplied: Union[float, TimeSeries] = None
    spinning_supplied: Union[float, TimeSeries] = None
    flex_up_supplied: Union[float, TimeSeries] = None
    flex_down_supplied: Union[float, TimeSeries] = None
    non_spinning_supplied: Union[float, TimeSeries] = None
    supplemental_supplied: Union[float, TimeSeries] = None
    fixed_commitment: Union[int, TimeSeries] = None
    fixed_regulation: Union[int, TimeSeries] = None
    commitment: Union[float, TimeSeries] = None
    commitment_cost: Union[float, TimeSeries] = None
    production_cost: Union[float, TimeSeries] = None

    @validator('initial_status')
    def initial_status_cannot_be_zero(cls, v):
        if math.isclose(0, v):
            raise ValueError('The number of time periods the generator has been or off initially cannot be zero.')
        return v

    @validator('power_factor')
    def power_factor_range(cls, v):
        if not (v >= -1 and v <= 1):
            raise ValueError('The power factor must be in the range [-1, 1].')
        return v


class ElementsDataModel(BaseModel):
    
    bus       : Dict[str, Bus] = None
    load      : Dict[str, Load] = None
    branch    : Dict[str, dict] = None # TBD
    interface : dict = None # TBD
    zone      : dict = None # TBD
    generator : Dict[str, Generator] = None 
    storage   : dict = None # TBD
    area      : dict = None # TBD
    fuel_supply: Dict[str, FuelSupply] = None

class SystemDataModel(BaseModel):

    time_indices : List[int] = None

    time_period_length_minutes : NumericQuantity

    baseMVA             : NumericQuantity
    reference_bus       : str = None
    reference_bus_angle : float = None

    load_mismatch_cost     : NumericQuantity = None
    reserve_shortfall_cost : NumericQuantity = None
    total_cost             : NumericQuantity = None

    reserve_requirement              : TimeSeries = None
    spinning_reserve_requirement     : TimeSeries = None
    non_spinning_reserve_requirement : TimeSeries = None
    regulation_up_requirement        : TimeSeries = None
    regulation_down_requirement      : TimeSeries = None
    flexible_ramp_up_requirement     : TimeSeries = None
    flexible_ramp_down_requirement   : TimeSeries = None
    supplmental_reserve_requirement  : TimeSeries = None

    reserve_shortfall                : TimeSeries = None
    spinning_reserve_shortfall       : TimeSeries = None
    non_spinning_reserve_shortfall   : TimeSeries = None
    regulation_up_shortfall          : TimeSeries = None
    regulation_down_shortfall        : TimeSeries = None
    flexible_ramp_up_shortfall       : TimeSeries = None
    flexible_ramp_down_shortfall     : TimeSeries = None
    supplemental_shortfall           : TimeSeries = None

    @validator('time_period_length_minutes')
    def time_period_length_minutes_units(cls, v):
        if v.units != 'min':
            raise ValueError('time_period_length_minutes must have units of min.')
    
    @validator('load_mismatch_cost')
    def load_mismatch_cost_units(cls, v):
        if v.units != '$':
            raise ValueError('load_mismatch_cost must have units of $.')
    
    @validator('reserve_shortfall_cost')
    def reserve_shortfall_cost_units(cls, v):
        if v.units != '$':
            raise ValueError('reserve_shortfall_cost must have units of $.')

    @validator('baseMVA')
    def baseMVA_units(cls, v):
        if v.units != 'MVA':
            raise ValueError('baseMVA must have units of MVA.')
    
    @validator('total_cost')
    def total_cost_units(cls, v):
        if v.units != '$':
            raise ValueError('total_cost must have units of $.')
    
class UnitCommitmentDataModel(BaseModel):

    elements : ElementsDataModel
    system   : SystemDataModel

print("")
print("")
print("SCHEMA IS...")
print(UnitCommitmentDataModel.schema_json(indent=2))

input_json_file_name = os.path.join(current_dir, 'uc_test_instances', 'schema_demo_tiny_uc_2.json')
input_json = json.load(open(input_json_file_name, 'r'))
print(input_json_file_name)

print("")
print("")
print("CALLING VALIDATOR...")
try:
    uc_data = UnitCommitmentDataModel(elements = input_json["elements"],
                                    system = input_json["system"])
except ValidationError as e:
    print(e)
else:
    print("SUCCESS!")

# input_json_file_name = os.path.join(current_dir, 'uc_test_instances', 'test_case_1.json')
# input_json = json.load(open(input_json_file_name, 'r'))
# print(input_json_file_name)

# print("")
# print("")
# print("CALLING VALIDATOR...")
# try:
#     uc_data = UnitCommitmentSolutionDataModel(elements = input_json["elements"],
#                                               system = input_json["system"])
# except ValidationError as e:
#     print(e)
# else:
#     print("SUCCESS!")