import { TimetableType } from "../redux/slices/optimosApi";
import { parseBpmn } from "../util/parseBpmn";

export const validateBPMN = async (bpmn: string, simParams: TimetableType) => {
  const { tasks, gateways, catchEvents } = await parseBpmn(bpmn);

  // Ensure all tasks have a task_resource_distribution
  const taskIds = tasks.map((task) => task.id);
  const taskResourceDistributions = simParams.task_resource_distribution.map(
    (taskResource) => taskResource.task_id
  );
  const missingTaskResourceDistributions = taskIds.filter(
    (taskId) => !taskResourceDistributions.includes(taskId)
  );
  if (missingTaskResourceDistributions.length > 0) {
    throw new Error(
      `The following tasks are missing a task_resource_distribution: ${missingTaskResourceDistributions.join(
        ", "
      )}`
    );
  }

  // Ensure all gateways have a gateway_branching_probability
  const gatewayIds = gateways.map((gateway) => gateway.id);
  const gatewayBranchingProbabilities =
    simParams.gateway_branching_probabilities.map(
      (gatewayBranchingProbability) => gatewayBranchingProbability.gateway_id
    );
  const missingGatewayBranchingProbabilities = gatewayIds.filter(
    (gatewayId) => !gatewayBranchingProbabilities.includes(gatewayId)
  );
  if (missingGatewayBranchingProbabilities.length > 0) {
    throw new Error(
      `The following gateways are missing a gateway_branching_probability: ${missingGatewayBranchingProbabilities.join(
        ", "
      )}`
    );
  }

  // Ensure all catch events have an event_distribution
  const catchEventIds = catchEvents.map((catchEvent) => catchEvent.id);
  const eventDistributions = Object.keys(simParams.event_distribution);
  const missingEventDistributions = catchEventIds.filter(
    (catchEventId) => !eventDistributions.includes(catchEventId)
  );
  if (missingEventDistributions.length > 0) {
    throw new Error(
      `The following catch events are missing an event_distribution: ${missingEventDistributions.join(
        ", "
      )}`
    );
  }
};
