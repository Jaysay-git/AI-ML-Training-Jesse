# Week 10 Agent — Security Notes

## 1. Secrets Management
- Local development secrets are stored in a local `.env` file.
- `.env` files are excluded from Git using `.gitignore`.
- `.env.example` contains placeholders only; it must never contain real secrets.
- Production secrets should be stored in Azure Key Vault.
- The application uses `DefaultAzureCredential` to authenticate to Azure Key Vault.
- The required Key Vault secret name is `GEMINI-API-KEY`.
- The deployed application's managed identity should receive only the Key Vault permissions it needs.
- Gemini API authentication still requires a supported Gemini API credential.

## 2. Access Control
- Use least-privilege access for application identities and developers.
- Only authorized users should be able to access secrets, logs, and monitoring data.
- Do not grant broad administrative permissions when narrower permissions are sufficient.

## 3. Logging and PII
- Application logs record event names, timestamps, request paths, status codes, durations, and limited operational metadata.
- User messages, generated answers, document contents, credentials, and API keys must not be written to application logs.
- Review existing local logs for sensitive information and clear or securely remove records that should not be retained.

## 4. Retention
- Keep logs only for the period required by the project's operational and organizational needs.
- Define retention periods before deploying to production.
- Restrict access to logs and securely dispose of records when retention ends.
- Do not place sensitive personal information in logs unless explicitly required and appropriately protected.

## 5. Monitoring
- The application supports optional Azure Monitor / Application Insights configuration.
- Without an Application Insights connection string, Azure monitoring remains disabled.
- Local structured JSON logs are written to `logs/agent.jsonl`.
- Production monitoring should track request latency, HTTP errors, exceptions, and service health without collecting unnecessary personal data.

## 6. Dependency Security
- Week 10 dependencies were audited with `python -m pip_audit -r .\requirements.txt`.
- Audit result: no known vulnerabilities found in the resolved Week 10 requirements at the time of the check.
- Repeat dependency audits regularly and after significant dependency changes.

## 7. Azure Deployment Status
- Azure Key Vault, managed identity, and Application Insights have not been verified against live Azure resources.
- This project currently uses local development configuration.
- Validate Azure permissions, secret retrieval, monitoring, and deployment settings before production use.
