\# Week 11 — Security Hardening and Monitoring



\## Overview



Week 11 hardens the Week 10 AI agent by improving secrets management, logging privacy, dependency security, and monitoring readiness.



The security implementation is applied to the existing Week 10 application rather than duplicated in a separate application.



\## Learning Objectives



\- Prepare secrets management using Azure Key Vault.

\- Use `DefaultAzureCredential` for Azure authentication.

\- Apply least-privilege access principles.

\- Avoid logging user messages, generated answers, document contents, and credentials.

\- Record structured operational events for troubleshooting.

\- Prepare Azure Monitor / Application Insights integration.

\- Audit Python dependencies for known vulnerabilities.

\- Document personal information (PII) handling and retention practices.



\## Implementation Guide



| Area | Implementation |

|---|---|

| Secrets configuration | `Week 10/azure\_config.py` |

| Environment template | `Week 10/.env.example` |

| Agent orchestration and privacy-conscious events | `Week 10/agent.py` |

| HTTP request monitoring | `Week 10/main.py` |

| Azure Monitor integration | `Week 10/monitoring.py` |

| Structured local event logs | `Week 10/tracing.py` |

| Security and retention notes | `Week 10/SECURITY.md` |

| Automated tests | `Week 10/tests/` |

| Dedicated CI workflow | `.github/workflows/week11-security.yml` |



\## How to Verify



Run the following commands from the repository root in PowerShell:



```powershell

Set-Location "Week 10"



python -m py\_compile ".\\agent.py" ".\\main.py" ".\\tracing.py" ".\\monitoring.py" ".\\azure\_config.py"



python -m pytest -q



python -m pip check



python -m pip\_audit -r ".\\requirements.txt"



python ".\\evaluation\_offline.py"

```



The dependency audit requires `pip-audit` to be installed in the active environment.



GitHub Actions runs the automated checks independently when the workflow is triggered.



\## Recorded Verification Results



Development verification on 27 October 2026:



\- Python compilation: passed.

\- Automated tests: 19 passed.

\- Dependency consistency: no broken requirements found.

\- Week 10 dependency audit: no known vulnerabilities found in the resolved requirements at the time of the audit.

\- Previous offline evaluation: 10/10 checks passed.



These are recorded development results, not a guarantee that future dependency versions or deployments will remain vulnerability-free.



\## Secrets and Personal Information



\- Keep real credentials in a local `.env` file for development; never commit that file.

\- Use `.env.example` for placeholders only.

\- Avoid writing user messages, generated answers, document contents, credentials, or API keys to logs.

\- Restrict access to logs and monitoring data.

\- Define an appropriate retention period before production deployment and securely dispose of records when retention ends.



See \[Week 10 Security Notes](../Week%2010/SECURITY.md) for further details.



\## Azure Deployment Status and Limitations



This project was developed without an Azure subscription.



The Azure Key Vault and Azure Monitor integrations are prepared in code but have not been validated against live Azure resources.



Before production deployment:



1\. Configure Azure Key Vault and store the `GEMINI-API-KEY` secret.

2\. Configure an appropriate Azure identity and grant only the required permissions.

3\. Configure Application Insights and validate telemetry.

4\. Confirm access controls, retention settings, and privacy requirements.

5\. Test secret retrieval and monitoring in the deployed environment.



`DefaultAzureCredential` supports different authentication methods depending on the environment. A deployed Azure managed identity must be configured and authorized; the code alone does not provision or validate that identity.



Gemini API authentication still requires a supported Gemini credential. Azure managed identity does not automatically replace the Gemini API key.



\## Submission Checklist



\- \[x] Security implementation documented.

\- \[x] Local environment file excluded from Git.

\- \[x] Structured logging avoids recording request content and tool results in the updated event paths.

\- \[x] Dependency audit performed.

\- \[x] Automated tests passed locally.

\- \[x] Azure deployment limitations documented.

\- \[ ] Dedicated Week 11 GitHub Actions workflow passes.

\- \[ ] Live Azure Key Vault, identity, and monitoring validation completed when Azure access is available.

