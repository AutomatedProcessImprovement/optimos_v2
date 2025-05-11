# cspell:disable
import datetime
import io

import pytz
from prosimos.all_attributes import AllAttributes
from prosimos.batch_processing_parser import BatchProcessingParser
from prosimos.branch_condition_parser import BranchConditionParser
from prosimos.branch_condition_rules import AllBranchConditionRules
from prosimos.case_attributes import AllCaseAttributes
from prosimos.event_attributes import AllEventAttributes
from prosimos.event_attributes_parser import EventAttributesParser
from prosimos.global_attributes import AllGlobalAttributes
from prosimos.global_attributes_parser import GlobalAttributesParser
from prosimos.prioritisation import AllPriorityRules
from prosimos.prioritisation_parser import PrioritisationParser
from prosimos.simulation_properties_parser import (
    BATCH_PROCESSING_SECTION,
    BRANCH_RULES,
    CASE_ATTRIBUTES_SECTION,
    DEFAULT_GATEWAY_EXECUTION_LIMIT,
    EVENT_ATTRIBUTES,
    EVENT_DISTRIBUTION_SECTION,
    GATEWAY_EXECUTION_LIMIT,
    GLOBAL_ATTRIBUTES,
    MULTITASKING_SECTION,
    PRIORITISATION_RULES_SECTION,
    RESOURCE_CALENDARS,
    add_default_flows,
    parse_arrival_branching_probabilities,
    parse_arrival_calendar,
    parse_case_attr,
    parse_event_distribution,
    parse_fuzzy_calendar,
    parse_gateway_conditions,
    parse_multitasking_model,
    parse_resource_calendars,
    parse_resource_profiles,
    parse_task_resource_distributions,
)
from prosimos.simulation_setup import (
    SimDiffSetup,
    parse_simulation_model,
)

from o2.models.timetable import TimetableType


class SimDiffSetupFileless(SimDiffSetup):
    """A file-less implementation of SimDiffSetup for simulation setup.

    This class extends SimDiffSetup to handle simulation setup without relying on
    physical files, instead using in-memory string representations of BPMN and
    timetable data.
    """

    def __init__(
        self,
        process_name: str,
        bpmn: str,
        timetable: "TimetableType",
        is_event_added_to_log: bool,
        total_cases: int,
    ) -> None:
        """Initialize a SimDiffSetupFileless instance.

        Sets up simulation parameters from in-memory string representations of BPMN and
        timetable data rather than loading from files.
        """
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
            self.prioritisation_rules,
            self.branch_rules,
            self.gateway_conditions,
            self.all_attributes,
            self.gateway_execution_limit,
            self.model_type,
            self.multitask_info,
        ) = self.parse_json_sim_parameters_from_string(timetable.to_dict())
        self.gateway_conditions = add_default_flows(self.gateway_conditions, bpmn_file)
        self.case_attributes = self.all_attributes.case_attributes

        # Reset the file pointer to the beginning of the file
        bpmn_file.seek(0)
        self.bpmn_graph = parse_simulation_model(bpmn_file)
        self.bpmn_graph.set_additional_fields_from_json(
            self.element_probability,
            self.task_resource,
            self.event_distibution,
            self.batch_processing,
            self.gateway_conditions,
            self.gateway_execution_limit,
        )

        if not self.arrival_calendar:
            self.arrival_calendar = self.find_arrival_calendar()

        self.is_event_added_to_log = is_event_added_to_log
        self.total_num_cases = total_cases  # how many process cases should be simulated

    def parse_json_sim_parameters_from_string(self, json_data: dict) -> tuple:
        """Parse simulation parameters from JSON data.

        Extracts various simulation components from a JSON representation of the
        timetable and configuration, such as resources, calendars, task distributions,
        and other simulation properties.
        """
        model_type = json_data.get("model_type", "CRISP")

        resources_map, res_pool = parse_resource_profiles(json_data["resource_profiles"])
        # calendars_map = parse_resource_calendars(json_data[RESOURCE_CALENDARS])

        calendars_map = (
            parse_fuzzy_calendar(json_data)
            if model_type == "FUZZY"
            else parse_resource_calendars(json_data[RESOURCE_CALENDARS])
        )

        task_resource_distribution = parse_task_resource_distributions(
            json_data["task_resource_distribution"], res_pool
        )

        branch_rules = (
            BranchConditionParser(json_data[BRANCH_RULES]).parse()
            if BRANCH_RULES in json_data
            else AllBranchConditionRules([])
        )

        element_distribution = parse_arrival_branching_probabilities(
            json_data["arrival_time_distribution"],
            json_data["gateway_branching_probabilities"],
        )

        gateway_conditions = parse_gateway_conditions(
            json_data["gateway_branching_probabilities"], branch_rules
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
        event_attributes = (
            EventAttributesParser(json_data[EVENT_ATTRIBUTES]).parse()
            if EVENT_ATTRIBUTES in json_data
            else AllEventAttributes({})
        )

        global_attributes = (
            GlobalAttributesParser(json_data[GLOBAL_ATTRIBUTES]).parse()
            if GLOBAL_ATTRIBUTES in json_data
            else AllGlobalAttributes({})
        )

        all_attributes = AllAttributes(global_attributes, case_attributes, event_attributes)

        prioritisation_rules = (
            PrioritisationParser(json_data[PRIORITISATION_RULES_SECTION]).parse()
            if PRIORITISATION_RULES_SECTION in json_data
            else AllPriorityRules([])
        )

        gateway_execution_limit = json_data.get(GATEWAY_EXECUTION_LIMIT, DEFAULT_GATEWAY_EXECUTION_LIMIT)

        multitasking_info = (
            parse_multitasking_model(json_data[MULTITASKING_SECTION], task_resource_distribution)
            if MULTITASKING_SECTION in json_data
            else None
        )

        return (
            resources_map,
            calendars_map,
            element_distribution,
            task_resource_distribution,
            arrival_calendar,
            event_distibution,
            batch_processing,
            prioritisation_rules,
            branch_rules,
            gateway_conditions,
            all_attributes,
            gateway_execution_limit,
            model_type,
            multitasking_info,
        )
