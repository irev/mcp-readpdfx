# Security Policy

## 🔒 Supported Versions

We actively maintain security updates for the following versions of ReadPDFx:

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | ✅ Fully supported |
| < 1.0   | ❌ No longer supported |

## 🚨 Reporting a Vulnerability

We take the security of ReadPDFx seriously. If you believe you have found a security vulnerability, please report it to us as described below.

### ⚠️ Please do NOT report security vulnerabilities through public GitHub issues.

Instead, please report them via email to: **security@readpdfx.com**

### 📧 Security Report Format

Please include the following information in your security report:

1. **Description**: A clear description of the vulnerability
2. **Impact**: What kind of vulnerability it is and what an attacker could do
3. **Reproduction**: Step-by-step instructions to reproduce the issue
4. **Environment**: Version information, OS, Python version, etc.
5. **Proof of Concept**: If available, include proof-of-concept code
6. **Suggested Fix**: If you have ideas on how to fix the issue

### 🔍 What to Include

```
Subject: [SECURITY] Brief description of the vulnerability

ReadPDFx Version: 1.0.0
Python Version: 3.11.5
Operating System: Ubuntu 22.04

Vulnerability Description:
[Detailed description of the vulnerability]

Steps to Reproduce:
1. [First step]
2. [Second step]
3. [Third step]

Expected Behavior:
[What should happen]

Actual Behavior:
[What actually happens]

Impact:
[What an attacker could do]

Proof of Concept:
[Include code or screenshots if applicable]
```

## ⏱️ Response Timeline

We will acknowledge your email within **48 hours** and will send a more detailed response within **7 days** indicating the next steps in handling your report.

After the initial reply to your report, we will:
- Keep you informed of the progress towards a fix and full announcement
- May ask for additional information or guidance
- Credit you appropriately if you wish

## 🛡️ Security Measures

ReadPDFx implements several security measures:

### Input Validation
- All file paths are validated and sanitized
- File size limits are enforced
- File type validation for uploaded content
- Input parameter validation for all API endpoints

### Access Control
- No authentication required for basic OCR operations
- File system access limited to specified directories
- Network access controlled and monitored

### Data Handling
- Temporary files are securely cleaned up
- No persistent storage of processed content
- Memory usage is bounded and monitored

### Dependencies
- Regular dependency updates
- Security scanning of dependencies
- Minimal dependency footprint

## 🔐 Security Best Practices for Users

### Server Deployment
- Run ReadPDFx with minimal privileges
- Use a dedicated user account
- Limit file system access
- Enable logging and monitoring
- Use HTTPS in production
- Implement rate limiting
- Set up proper firewall rules

### File Handling
- Validate all input files
- Use secure file upload mechanisms
- Implement virus scanning if processing untrusted files
- Set appropriate file size limits
- Clean up temporary files

### Network Security
- Use secure communication channels
- Implement proper authentication for production use
- Monitor network traffic
- Use VPN or private networks when possible

### Configuration Security
```bash
# Example secure configuration
export MCP_SERVER_HOST="127.0.0.1"  # Bind to localhost only
export MCP_MAX_FILE_SIZE="100MB"    # Limit file sizes
export MCP_TEMP_DIR="/secure/tmp"   # Use secure temp directory
export MCP_LOG_LEVEL="INFO"         # Enable logging
```

## 🚨 Known Security Considerations

### File System Access
ReadPDFx needs to read PDF files and write temporary files. Ensure:
- Input files are from trusted sources
- Temp directory has proper permissions
- File paths are properly validated

### Memory Usage
Large PDF files can consume significant memory:
- Monitor memory usage
- Set appropriate resource limits
- Implement timeouts for long-running operations

### Network Endpoints
HTTP endpoints are exposed for MCP clients:
- Use authentication in production
- Implement rate limiting
- Monitor for unusual activity

### Dependencies
ReadPDFx relies on external libraries:
- Tesseract OCR
- PDF processing libraries
- HTTP server frameworks

Regular updates and security scanning are recommended.

## 📋 Security Checklist for Deployment

### Before Deployment
- [ ] Update all dependencies to latest versions
- [ ] Run security scans on dependencies
- [ ] Review configuration for security best practices
- [ ] Set up proper logging and monitoring
- [ ] Configure firewalls and network security
- [ ] Test with security scanning tools

### During Operation
- [ ] Monitor logs for unusual activity
- [ ] Regular security updates
- [ ] Monitor resource usage
- [ ] Backup security configurations
- [ ] Regular security assessments

### Incident Response
- [ ] Have incident response plan ready
- [ ] Know how to quickly shut down the service
- [ ] Have backup and recovery procedures
- [ ] Keep security contact information updated

## 🔧 Security Configuration

### Environment Variables
```bash
# Security-focused environment configuration
export MCP_SERVER_HOST="127.0.0.1"
export MCP_SERVER_PORT="8000"
export MCP_MAX_FILE_SIZE="100MB"
export MCP_REQUEST_TIMEOUT="30"
export MCP_RATE_LIMIT="100"
export MCP_LOG_LEVEL="INFO"
export MCP_SECURE_HEADERS="true"
```

### Recommended Firewall Rules
```bash
# Allow only necessary connections
iptables -A INPUT -p tcp --dport 8000 -s 127.0.0.1 -j ACCEPT
iptables -A INPUT -p tcp --dport 8000 -j DROP
```

## 📊 Security Monitoring

### Log Monitoring
Monitor logs for:
- Failed authentication attempts
- Unusual file access patterns
- Large file uploads
- Repeated error messages
- Memory or CPU spikes

### Metrics to Track
- Request rates and response times
- Error rates by endpoint
- File processing times
- Memory and CPU usage
- Network connection patterns

## 🆘 Security Incident Response

### Immediate Actions
1. **Isolate**: Disconnect from network if needed
2. **Assess**: Determine scope and impact
3. **Document**: Record all findings
4. **Notify**: Contact security team
5. **Contain**: Prevent further damage

### Communication
- Internal team notification
- User notification (if applicable)
- Security community disclosure (after fix)
- Documentation updates

## 📝 Security Updates

Security updates will be:
- Released as soon as possible
- Clearly marked as security releases
- Include detailed fix information
- Provide upgrade instructions

Subscribe to security notifications:
- Watch the GitHub repository
- Follow security mailing list
- Check release notes regularly

## 🏆 Security Hall of Fame

We recognize security researchers who help improve ReadPDFx security:

- [Your name could be here!]

### Responsible Disclosure Recognition
- Public acknowledgment (with permission)
- Credit in release notes
- Special thanks in documentation
- Priority support for security researchers

## 📞 Contact Information

**Security Email**: security@readpdfx.com  
**General Issues**: https://github.com/irev/mcp-readpdfx/issues  
**Documentation**: https://github.com/irev/mcp-readpdfx#readme

---

**Thank you for helping keep ReadPDFx secure!** 🛡️