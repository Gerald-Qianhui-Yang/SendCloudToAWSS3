# CFC SOC Log Forwarder Format

A comprehensive Python module for generating SOC (Security Operation Centre) logs according to CFC (China Future Cloud) SOC Logging Guidelines 4.0.

**Location:** `app/log_forwarder_format.py`

## Overview

This module implements a structured log format for forwarding security logs from various sources (applications, platforms, APIs) to AWS CloudWatch and S3. It focuses on three main log categories:
- **Platform Logs**: OS and infrastructure events
- **Application Logs**: User actions, API calls, admin operations
- **API Type Logs**: Inbound/outbound API requests with full tracing

## Features

### Core Log Types

1. **Platform Logs** - OS, CloudTrail, GuardDuty, Config events
   - Event type and name tracking
   - Resource identification
   - Status and error details

2. **Login Logs** - User authentication events
   - Success/failure tracking
   - Authentication method recording
   - Failure reason documentation
   - Session ID tracking

3. **API Logs** - API request/response tracking
   - Inbound/outbound direction
   - API name, version, method, path
   - Request/response sizing
   - HTTP status codes
   - Duration metrics
   - Error message capture

4. **Application Logs** - General user actions
   - Action and resource tracking
   - Status monitoring
   - Custom details support

5. **MACD Logs** - Admin operations
   - Move/Add/Change/Delete operations
   - Object type and ID tracking
   - Before/after value tracking
   - Operation reason documentation

## Format Specifications

### Requirements (Per CFC SOC Guidelines)

| Requirement | Specification | Reference |
|---|---|---|
| **Column Separator** | Single space (` `) | LOG-8 |
| **File Format** | CSV or TXT | LOG-12 |
| **Compression** | NOT allowed | LOG-12 |
| **Storage** | AWS CloudWatch → S3 | LOG-9 |
| **Retention** | Minimum 365 days | All log types |
| **Access** | Read-only for users | Security requirement |

### Common Fields

All log entries include:
- `timestamp`: ISO 8601 format (YYYY-MM-DDTHH:MM:SS.sss)
- `log_type`: Log classification tag
- `platform`: Platform identifier (e.g., CFC, AWS, Azure)
- `app_name`: Application name
- `user_id`: User identifier
- `ip_address`: Source IP address

## Usage Examples

### Platform Log

```python
from log_forwarder_format import LogForwarderFormat, OperationStatus

platform_log = LogForwarderFormat.create_platform_log(
    timestamp="2024-03-09 15:30:45.123",
    platform="CFC",
    app_name="patient-app",
    user_id="admin@lilly.com",
    ip_address="192.168.1.100",
    event_type="CloudTrail",
    event_name="PutBucketPolicy",
    resource_id="arn:aws:s3:::cfc-logs-bucket",
    status=OperationStatus.SUCCESS
)
log_entry = platform_log.to_log_entry()
print(log_entry)
```

Output:
```
2024-03-09 15:30:45.123 [AUDIT] [Platform] CFC patient-app admin@lilly.com 192.168.1.100 CloudTrail PutBucketPolicy arn:aws:s3:::cfc-logs-bucket SUCCESS
```

### Login Log - Success

```python
login_log = LogForwarderFormat.create_login_log(
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

Output:
```
2024-03-09 09:15:30.456 [AUDIT] [Login] CFC portal user@lilly.com 203.0.113.45 Azure_AD SUCCESS  sess-abc123xyz
```

### Login Log - Failure

```python
login_log_failure = LogForwarderFormat.create_login_log(
    timestamp="2024-03-09 09:14:15.789",
    platform="CFC",
    app_name="portal",
    user_id="user@domain.com",
    ip_address="203.0.113.46",
    status=OperationStatus.FAILURE,
    auth_method="Azure_AD",
    failure_reason="User exists in AD but lacks application permissions"
)
```

Output:
```
2024-03-09 09:14:15.789 [AUDIT] [Login] CFC portal user@domain.com 203.0.113.46 Azure_AD FAILURE User exists in AD but lacks application permissions
```

### API Log - Inbound

```python
from log_forwarder_format import ApiDirection

api_log_inbound = LogForwarderFormat.create_api_log(
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

Output:
```
2024-03-09 14:22:10.234 [AUDIT] [API] CFC data-service INBOUND getPatientData v2 POST /api/v2/patients/search external-system@partner.com 198.51.100.50 HIS-System 200 SUCCESS 512 2048 145
```

### API Log - Outbound

```python
api_log_outbound = LogForwarderFormat.create_api_log(
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

Output:
```
2024-03-09 14:25:33.567 [AUDIT] [API] CFC integration-service OUTBOUND createOrder v1 POST /api/v1/orders integration@lilly.com 192.168.1.50 ERP-System 201 SUCCESS 1024 512 320
```

### API Log - Error Scenario

```python
api_log_error = LogForwarderFormat.create_api_log(
    timestamp="2024-03-09 14:26:45.890",
    platform="CFC",
    app_name="data-service",
    user_id="app-user@lilly.com",
    ip_address="192.168.2.100",
    api_direction=ApiDirection.INBOUND,
    api_name="updateRecord",
    api_version="v1",
    request_method="PUT",
    request_path="/api/v1/records/12345",
    remote_system="Mobile-App",
    status_code=500,
    response_status=OperationStatus.ERROR,
    request_size=256,
    response_size=128,
    duration_ms=2500,
    error_message="Database connection timeout"
)
```

Output:
```
2024-03-09 14:26:45.890 [AUDIT] [API] CFC data-service INBOUND updateRecord v1 PUT /api/v1/records/12345 app-user@lilly.com 192.168.2.100 Mobile-App 500 ERROR 256 128 2500 Database connection timeout
```

### Application Log

```python
app_log = LogForwarderFormat.create_application_log(
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

Output:
```
2024-03-09 13:45:20.123 [AUDIT] [EndUser] CFC patient-portal doctor@lilly.com 203.0.113.88 VIEW patient_record_5678 SUCCESS
```

### MACD Log - Add Operation

```python
macd_log_add = LogForwarderFormat.create_macd_log(
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

Output:
```
2024-03-09 11:00:00.456 [AUDIT] [MACD] CFC admin-console admin@lilly.com 192.168.1.1 ADD Role role-viewer-001  ViewerRole with read permissions SUCCESS New role for external auditors
```

### MACD Log - Change Operation

```python
macd_log_change = LogForwarderFormat.create_macd_log(
    timestamp="2024-03-09 10:30:15.789",
    platform="CFC",
    app_name="admin-console",
    user_id="admin@lilly.com",
    ip_address="192.168.1.1",
    operation_type="CHANGE",
    object_type="Configuration",
    object_id="log-retention-policy",
    status=OperationStatus.SUCCESS,
    old_value="180 days",
    new_value="365 days",
    reason="Compliance requirement update"
)
```

Output:
```
2024-03-09 10:30:15.789 [AUDIT] [MACD] CFC admin-console admin@lilly.com 192.168.1.1 CHANGE Configuration log-retention-policy 180 days 365 days SUCCESS Compliance requirement update
```

## Log Type Reference

### Platform Logs
- **Event Types**: CloudTrail, GuardDuty, Config, OS logs
- **Use Case**: Track infrastructure and platform-level events

### Login Logs
- **Fields**: User, IP, Auth method, Status, Session ID
- **Use Case**: Authentication and access tracking

### API Logs
- **Fields**: Direction, API name, Method, Path, Status code, Duration
- **Use Case**: API usage monitoring and debugging

### Application Logs
- **Fields**: Action, Resource, Status, Details
- **Use Case**: User action tracking

### MACD Logs
- **Fields**: Operation type, Object, Old value, New value, Reason
- **Use Case**: Admin operation audit trail

## Compliance Requirements

✅ **LOG-8**: Column separators are single blank spaces
✅ **LOG-9**: Logs pushed to AWS CloudWatch service
✅ **LOG-12**: Format is CSV or TXT, not compressed
✅ **LOG-1 to LOG-4**: All required log types implemented
✅ **Retention**: 365 days minimum enforced
✅ **Security**: Read-only logs, user identification, IP tracking

## Storage and Routing

- **Source**: AWS CloudWatch (application logs)
- **Destination**: S3 (CFC Security account)
- **Frequency**: Real-time log generation
- **Format**: CSV or TXT files (space-separated)
- **Access Control**: China local security roles + Global AWS Cloud Foundation team

## Requirements

- Python 3.7+
- No external dependencies (uses only stdlib)

## Running Examples

```bash
python log_forwarder_format.py
```

This will display example logs for all types with actual output.
