CREATE TABLE IF NOT EXISTS candidates (
    candidate_id VARCHAR(50) PRIMARY KEY,
    country VARCHAR(10),
    years_experience INTEGER,
    preferred_job_family VARCHAR(100),
    profile_completeness DOUBLE PRECISION
);

CREATE TABLE IF NOT EXISTS jobs (
    job_id VARCHAR(50) PRIMARY KEY,
    country VARCHAR(10),
    job_family VARCHAR(100),
    seniority VARCHAR(50),
    created_at VARCHAR(50)
);

CREATE TABLE IF NOT EXISTS applications (
    application_id VARCHAR(50) PRIMARY KEY,
    job_id VARCHAR(50),
    candidate_id VARCHAR(50),
    created_at VARCHAR(50),
    rule_score DOUBLE PRECISION,
    rule_fit VARCHAR(50),
    llm_score DOUBLE PRECISION,
    llm_model_version VARCHAR(50),
    recruiter_decision VARCHAR(50),
    decision_at VARCHAR(50)
);

CREATE TABLE IF NOT EXISTS recruiter_events (
    event_id VARCHAR(50) PRIMARY KEY,
    application_id VARCHAR(50),
    recruiter_id VARCHAR(50),
    event_type VARCHAR(100),
    created_at VARCHAR(50)
);

COPY candidates(candidate_id, country, years_experience, preferred_job_family, profile_completeness)
FROM '/var/lib/postgresql/csvs/candidates.csv'
DELIMITER ','
CSV HEADER;

COPY jobs(job_id, country, job_family, seniority, created_at)
FROM '/var/lib/postgresql/csvs/jobs.csv'
DELIMITER ','
CSV HEADER;

COPY applications(application_id, job_id, candidate_id, created_at, rule_score, rule_fit, llm_score, llm_model_version, recruiter_decision, decision_at)
FROM '/var/lib/postgresql/csvs/applications.csv'
DELIMITER ','
CSV HEADER;

COPY recruiter_events(event_id, application_id, recruiter_id, event_type, created_at)
FROM '/var/lib/postgresql/csvs/recruiter_events.csv'
DELIMITER ','
CSV HEADER;
