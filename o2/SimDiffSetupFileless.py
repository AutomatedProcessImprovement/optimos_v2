import datetime
import io
from typing import TYPE_CHECKING

import pytz
from bpdfr_simulation_engine.batch_processing_parser import BatchProcessingParser
from bpdfr_simulation_engine.case_attributes import AllCaseAttributes
from bpdfr_simulation_engine.prioritisation import AllPriorityRules
from bpdfr_simulation_engine.prioritisation_parser import PrioritisationParser
from bpdfr_simulation_engine.simulation_properties_parser import (
    BATCH_PROCESSING_SECTION,
    CASE_ATTRIBUTES_SECTION,
    EVENT_DISTRIBUTION_SECTION,
    PRIORITISATION_RULES_SECTION,
    RESOURCE_CALENDARS,
    parse_arrival_branching_probabilities,
    parse_arrival_calendar,
    parse_case_attr,
    parse_event_distribution,
    parse_resource_calendars,
    parse_resource_profiles,
    parse_task_resource_distributions,
)
from bpdfr_simulation_engine.simulation_setup import (
    SimDiffSetup,
    parse_simulation_model,
)

if TYPE_CHECKING:
    from o2.types.timetable import TimetableType


class SimDiffSetupFileless(SimDiffSetup):
    def __init__(
        self,
        process_name,
        bpmn: str,
        timetable: "TimetableType",
        is_event_added_to_log,
        total_cases,
    ):
        self.process_name = process_name
        self.start_datetime = datetime.datetime.now(pytz.utc)

        bpmn_file = io.StringIO()
        bpmn_file.write(bpmn)
        bpmn_file.seek(0)

        (
            self.resources_map,
            self.calendars_map,
            self.element_probability,
            self.task_resource,
            self.arrival_calendar,
            self.event_distibution,
            self.batch_processing,
            self.case_attributes,
            self.prioritisation_rules,
        ) = self.parse_json_sim_parameters_from_string(timetable.to_dict())

        self.bpmn_graph = parse_simulation_model(bpmn_file)
        self.bpmn_graph.set_additional_fields_from_json(
            self.element_probability,
            self.task_resource,
            self.event_distibution,
            self.batch_processing,
        )
        if not self.arrival_calendar:
            self.arrival_calendar = self.find_arrival_calendar()

        self.is_event_added_to_log = is_event_added_to_log
        self.total_num_cases = total_cases  # how many process cases should be simulated

    def parse_json_sim_parameters_from_string(self, json_data):
        resources_map, res_pool = parse_resource_profiles(
            json_data["resource_profiles"]
        )
        calendars_map = parse_resource_calendars(json_data[RESOURCE_CALENDARS])
        task_resource_distribution = parse_task_resource_distributions(
            json_data["task_resource_distribution"], res_pool
        )

        element_distribution = parse_arrival_branching_probabilities(
            json_data["arrival_time_distribution"],
            json_data["gateway_branching_probabilities"],
        )
        arrival_calendar = parse_arrival_calendar(json_data)
        event_distibution = (
            parse_event_distribution(json_data[EVENT_DISTRIBUTION_SECTION])
            if EVENT_DISTRIBUTION_SECTION in json_data
            else dict()
        )
        batch_processing = (
            BatchProcessingParser(json_data[BATCH_PROCESSING_SECTION]).parse()
            if BATCH_PROCESSING_SECTION in json_data
            else dict()
        )
        case_attributes = (
            parse_case_attr(json_data[CASE_ATTRIBUTES_SECTION])
            if CASE_ATTRIBUTES_SECTION in json_data
            else AllCaseAttributes([])
        )
        prioritisation_rules = (
            PrioritisationParser(json_data[PRIORITISATION_RULES_SECTION]).parse()
            if PRIORITISATION_RULES_SECTION in json_data
            else AllPriorityRules([])
        )

        return (
            resources_map,
            calendars_map,
            element_distribution,
            task_resource_distribution,
            arrival_calendar,
            event_distibution,
            batch_processing,
            case_attributes,
            prioritisation_rules,
        )
