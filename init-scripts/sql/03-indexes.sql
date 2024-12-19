-- 03-indexes.sql

-- User-related indexes
-- These indexes improve lookup performance for user authentication and verification
CREATE INDEX IF NOT EXISTS ix_users_email ON public.users(email);
CREATE INDEX IF NOT EXISTS ix_users_id ON public.users(id);
CREATE INDEX IF NOT EXISTS idx_verification_token ON public.users(verification_token);

-- Organization-related indexes
-- These improve performance for organization lookups and filtering
CREATE INDEX IF NOT EXISTS ix_organizations_id ON public.organizations(id);
CREATE INDEX IF NOT EXISTS ix_organizations_name ON public.organizations(name);

-- User-Organization relationship indexes
-- These optimize joining users with organizations and role-based queries
CREATE INDEX IF NOT EXISTS idx_user_organizations_role ON public.user_organizations(role);
CREATE INDEX IF NOT EXISTS idx_user_organizations_user_id ON public.user_organizations(user_id);
CREATE INDEX IF NOT EXISTS idx_user_organizations_org_id ON public.user_organizations(organization_id);

-- User roles indexes
-- These improve role-based access control queries
CREATE INDEX IF NOT EXISTS idx_user_roles_user_id ON public.user_roles(user_id);

-- Articles indexes
-- These optimize article searches and filtering
CREATE INDEX IF NOT EXISTS idx_articles_organization_id ON public.articles(organization_id);
CREATE INDEX IF NOT EXISTS idx_articles_date ON public.articles(date);
CREATE INDEX IF NOT EXISTS idx_articles_category ON public.articles(category);
CREATE INDEX IF NOT EXISTS idx_articles_time_period ON public.articles(time_period);

-- Data source connection indexes
-- These improve lookup performance for data source operations
CREATE INDEX IF NOT EXISTS idx_data_source_connections_org_id ON public.data_source_connections(organization_id);

-- Metric definitions indexes
-- These optimize metric lookups and filtering
CREATE INDEX IF NOT EXISTS idx_metric_definitions_conn_id ON public.metric_definitions(connection_id);

-- Interaction history indexes
-- These improve performance for user interaction queries and session management
CREATE INDEX IF NOT EXISTS idx_interaction_history_user_id ON public.interaction_history(user_id);
CREATE INDEX IF NOT EXISTS idx_interaction_history_session_id ON public.interaction_history(session_id);

-- Suggested questions indexes
-- These optimize question retrieval by category
CREATE INDEX IF NOT EXISTS idx_suggested_questions_category ON public.suggested_questions(category);

-- Composite indexes for frequently combined queries
-- These optimize queries that often filter or join on multiple columns
CREATE INDEX IF NOT EXISTS idx_articles_org_date ON public.articles(organization_id, date);
CREATE INDEX IF NOT EXISTS idx_user_org_role ON public.user_organizations(organization_id, user_id, role);
CREATE INDEX IF NOT EXISTS idx_interaction_user_time ON public.interaction_history(user_id, "timestamp");

-- Text search indexes
-- These improve performance for full-text search operations
CREATE INDEX IF NOT EXISTS idx_articles_content_gin ON public.articles USING gin(to_tsvector('english', content));
CREATE INDEX IF NOT EXISTS idx_articles_title_gin ON public.articles USING gin(to_tsvector('english', title));

CREATE INDEX IF NOT EXISTS idx_liked_posts_user_id ON liked_posts(user_id);
CREATE INDEX IF NOT EXISTS idx_liked_posts_article_id ON liked_posts(article_id);
CREATE INDEX IF NOT EXISTS idx_liked_posts_liked_at ON liked_posts(liked_at);