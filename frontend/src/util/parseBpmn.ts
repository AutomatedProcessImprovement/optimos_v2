import {
  ModelTask,
  Gateway as Gateway_,
  IntermediateCatchEvent,
} from "../types/bpmn_types";

import type { Gateway, Task } from "bpmn-moddle";
import * as BpmnModdle from "bpmn-moddle";

export async function parseBpmn(xmlStr: string) {
  let tasks: ModelTask[];
  let gateways: Gateway_[];
  let catchEvents: IntermediateCatchEvent[];

  const moddle = new BpmnModdle();
  const { elementsById, references, rootElement, warnings }: any =
    await moddle.fromXML(xmlStr);
  console.log("warnings", warnings);
  const process = rootElement?.rootElements?.find(
    (e: { $type: string }) => e.$type === "bpmn:Process"
  );

  tasks = process?.flowElements
    ?.filter((e: { $type: string }) => e.$type === "bpmn:Task")
    .reduce((acc: [], task: Task) => {
      return [
        ...acc,
        {
          id: task.id,
          name: task.name,
        },
      ];
    }, [] as ModelTask[]);

  gateways = process?.flowElements
    ?.filter(
      (e: Gateway) =>
        (e.$type === "bpmn:ExclusiveGateway" ||
          e.$type === "bpmn:InclusiveGateway") &&
        (e.gatewayDirection === "Diverging" || e.gatewayDirection === "Mixed")
    )
    .reduce((acc: [], current: Gateway) => {
      const targets = references
        .filter(
          (r: any) => r.id === current.id && r.property === "bpmn:sourceRef"
        )
        .map((r: any) => r.element.targetRef);

      return [
        ...acc,
        {
          id: current.id,
          name: current.name,
          outgoingFlows: targets,
        },
      ];
    }, [] as Gateway_[]);

  catchEvents = process?.flowElements
    ?.filter(
      (e: { $type: string }) => e.$type === "bpmn:IntermediateCatchEvent"
    )
    .reduce((acc: [], t: any) => {
      return [
        ...acc,
        {
          id: t.id,
          name: t.name,
        },
      ];
    }, [] as IntermediateCatchEvent[]);

  return { xmlStr, tasks, gateways, catchEvents };
}
