"use client";

import { useMemo, useState } from "react";
import {
  Activity,
  Approval,
  Memory,
  Workspace,
  approveOutput,
  createWorkspace,
  listActivities,
  listApprovals,
  listMemories,
  runCustomerIssueDemo
} from "@/lib/api";

export default function Dashboard() {
  const [workspaceName, setWorkspaceName] = useState("Demo Company");
  const [workspaceDescription, setWorkspaceDescription] = useState("AI Context OS demo workspace");
  const [workspace, setWorkspace] = useState<Workspace | null>(null);
  const [customerName, setCustomerName] = useState("Acme SaaS");
  const [issue, setIssue] = useState(
    "Users report that dashboard settings disappear after refreshing the page."
  );
  const [memories, setMemories] = useState<Memory[]>([]);
  const [activities, setActivities] = useState<Activity[]>([]);
  const [approvals, setApprovals] = useState<Approval[]>([]);
  const [taskStatus, setTaskStatus] = useState("not started");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const pendingApproval = useMemo(
    () => approvals.find((approval) => approval.status === "pending"),
    [approvals]
  );

  async function refresh(workspaceId = workspace?.id) {
    if (!workspaceId) return;
    const [nextMemories, nextActivities, nextApprovals] = await Promise.all([
      listMemories(workspaceId),
      listActivities(workspaceId),
      listApprovals(workspaceId)
    ]);
    setMemories(nextMemories);
    setActivities(nextActivities);
    setApprovals(nextApprovals);
  }

  async function handleCreateWorkspace() {
    setLoading(true);
    setError(null);
    try {
      const created = await createWorkspace(workspaceName, workspaceDescription);
      setWorkspace(created);
      setTaskStatus("workspace ready");
      await refresh(created.id);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not create workspace");
    } finally {
      setLoading(false);
    }
  }

  async function handleRunWorkflow() {
    if (!workspace) {
      setError("Create a workspace first.");
      return;
    }

    setLoading(true);
    setError(null);
    try {
      const result = await runCustomerIssueDemo(workspace.id, customerName, issue);
      setTaskStatus(result.task.status);
      await refresh(workspace.id);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not run workflow");
    } finally {
      setLoading(false);
    }
  }

  async function handleApprove() {
    if (!pendingApproval || !workspace) return;

    setLoading(true);
    setError(null);
    try {
      await approveOutput(pendingApproval.id, "Ayush");
      await refresh(workspace.id);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not approve output");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="shell">
      <header className="topbar">
        <div className="topbar-inner">
          <div className="brand">
            <h1>AI Context Operating System</h1>
            <p>Shared memory, workflow continuity, and approval control for agents.</p>
          </div>
          <button className="secondary" onClick={() => workspace && refresh()} disabled={!workspace || loading}>
            Refresh
          </button>
        </div>
      </header>

      <div className="content">
        <section className="stack">
          <div className="panel">
            <div className="panel-header">
              <h2 className="panel-title">Workspace</h2>
            </div>
            <div className="panel-body">
              <div className="field">
                <label>Name</label>
                <input value={workspaceName} onChange={(event) => setWorkspaceName(event.target.value)} />
              </div>
              <div className="field">
                <label>Description</label>
                <input
                  value={workspaceDescription}
                  onChange={(event) => setWorkspaceDescription(event.target.value)}
                />
              </div>
              <button onClick={handleCreateWorkspace} disabled={loading}>
                Create Workspace
              </button>
              {workspace ? <p className="muted">Active workspace: {workspace.id}</p> : null}
            </div>
          </div>

          <div className="panel">
            <div className="panel-header">
              <h2 className="panel-title">Customer Issue</h2>
            </div>
            <div className="panel-body">
              <div className="field">
                <label>Customer</label>
                <input value={customerName} onChange={(event) => setCustomerName(event.target.value)} />
              </div>
              <div className="field">
                <label>Issue</label>
                <textarea value={issue} onChange={(event) => setIssue(event.target.value)} />
              </div>
              <button onClick={handleRunWorkflow} disabled={loading || !workspace}>
                Run Agent Workflow
              </button>
              {error ? <div className="error">{error}</div> : null}
            </div>
          </div>
        </section>

        <section className="stack">
          <div className="grid">
            <div className="metric">
              <strong>{taskStatus}</strong>
              <span>Task status</span>
            </div>
            <div className="metric">
              <strong>{memories.length}</strong>
              <span>Shared memories</span>
            </div>
            <div className="metric">
              <strong>{activities.length}</strong>
              <span>Timeline events</span>
            </div>
          </div>

          <div className="columns">
            <div className="panel">
              <div className="panel-header">
                <h2 className="panel-title">Activity Timeline</h2>
              </div>
              <div className="panel-body">
                {activities.length === 0 ? <p className="muted">Run the workflow to see agent actions.</p> : null}
                {activities.map((activity) => (
                  <article className="item" key={activity.id}>
                    <h3>{activity.action_type}</h3>
                    <p>{activity.output_summary || activity.input_summary || activity.status}</p>
                  </article>
                ))}
              </div>
            </div>

            <div className="stack">
              <div className="panel">
                <div className="panel-header">
                  <h2 className="panel-title">Pending Approval</h2>
                  {pendingApproval ? <span className="badge">{pendingApproval.status}</span> : null}
                </div>
                <div className="panel-body">
                  {pendingApproval ? (
                    <>
                      <div className="item">
                        <h3>{pendingApproval.title}</h3>
                        <p>{pendingApproval.content}</p>
                      </div>
                      <button onClick={handleApprove} disabled={loading}>
                        Approve as Ayush
                      </button>
                    </>
                  ) : (
                    <p className="muted">No pending approval.</p>
                  )}
                </div>
              </div>

              <div className="panel">
                <div className="panel-header">
                  <h2 className="panel-title">Shared Memory</h2>
                </div>
                <div className="panel-body">
                  {memories.length === 0 ? <p className="muted">Memories appear after agent work.</p> : null}
                  {memories.map((memory) => (
                    <article className="item" key={memory.id}>
                      <h3>{memory.title}</h3>
                      <p>{memory.content}</p>
                    </article>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </section>
      </div>
    </main>
  );
}
