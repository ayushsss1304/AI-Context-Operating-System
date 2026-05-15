export const API_BASE = process.env.NEXT_PUBLIC_API_BASE ?? "http://127.0.0.1:8000";

export type Workspace = {
  id: string;
  name: string;
  description?: string | null;
};

export type Memory = {
  id: string;
  title: string;
  content: string;
  memory_type: string;
  tags: string[];
};

export type Activity = {
  id: string;
  action_type: string;
  input_summary?: string | null;
  output_summary?: string | null;
  status: string;
  created_at: string;
};

export type Approval = {
  id: string;
  title: string;
  content: string;
  status: string;
  reviewed_by?: string | null;
};

export type WorkflowResult = {
  task: {
    id: string;
    title: string;
    status: string;
  };
  memories: Memory[];
  activities: Activity[];
  approval: Approval;
};

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers ?? {})
    }
  });

  if (!response.ok) {
    const detail = await response.text();
    throw new Error(detail || `Request failed with ${response.status}`);
  }

  return response.json() as Promise<T>;
}

export function createWorkspace(name: string, description: string) {
  return request<Workspace>("/workspaces", {
    method: "POST",
    body: JSON.stringify({ name, description })
  });
}

export function runCustomerIssueDemo(workspaceId: string, customerName: string, issue: string) {
  return request<WorkflowResult>("/workflows/customer-issue-demo", {
    method: "POST",
    body: JSON.stringify({
      workspace_id: workspaceId,
      customer_name: customerName,
      issue
    })
  });
}

export function listMemories(workspaceId: string) {
  return request<Memory[]>(`/memories?workspace_id=${workspaceId}`);
}

export function listActivities(workspaceId: string) {
  return request<Activity[]>(`/activities?workspace_id=${workspaceId}`);
}

export function listApprovals(workspaceId: string) {
  return request<Approval[]>(`/approvals?workspace_id=${workspaceId}`);
}

export function approveOutput(approvalId: string, reviewedBy: string) {
  return request<Approval>(`/approvals/${approvalId}/approve`, {
    method: "POST",
    body: JSON.stringify({ reviewed_by: reviewedBy })
  });
}
