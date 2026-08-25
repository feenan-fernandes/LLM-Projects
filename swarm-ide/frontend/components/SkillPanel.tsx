/**
 * SkillPanel.tsx
 * Displays discovered, installed, and selected skills per task.
 * Connects to /api/skills endpoint which reads from registry.json.
 */
import React, { useEffect, useState } from "react";

interface Skill {
  slug: string;
  name: string;
  full_name: string;
  url: string;
  stars: number;
  score: number;
  status: "discovered" | "installed" | "selected" | "rejected";
}

interface SkillPanelProps {
  taskId: string;
  onApproveInstall: (slug: string) => void;  // triggers human-approval → install
  onSelectSkill: (slug: string) => void;
}

export const SkillPanel: React.FC<SkillPanelProps> = ({
  taskId,
  onApproveInstall,
  onSelectSkill,
}) => {
  const [skills, setSkills] = useState<Skill[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!taskId) return;
    setLoading(true);
    fetch(`/api/skills?task_id=${taskId}`)
      .then((r) => r.json())
      .then((data) => setSkills(data.skills ?? []))
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [taskId]);

  const statusBadge = (status: Skill["status"]) => {
    const map: Record<Skill["status"], string> = {
      discovered: "var(--accent-yellow)",
      installed:  "var(--accent-blue)",
      selected:   "var(--accent-green)",
      rejected:   "var(--accent-red)",
    };
    return (
      <span
        style={{
          fontSize: "0.7rem",
          fontWeight: 600,
          padding: "2px 8px",
          borderRadius: 12,
          border: `1px solid ${map[status]}`,
          color: map[status],
          textTransform: "uppercase",
          letterSpacing: "0.5px",
        }}
      >
        {status}
      </span>
    );
  };

  if (loading) return <div className="skill-panel-loading">Scouting skills...</div>;
  if (!skills.length) return null;

  return (
    <section className="skill-panel" aria-label="Skill Panel">
      <h3 style={{ marginBottom: 12, fontSize: "0.85rem", textTransform: "uppercase", letterSpacing: "1px", color: "var(--text-muted)" }}>
        <i data-lucide="package" className="lucide-sm" style={{ display: "inline-block", verticalAlign: "middle", marginRight: 6 }} />
        Skills
      </h3>
      {skills.map((skill) => (
        <div
          key={skill.slug}
          className="result-card"
          style={{ padding: "14px 16px", marginBottom: 10 }}
        >
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 6 }}>
            <div>
              <div style={{ fontWeight: 600, fontSize: "0.9rem" }}>{skill.name}</div>
              <a href={skill.url} target="_blank" rel="noreferrer" style={{ fontSize: "0.75rem", color: "var(--text-muted)" }}>
                {skill.full_name}
              </a>
            </div>
            {statusBadge(skill.status)}
          </div>

          <div style={{ fontSize: "0.75rem", color: "var(--text-muted)", marginBottom: 10 }}>
            {skill.stars} stars · score {skill.score.toFixed(1)}
          </div>

          {skill.status === "discovered" && (
            <button
              onClick={() => onApproveInstall(skill.slug)}
              style={{
                padding: "6px 12px", borderRadius: 8, border: "1px solid var(--accent-blue)",
                background: "rgba(59,130,246,0.1)", color: "var(--accent-blue)",
                cursor: "pointer", fontSize: "0.8rem", fontWeight: 500,
              }}
            >
              Approve &amp; Install
            </button>
          )}

          {skill.status === "installed" && (
            <button
              onClick={() => onSelectSkill(skill.slug)}
              style={{
                padding: "6px 12px", borderRadius: 8, border: "1px solid var(--accent-green)",
                background: "rgba(16,185,129,0.1)", color: "var(--accent-green)",
                cursor: "pointer", fontSize: "0.8rem", fontWeight: 500,
              }}
            >
              Use This Skill
            </button>
          )}
        </div>
      ))}
    </section>
  );
};

export default SkillPanel;
