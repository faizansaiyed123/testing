export type MembershipRole = "owner" | "admin" | "member";

export type User = {
  id: string;
  email: string;
  full_name: string;
  is_active: boolean;
  memberships: { organization_id: string; role: MembershipRole }[];
};

export type AuthResponse = {
  access_token: string;
  token_type: string;
  user: User;
};

export type Contact = {
  id: string;
  organization_id: string;
  company_id: string | null;
  owner_user_id: string;
  first_name: string;
  last_name: string;
  email: string | null;
  phone: string | null;
  job_title: string | null;
  lifecycle: "lead" | "prospect" | "customer" | "churned";
};

export type ContactList = {
  items: Contact[];
  page: number;
  page_size: number;
  total: number;
};

export type Company = {
  id: string;
  organization_id: string;
  owner_user_id: string;
  name: string;
  website: string | null;
  phone: string | null;
};

export type CompanyList = {
  items: Company[];
  page: number;
  page_size: number;
  total: number;
};

export type Opportunity = {
  id: string;
  organization_id: string;
  owner_user_id: string;
  company_id: string | null;
  contact_id: string | null;
  stage_id: string;
  name: string;
  amount: string | null;
  status: "open" | "won" | "lost";
  expected_close_date: string | null;
  lost_reason: string | null;
};

export type OpportunityList = {
  items: Opportunity[];
  page: number;
  page_size: number;
  total: number;
};

export type AttentionItem = {
  entity_type: "task" | "opportunity" | "contact";
  entity_id: string;
  priority: number;
  title: string;
  reason: string;
  due_at: string | null;
  last_activity_at: string | null;
};

export type AttentionResponse = {
  items: AttentionItem[];
  generated_at: string;
};

export type RelationshipHealth = {
  contact_id: string;
  score: number;
  band: "healthy" | "warming" | "at_risk" | "dormant";
  last_activity_at: string | null;
  activity_count_30d: number;
  open_opportunity_count: number;
  overdue_task_count: number;
  evidence: { code: string; impact: number; description: string }[];
};

export type SavedView = {
  id: string;
  organization_id: string;
  created_by_user_id: string;
  resource: "contacts";
  name: string;
  shared: boolean;
  definition_version: number;
  definition: {
    query: string | null;
    lifecycle: ("lead" | "prospect" | "customer" | "churned")[];
    company_id: string | null;
    owner_user_id: string | null;
    has_email: boolean | null;
    sort: "updated_desc" | "updated_asc" | "name_asc" | "name_desc";
  };
};

export type ImportPreview = {
  id: string;
  status: string;
  filename: string;
  total_rows: number;
  valid_rows: number;
  invalid_rows: number;
  committed_rows: number;
  created_at: string;
  completed_at: string | null;
  errors: { row_number: number; errors: string[] }[];
  errors_truncated: boolean;
};

export type ImportCommitResponse = {
  job_id: string;
  status: string;
  dry_run: boolean;
  total_rows: number;
  valid_rows: number;
  invalid_rows: number;
  would_create: number;
  committed_rows: number;
};
