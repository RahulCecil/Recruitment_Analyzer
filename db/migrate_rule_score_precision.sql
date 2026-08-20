-- Apply this migration to an existing database initialized before NUMERIC(5,4).

DROP VIEW IF EXISTS view_application_evaluations;

ALTER TABLE applications
    ALTER COLUMN rule_score TYPE NUMERIC(5, 4)
    USING rule_score::NUMERIC(5, 4);

CREATE OR REPLACE VIEW view_application_evaluations AS
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
    a.rule_score::double precision AS rule_score,
    (a.llm_score / 100.0)::double precision AS llm_score_norm,
    ABS(a.rule_score - (a.llm_score / 100.0))::double precision AS score_delta,
    a.recruiter_decision,
    CASE
        WHEN a.recruiter_decision IN ('interviewed', 'hired') THEN 1
        WHEN a.recruiter_decision = 'rejected' THEN 0
        ELSE NULL
    END AS is_positive_outcome
FROM applications a
JOIN candidates c ON a.candidate_id = c.candidate_id
JOIN jobs j ON a.job_id = j.job_id;