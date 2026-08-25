/**
 * ArtifactCard.tsx
 * Renders a plan or diff from the Orchestrator as a structured, clickable review card.
 * Used before any write or network action that requires human confirmation.
 * Surfaces: plan summaries, unified diffs, skill install confirmations.
 */
import React, { useState } from "react";

type CardVariant = "plan" | "diff" | "skill_install" | "sandbox_alert";

interface ArtifactCardProps {
  id: string;
  variant: CardVariant;
  title: string;
  content: string;          // markdown plan text or unified diff string
  metadata?: Record<string, string | number>;
  onApprove?: (id: string) => void;
  onReject?: (id: string) => void;
  taskId?: string;
}

const VARIANT_COLORS: Record<CardVariant, string> = {
  plan:           "var(--accent-blue)",
  diff:           "var(--accent-yellow)",
  skill_install:  "var(--accent-green)",
  sandbox_alert:  "var(--accent-red)",
};

const VARIANT_ICONS: Record<CardVariant, string> = {
  plan:           "clipboard-list",
  diff:           "file-diff",
  skill_install:  "package-plus",
  sandbox_alert:  "shield-alert",
};

export const ArtifactCard: React.FC<ArtifactCardProps> = ({
  id, variant, title, content, metadata, onApprove, onReject, taskId,
}) => {
  const [expanded, setExpanded] = useState(false);
  const [acted, setActed] = useState<"approved" | "rejected" | null>(null);

  const color = VARIANT_COLORS[variant];
  const icon  = VARIANT_ICONS[variant];

  const handleApprove = () => {
    setActed("approved");
    onApprove?.(id);
  };
  const handleReject = () => {
    setActed("rejected");
    onReject?.(id);
  };

  return (
    <article
      className="result-card"
      style={{
        borderColor: color,
        background: `color-mix(in srgb, ${color} 5%, var(--bg-panel))`,
        marginBottom: 16,
        opacity: acted ? 0.7 : 1,
        transition: "opacity 0.3s",
      }}
      aria-label={`Artifact: ${title}`}
    >
      {/* Header */}
      <header style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 10 }}>
        <i data-lucide={icon} className="lucide" style={{ color }} />
        <h3 style={{ margin: 0, fontSize: "1rem", color }}>{title}</h3>
        {taskId && (
          <span style={{ marginLeft: "auto", fontSize: "0.7rem", color: "var(--text-muted)" }}>
            task: {taskId}
          </span>
        )}
      </header>

      {/* Metadata row */}
      {metadata && Object.keys(metadata).length > 0 && (
        <dl style={{ display: "flex", gap: 16, margin: "0 0 10px", flexWrap: "wrap" }}>
          {Object.entries(metadata).map(([k, v]) => (
            <div key={k}>
              <dt style={{ fontSize: "0.7rem", color: "var(--text-muted)", textTransform: "uppercase" }}>{k}</dt>
              <dd style={{ margin: 0, fontWeight: 600, fontSize: "0.85rem" }}>{v}</dd>
            </div>
          ))}
        </dl>
      )}

      {/* Collapsible content */}
      <details open={expanded} onToggle={(e) => setExpanded((e.target as HTMLDetailsElement).open)}>
        <summary style={{ cursor: "pointer", color: "var(--text-muted)", fontSize: "0.8rem", userSelect: "none" }}>
          {expanded ? "Hide" : "Show"} details
        </summary>
        <pre style={{
          marginTop: 10, padding: 14, borderRadius: 8,
          background: "var(--bg-base)", border: "1px solid var(--border)",
          overflowX: "auto", fontSize: "0.8rem", lineHeight: 1.5,
          whiteSpace: "pre-wrap", wordBreak: "break-all",
        }}>
          {content}
        </pre>
      </details>

      {/* Action buttons */}
      {!acted && (onApprove || onReject) && (
        <footer style={{ display: "flex", gap: 10, marginTop: 14 }}>
          {onApprove && (
            <button
              onClick={handleApprove}
              style={{
                padding: "7px 16px", borderRadius: 8,
                border: `1px solid var(--accent-green)`,
                background: "rgba(16,185,129,0.1)", color: "var(--accent-green)",
                cursor: "pointer", fontWeight: 500, fontSize: "0.85rem",
              }}
            >
              Approve
            </button>
          )}
          {onReject && (
            <button
              onClick={handleReject}
              style={{
                padding: "7px 16px", borderRadius: 8,
                border: "1px solid var(--accent-red)",
                background: "rgba(239,68,68,0.1)", color: "var(--accent-red)",
                cursor: "pointer", fontWeight: 500, fontSize: "0.85rem",
              }}
            >
              Reject
            </button>
          )}
        </footer>
      )}

      {acted && (
        <div style={{ marginTop: 10, fontWeight: 600, fontSize: "0.8rem", color: acted === "approved" ? "var(--accent-green)" : "var(--accent-red)" }}>
          {acted === "approved" ? "Approved — executing..." : "Rejected."}
        </div>
      )}
    </article>
  );
};

export default ArtifactCard;
