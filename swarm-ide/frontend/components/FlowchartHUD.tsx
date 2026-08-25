/**
 * FlowchartHUD.tsx
 * Live architecture tracker. Reads governance events from a server-sent-event
 * stream and lights up each node in the pipeline as it becomes active.
 *
 * Nodes: Prompt → Router → Orchestrator → Sandbox → Validation
 */
import React, { useEffect, useState } from "react";

type NodeState = "idle" | "active" | "success" | "error";

interface FlowNode {
  id: string;
  label: string;
  icon: string; // Lucide icon name
}

const NODES: FlowNode[] = [
  { id: "prompt",       label: "Prompt",       icon: "message-square" },
  { id: "router",       label: "Router",        icon: "git-branch"     },
  { id: "orchestrator", label: "Orchestrator",  icon: "brain-circuit"  },
  { id: "sandbox",      label: "Sandbox",       icon: "box"            },
  { id: "validation",   label: "Validation",    icon: "check-circle"   },
];

interface FlowchartHUDProps {
  activeNodeId: string | null;  // id of the currently active node
  errorNodeId?: string | null;
  successNodeId?: string | null;
}

export const FlowchartHUD: React.FC<FlowchartHUDProps> = ({
  activeNodeId,
  errorNodeId,
  successNodeId,
}) => {
  const getState = (id: string): NodeState => {
    if (id === errorNodeId)   return "error";
    if (id === successNodeId) return "success";
    if (id === activeNodeId)  return "active";
    return "idle";
  };

  const nodeClass = (state: NodeState) => {
    const base = "flow-node";
    if (state === "active")  return `${base} active`;
    if (state === "error")   return `${base} error`;
    if (state === "success") return `${base} success`;
    return base;
  };

  return (
    <div className="hud-flow" aria-label="Live Architecture Tracker">
      {NODES.map((node, i) => (
        <React.Fragment key={node.id}>
          <div className={nodeClass(getState(node.id))} id={`fn-${node.id}`}>
            {/* Lucide icon rendered via <i data-lucide="..."> in parent app */}
            <i data-lucide={node.icon} className="lucide-sm" />
            {node.label}
          </div>
          {i < NODES.length - 1 && (
            <div className="flow-arrow">
              <i data-lucide="arrow-right" className="lucide-sm" />
            </div>
          )}
        </React.Fragment>
      ))}
    </div>
  );
};

export default FlowchartHUD;
