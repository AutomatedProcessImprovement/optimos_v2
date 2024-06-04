from dataclasses import replace
from o2.types.days import DAY
from o2.types.timetable import DISTRIBUTION_TYPE, ArrivalTimeDistribution, DistributionParameter, EventDistribution, GatewayBranchingProbability, Probability, Resource, ResourceCalendar, ResourcePool, TaskResourceDistribution, TaskResourceDistributions, TimePeriod, TimetableType
import xml.etree.ElementTree as ET
import io



class TimeTableGenerator:
    RESOURCE_POOL_ID = "BASE_RESOURCE_POOL"
    RESOURCE_ID = "BASE_RESOURCE"
    CALENDAR_ID = "BASE_CALENDAR"
    GATEWAY_ID = "OR_GATEWAY"


    def __init__(self, bpmn: str):
        fileIo = io.StringIO()
        fileIo.write(bpmn)
        fileIo.seek(0)
        self.bpmn = ET.parse(fileIo)
        self.bpmnRoot = self.bpmn.getroot()
        # Get all the Elements of kind bpmn:task in bpmn:process
        self.tasks = self.bpmnRoot.findall(".//{http://www.omg.org/spec/BPMN/20100524/MODEL}task")
        self.timetable = TimetableType(
            resource_profiles=[],
            arrival_time_distribution=ArrivalTimeDistribution(
                distribution_name=DISTRIBUTION_TYPE.FIXED,
                distribution_params=[
                    DistributionParameter(value=0),
                ]
            ),
            gateway_branching_probabilities=[],
            batch_processing=[],
            arrival_time_calendar=[],
            task_resource_distribution=[],
            resource_calendars=[],
            event_distribution=EventDistribution(),
            total_cases=1000,
            start_time="2000-01-01T00:00:00Z"
        )

    def create_simple_resource_profile(self):
        self.timetable.resource_profiles.append(
         ResourcePool(
             id=self.RESOURCE_POOL_ID,
             name="Base Resource Pool",
                resource_list=[
                    Resource(
                        id=self.RESOURCE_ID,
                        name="Base Resource",
                        calendar="BASE_CALENDAR",
                        cost_per_hour=1,
                        amount=1,
                        assigned_tasks=[
                            task.attrib["id"] for task in self.tasks
                        ]
                    )
                ]
         )
        )

    def create_simple_arrival_time_calendar(self):
        self.timetable.arrival_time_calendar.append(
            TimePeriod(
                from_=DAY.MONDAY,
                to=DAY.SUNDAY,
                beginTime="00:00:00",
                endTime="23:59:59"
            )
        )

    def create_simple_arrival_time_distribution(self):
        self.timetable = replace(
            self.timetable,
            arrival_time_distribution=ArrivalTimeDistribution(
                distribution_name=DISTRIBUTION_TYPE.FIXED,
                distribution_params=[
                    DistributionParameter(value=60), # 8:00
                ]
            )
        )
    
    def create_simple_task_resource_distribution(self):
        self.timetable = replace(self.timetable, task_resource_distribution=[
            TaskResourceDistributions(
                task_id=task.attrib["id"],
                resources=[
                    TaskResourceDistribution(
                        resource_id=self.RESOURCE_ID,
                        distribution_name=DISTRIBUTION_TYPE.FIXED,
                        distribution_params=[
                            DistributionParameter(value=60)
                        ]
                    )
                ]
            ) for task in self.tasks
        ])

    def create_simple_resource_calendars(self):
        self.timetable.resource_calendars.append(
           ResourceCalendar(
                id=self.CALENDAR_ID,
                name="Base Calendar",
                time_periods=[
                     TimePeriod(
                          from_=DAY.MONDAY,
                          to=DAY.SUNDAY,
                          beginTime="00:00:00",
                          endTime="23:59:59"
                     )
                ]
           )
        )

    def create_gateway_branching_probabilities(self):
        self.timetable.gateway_branching_probabilities.append(
            GatewayBranchingProbability(
                gateway_id=self.GATEWAY_ID,
                probabilities=[
                    Probability(
                        path_id='FLOW_OR_JOIN',
                        value=0.9
                    ),
                    Probability(
                        path_id='FLOW_OR_LAST',
                        value=0.1
                    )
                ]
            )
        )
        

    def generate(self):
        self.create_simple_resource_profile()
        self.create_simple_arrival_time_calendar()
        self.create_simple_arrival_time_distribution()
        self.create_simple_task_resource_distribution()
        self.create_simple_resource_calendars()
        self.create_gateway_branching_probabilities()
        return self.timetable
    
