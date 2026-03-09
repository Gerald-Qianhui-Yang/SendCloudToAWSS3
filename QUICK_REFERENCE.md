# CFC SOC Log Forwarder - Quick Reference

## Supported Log Types

| Type | Purpose | Key Fields |
|------|---------|-----------|
| **Platform** | OS, CloudTrail, GuardDuty, Config | event_type, event_name, resource_id |
| **Login** | User authentication | auth_method, status, session_id |
| **API** | API requests (inbound/outbound) | api_direction, method, path, status_code, duration_ms |
| **Application** | User actions | action, resource, status |
| **MACD** | Admin operations | operation_type, object_type, old_value, new_value |

## Format Specification

**Column Separator:** Single space (` `)
**File Format:** CSV or TXT
**Storage:** AWS CloudWatch → S3
**Retention:** 365 days minimum
**Compression:** NOT allowed

## Common Fields (All Logs)

```
timestamp platform app_name user_id ip_address [type-specific-fields]
```

- `timestamp`: YYYY-MM-DD HH:MM:SS.sss (ISO 8601)
- `platform`: CFC, AWS, Azure, etc.
- `app_name`: Application identifier
- `user_id`: User email or identifier
- `ip_address`: Source IP address

## Quick Examples

### Platform Log
```python
LogForwarderFormat.create_platform_log(
    timestamp="2024-03-09 15:30:45.123",
    platform="CFC",
    app_name="patient-app",
    user_id="admin@lilly.com",
    ip_address="192.168.1.100",
    event_type="CloudTrail",
    event_name="PutBucketPolicy",
    resource_id="arn:aws:s3:::cfc-logs-bucket"
)
```

### Login Log
```python
LogForwarderFormat.create_login_log(
    timestamp="2024-03-09 09:15:30.456",
    platform="CFC",
    app_name="portal",
    user_id="user@lilly.com",
    ip_address="203.0.113.45",
    status=OperationStatus.SUCCESS,
    auth_method="Azure_AD",
    session_id="sess-abc123xyz"
)
```

### API Log (Inbound)
```python
LogForwarderFormat.create_api_log(
    timestamp="2024-03-09 14:22:10.234",
    platform="CFC",
    app_name="data-service",
    user_id="external-system@partner.com",
    ip_address="198.51.100.50",
    api_direction=ApiDirection.INBOUND,
    api_name="getPatientData",
    api_version="v2",
    request_method="POST",
    request_path="/api/v2/patients/search",
    remote_system="HIS-System",
    status_code=200,
    response_status=OperationStatus.SUCCESS,
    request_size=512,
    response_size=2048,
    duration_ms=145
)
```

### API Log (Outbound)
```python
LogForwarderFormat.create_api_log(
    timestamp="2024-03-09 14:25:33.567",
    platform="CFC",
    app_name="integration-service",
    user_id="integration@lilly.com",
    ip_address="192.168.1.50",
    api_direction=ApiDirection.OUTBOUND,
    api_name="createOrder",
    api_version="v1",
    request_method="POST",
    request_path="/api/v1/orders",
    remote_system="ERP-System",
    status_code=201,
    response_status=OperationStatus.SUCCESS,
    request_size=1024,
    response_size=512,
    duration_ms=320
)
```

### Application Log
```python
LogForwarderFormat.create_application_log(
    timestamp="2024-03-09 13:45:20.123",
    platform="CFC",
    app_name="patient-portal",
    user_id="doctor@lilly.com",
    ip_address="203.0.113.88",
    action="VIEW",
    resource="patient_record_5678",
    log_type=LogType.ENDUSER,
    status=OperationStatus.SUCCESS
)
```

### MACD Log
```python
LogForwarderFormat.create_macd_log(
    timestamp="2024-03-09 11:00:00.456",
    platform="CFC",
    app_name="admin-console",
    user_id="admin@lilly.com",
    ip_address="192.168.1.1",
    operation_type="ADD",
    object_type="Role",
    object_id="role-viewer-001",
    status=OperationStatus.SUCCESS,
    new_value="ViewerRole with read permissions",
    reason="New role for external auditors"
)
```

## Enums

### ApiDirection
- `INBOUND` - Other systems calling this system
- `OUTBOUND` - This system calling other systems

### OperationStatus
- `SUCCESS` - Operation completed successfully
- `FAILURE` - Operation failed
- `ERROR` - System error occurred

### LogType
- `LOGIN` - Authentication logs
- `API` - API request logs
- `ENDUSER` - User action logs
- `MACD` - Admin operation logs

## Export to File

```python
from app.log_forwarder_integration import LogForwarderIntegration

logs = [log1, log2, log3, ...]
LogForwarderIntegration.export_logs_to_file(logs, "output.txt")
```

## Running Examples

```bash
# View all log format examples
python app/log_forwarder_format.py

# Generate sample log files
python app/log_forwarder_integration.py
```

## Sample Output Files

- `logs_user_session.txt` - 7 logs from user session
- `logs_admin_session.txt` - 4 logs from admin work
- `logs_api_integration.txt` - 5 logs from API calls
- `logs_platform_events.txt` - 3 logs from infrastructure

## Integration Checklist

- [ ] Import `LogForwarderFormat` in your application
- [ ] Create log entries using appropriate factory methods
- [ ] Call `.to_log_entry()` to generate formatted string
- [ ] Send to AWS CloudWatch
- [ ] Verify logs appear in S3 with correct format
- [ ] Test log retention settings (365+ days)
- [ ] Verify access controls are enforced
- [ ] Document log review procedures in security plan

## Compliance Requirements

✅ **LOG-8**: Single-space column separators
✅ **LOG-9**: CloudWatch ingestion support
✅ **LOG-12**: CSV/TXT format, no compression
✅ **LOG-1**: Login logs with success/failure
✅ **LOG-2**: API logs with inbound/outbound direction
✅ **LOG-3**: User action logs (EndUser)
✅ **LOG-4**: Admin operation logs (MACD)

## Files

- `log_forwarder_format.py` - Core module with all log types
- `log_forwarder_integration.py` - Integration examples and sample generation
- `LOG_FORWARDER_FORMAT.md` - Complete documentation
- `IMPLEMENTATION_SUMMARY.md` - Full implementation guide
- `QUICK_REFERENCE.md` - This file

---

**Status:** Production Ready
**Requirements:** Python 3.7+ (no external dependencies)
