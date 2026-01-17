# Security Policy

## Reporting a Vulnerability

If you believe you have found a security vulnerability in this repository, please report it responsibly.

**Do not open a public GitHub issue for security-related findings.**

Instead, report the issue using one of the methods below.

### Preferred Reporting Method
- GitHub Security Advisories  
  Use the **“Report a vulnerability”** button in the repository’s **Security** tab.

### Alternative Contact
- Email: sydefcon5@gmail.com  
  (Replace with a monitored address)

Please include:
- A clear description of the issue
- Steps to reproduce (if applicable)
- Impact and attack scenario
- Any proof-of-concept or references

---

## Supported Versions

Only the **latest version on the `main` branch** is actively supported with security updates.

| Version | Supported |
|-------|-----------|
| main  | ✅ |
| older releases | ❌ |

---

## Disclosure Process

Once a vulnerability is reported:

1. We will acknowledge receipt within **72 hours**
2. We will assess severity and impact
3. We will work on a fix or mitigation
4. We will coordinate disclosure timing when appropriate

We follow **responsible disclosure** practices and appreciate coordinated reporting.

---

## Scope

In scope:
- Source code in this repository
- CI/CD workflows
- Dependency configuration
- Build and deployment scripts

Out of scope:
- Third-party dependencies (report upstream)
- Issues requiring physical access
- Denial-of-service attacks
- Social engineering attacks

---

## Security Best Practices

This project follows basic security hygiene, including:
- No hardcoded secrets in source code
- Use of `.gitignore` for sensitive files
- Dependency review and updates
- Branch protection and PR-based changes

---

## Acknowledgements

We appreciate the efforts of the security community and will acknowledge valid reports when appropriate.

Thank you for helping keep this project secure.
