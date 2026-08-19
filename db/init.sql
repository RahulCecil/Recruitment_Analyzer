-- 1. DEFINE SCHEMA (Parent tables first, then child tables)

CREATE TABLE candidates (
    candidate_id VARCHAR(50) PRIMARY KEY,
    country VARCHAR(2) NOT NULL,
    years_experience INT NOT NULL CHECK (years_experience >= 0),
    preferred_job_family VARCHAR(50) NOT NULL,
    profile_completeness NUMERIC(3, 2) NOT NULL CHECK (profile_completeness BETWEEN 0.0 AND 1.0)
);

CREATE TABLE jobs (
    job_id VARCHAR(50) PRIMARY KEY,
    country VARCHAR(2) NOT NULL,
    job_family VARCHAR(50) NOT NULL,
    seniority VARCHAR(20) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL
);

CREATE TABLE applications (
    application_id VARCHAR(50) PRIMARY KEY,
    job_id VARCHAR(50) NOT NULL REFERENCES jobs(job_id) ON DELETE CASCADE,
    candidate_id VARCHAR(50) NOT NULL REFERENCES candidates(candidate_id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    rule_score NUMERIC(3, 2) CHECK (rule_score BETWEEN 0.0 AND 1.0),
    rule_fit VARCHAR(20) CHECK (rule_fit IN ('low', 'medium', 'good')),
    llm_score INT CHECK (llm_score BETWEEN 0 AND 100),
    llm_model_version VARCHAR(20) NOT NULL,
    recruiter_decision VARCHAR(20) CHECK (recruiter_decision IN ('rejected', 'interviewed', 'hired')),
    decision_at TIMESTAMP WITH TIME ZONE
);

CREATE TABLE recruiter_events (
    event_id VARCHAR(50) PRIMARY KEY,
    application_id VARCHAR(50) NOT NULL REFERENCES applications(application_id) ON DELETE CASCADE,
    recruiter_id VARCHAR(50) NOT NULL,
    event_type VARCHAR(50) NOT NULL CHECK (event_type IN ('profile_opened', 'ai_score_viewed', 'shortlisted')),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL
);

-- Indexes for backend analytics performance
CREATE INDEX idx_applications_segmentation ON applications(llm_model_version, recruiter_decision);
CREATE INDEX idx_jobs_family_country ON jobs(job_family, country);
CREATE INDEX idx_recruiter_events_app_id ON recruiter_events(application_id);

-- 2. COPY CSV DATA INTO TABLES
-- Note: Empty values in CSV (like pending decisions/timestamps) load as NULL automatically

\copy candidates FROM '/var/lib/postgresql/csvs/candidates.csv' WITH (FORMAT csv, HEADER true);
\copy jobs FROM '/var/lib/postgresql/csvs/jobs.csv' WITH (FORMAT csv, HEADER true);
\copy applications FROM '/var/lib/postgresql/csvs/applications.csv' WITH (FORMAT csv, HEADER true, NULL '');
\copy recruiter_events FROM '/var/lib/postgresql/csvs/recruiter_events.csv' WITH (FORMAT csv, HEADER true);

CREATE VIEW view_application_evaluations AS
SELECT
    a.application_id,
    a.job_id,
    a.candidate_id,
    j.job_family,
    j.country AS job_country,
    c.country AS candidate_country,
    c.years_experience,
    c.profile_completeness,
    a.llm_model_version,

    -- Normalized scores (0.0 to 1.0 scale)
    a.rule_score,
    (a.llm_score / 100.0) AS llm_score_norm,

    -- Score divergence (Agreement metric)
    ABS(a.rule_score - (a.llm_score / 100.0)) AS score_delta,

    -- Ground truth excludes pending decisions.
    a.recruiter_decision,
    CASE
        WHEN a.recruiter_decision IN ('interviewed', 'hired') THEN 1
        WHEN a.recruiter_decision = 'rejected' THEN 0
        ELSE NULL -- Pending decision
    END AS is_positive_outcome
FROM applications a
JOIN candidates c ON a.candidate_id = c.candidate_id
JOIN jobs j ON a.job_id = j.job_id;
