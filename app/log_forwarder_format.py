"""
CFC SOC Log Forwarder Format Module

Based on CFC SOC Logging Guidelines 4.0
Supports: Platform, Application, and API log types
Format: Space-separated columns (per LOG-8 requirement)
Storage: AWS CloudWatch -> S3 (CSV or TXT)
"""

from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any
import json


class LogType(Enum):
    """Log type enumeration per CFC SOC guidelines"""
    LOGIN = "[AUDIT] [Login]"
    API = "[AUDIT] [API]"
    ENDUSER = "[AUDIT] [EndUser]"
    MACD = "[AUDIT] [MACD]"


class ApiDirection(Enum):
    """Direction of API call"""
    INBOUND = "INBOUND"  # Other platforms calling this system
    OUTBOUND = "OUTBOUND"  # This system calling other platforms


class OperationStatus(Enum):
    """Operation status"""
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"
    ERROR = "ERROR"


@dataclass
class BaseLogEntry:
    """Base log entry with common fields"""
    timestamp: str  # ISO 8601 format: YYYY-MM-DD HH:MM:SS.sss
    user_id: str  # User identifier
    ip_address: str  # Source IP address
    platform: str  # Platform identifier (e.g., CFC, AWS, Azure)
    app_name: str  # Application name

    def to_space_separated(self, *args) -> str:
        """Convert to space-separated format (per LOG-8)"""
        values = [str(v) if v is not None else "N/A" for v in args]
        return " ".join(values)


@dataclass
class PlatformLogEntry(BaseLogEntry):
    """Platform log entry - OS and infrastructure events"""
    log_type: str = field(default="[AUDIT] [Platform]")
    event_type: str = ""  # OS, CloudTrail, GuardDuty, Config, etc.
    event_name: str = ""  # Specific event name
    resource_id: str = ""  # Resource identifier
    status: OperationStatus = OperationStatus.SUCCESS
    details: str = ""  # Additional details

    def to_log_entry(self) -> str:
        """Format as log entry string"""
        return self.to_space_separated(
            self.timestamp,
            self.log_type,
            self.platform,
            self.app_name,
            self.user_id,
            self.ip_address,
            self.event_type,
            self.event_name,
            self.resource_id,
            self.status.value,
            self.details
        )


@dataclass
class ApplicationLogEntry(BaseLogEntry):
    """Application log entry"""
    log_type: LogType = LogType.ENDUSER
    action: str = ""  # Action performed (view, create, update, delete, etc.)
    resource: str = ""  # Resource name/type
    status: OperationStatus = OperationStatus.SUCCESS
    details: str = ""  # Additional details

    def to_log_entry(self) -> str:
        """Format as log entry string"""
        return self.to_space_separated(
            self.timestamp,
            self.log_type.value,
            self.platform,
            self.app_name,
            self.user_id,
            self.ip_address,
            self.action,
            self.resource,
            self.status.value,
            self.details
        )


@dataclass
class LoginLogEntry(BaseLogEntry):
    """Login/Authentication log entry"""
    log_type: str = field(default="[AUDIT] [Login]")
    auth_method: str = "Azure_AD"  # Authentication method
    status: OperationStatus = OperationStatus.SUCCESS
    failure_reason: str = ""  # Reason for failure (if any)
    session_id: str = ""  # Session identifier

    def to_log_entry(self) -> str:
        """Format as log entry string"""
        return self.to_space_separated(
            self.timestamp,
            self.log_type,
            self.platform,
            self.app_name,
            self.user_id,
            self.ip_address,
            self.auth_method,
            self.status.value,
            self.failure_reason,
            self.session_id
        )


@dataclass
class ApiLogEntry(BaseLogEntry):
    """API call log entry - tracks inbound and outbound API requests"""
    log_type: str = field(default="[AUDIT] [API]")
    api_direction: ApiDirection = ApiDirection.INBOUND
    api_name: str = ""  # API endpoint/method name
    api_version: str = ""  # API version
    request_method: str = ""  # HTTP method (GET, POST, PUT, DELETE, etc.)
    request_path: str = ""  # API request path
    remote_system: str = ""  # Remote system calling/being called
    status_code: int = 200  # HTTP status code
    response_status: OperationStatus = OperationStatus.SUCCESS
    request_size: int = 0  # Request size in bytes
    response_size: int = 0  # Response size in bytes
    duration_ms: int = 0  # Duration in milliseconds
    error_message: str = ""  # Error message if failed

    def to_log_entry(self) -> str:
        """Format as log entry string"""
        return self.to_space_separated(
            self.timestamp,
            self.log_type,
            self.platform,
            self.app_name,
            self.api_direction.value,
            self.api_name,
            self.api_version,
            self.request_method,
            self.request_path,
            self.user_id,
            self.ip_address,
            self.remote_system,
            self.status_code,
            self.response_status.value,
            self.request_size,
            self.response_size,
            self.duration_ms,
            self.error_message
        )


@dataclass
class MacdLogEntry(BaseLogEntry):
    """MACD (Move/Add/Change/Delete) log entry - admin operations"""
    log_type: str = field(default="[AUDIT] [MACD]")
    operation_type: str = ""  # ADD, CHANGE, DELETE, MOVE
    object_type: str = ""  # User, Role, Resource, Configuration, etc.
    object_id: str = ""  # Object identifier
    old_value: str = ""  # Previous value (for CHANGE operations)
    new_value: str = ""  # New value
    status: OperationStatus = OperationStatus.SUCCESS
    reason: str = ""  # Reason for operation

    def to_log_entry(self) -> str:
        """Format as log entry string"""
        return self.to_space_separated(
            self.timestamp,
            self.log_type,
            self.platform,
            self.app_name,
            self.user_id,
            self.ip_address,
            self.operation_type,
            self.object_type,
            self.object_id,
            self.old_value,
            self.new_value,
            self.status.value,
            self.reason
        )


class LogForwarderFormat:
    """Main log forwarder format class"""

    # Log file format requirements
    SEPARATOR = " "  # Single space (per LOG-8)
    SUPPORTED_FORMATS = ["csv", "txt"]
    RETENTION_DAYS = 365

    @staticmethod
    def create_platform_log(
        timestamp: str,
        platform: str,
        app_name: str,
        user_id: str,
        ip_address: str,
        event_type: str,
        event_name: str,
        resource_id: str = "",
        status: OperationStatus = OperationStatus.SUCCESS,
        details: str = ""
    ) -> PlatformLogEntry:
        """Create a platform/OS log entry"""
        return PlatformLogEntry(
            timestamp=timestamp,
            platform=platform,
            app_name=app_name,
            user_id=user_id,
            ip_address=ip_address,
            event_type=event_type,
            event_name=event_name,
            resource_id=resource_id,
            status=status,
            details=details
        )

    @staticmethod
    def create_login_log(
        timestamp: str,
        platform: str,
        app_name: str,
        user_id: str,
        ip_address: str,
        status: OperationStatus = OperationStatus.SUCCESS,
        auth_method: str = "Azure_AD",
        failure_reason: str = "",
        session_id: str = ""
    ) -> LoginLogEntry:
        """Create a login log entry"""
        return LoginLogEntry(
            timestamp=timestamp,
            platform=platform,
            app_name=app_name,
            user_id=user_id,
            ip_address=ip_address,
            auth_method=auth_method,
            status=status,
            failure_reason=failure_reason,
            session_id=session_id
        )

    @staticmethod
    def create_api_log(
        timestamp: str,
        platform: str,
        app_name: str,
        user_id: str,
        ip_address: str,
        api_direction: ApiDirection,
        api_name: str,
        api_version: str,
        request_method: str,
        request_path: str,
        remote_system: str = "",
        status_code: int = 200,
        response_status: OperationStatus = OperationStatus.SUCCESS,
        request_size: int = 0,
        response_size: int = 0,
        duration_ms: int = 0,
        error_message: str = ""
    ) -> ApiLogEntry:
        """Create an API log entry"""
        return ApiLogEntry(
            timestamp=timestamp,
            platform=platform,
            app_name=app_name,
            user_id=user_id,
            ip_address=ip_address,
            api_direction=api_direction,
            api_name=api_name,
            api_version=api_version,
            request_method=request_method,
            request_path=request_path,
            remote_system=remote_system,
            status_code=status_code,
            response_status=response_status,
            request_size=request_size,
            response_size=response_size,
            duration_ms=duration_ms,
            error_message=error_message
        )

    @staticmethod
    def create_application_log(
        timestamp: str,
        platform: str,
        app_name: str,
        user_id: str,
        ip_address: str,
        action: str,
        resource: str,
        log_type: LogType = LogType.ENDUSER,
        status: OperationStatus = OperationStatus.SUCCESS,
        details: str = ""
    ) -> ApplicationLogEntry:
        """Create an application log entry"""
        return ApplicationLogEntry(
            timestamp=timestamp,
            platform=platform,
            app_name=app_name,
            user_id=user_id,
            ip_address=ip_address,
            log_type=log_type,
            action=action,
            resource=resource,
            status=status,
            details=details
        )

    @staticmethod
    def create_macd_log(
        timestamp: str,
        platform: str,
        app_name: str,
        user_id: str,
        ip_address: str,
        operation_type: str,
        object_type: str,
        object_id: str,
        status: OperationStatus = OperationStatus.SUCCESS,
        old_value: str = "",
        new_value: str = "",
        reason: str = ""
    ) -> MacdLogEntry:
        """Create a MACD log entry"""
        return MacdLogEntry(
            timestamp=timestamp,
            platform=platform,
            app_name=app_name,
            user_id=user_id,
            ip_address=ip_address,
            operation_type=operation_type,
            object_type=object_type,
            object_id=object_id,
            status=status,
            old_value=old_value,
            new_value=new_value,
            reason=reason
        )


# Example usage and log format specifications
if __name__ == "__main__":
    # Example: Platform Log
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
    print("Platform Log:")
    print(platform_log.to_log_entry())
    print()

    # Example: Login Log - Success
    login_log_success = LogForwarderFormat.create_login_log(
        timestamp="2024-03-09 09:15:30.456",
        platform="CFC",
        app_name="portal",
        user_id="user@lilly.com",
        ip_address="203.0.113.45",
        status=OperationStatus.SUCCESS,
        auth_method="Azure_AD",
        session_id="sess-abc123xyz"
    )
    print("Login Log (Success):")
    print(login_log_success.to_log_entry())
    print()

    # Example: Login Log - Failure
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
    print("Login Log (Failure):")
    print(login_log_failure.to_log_entry())
    print()

    # Example: API Log - Inbound
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
    print("API Log (Inbound):")
    print(api_log_inbound.to_log_entry())
    print()

    # Example: API Log - Outbound
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
    print("API Log (Outbound):")
    print(api_log_outbound.to_log_entry())
    print()

    # Example: API Log - Error
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
    print("API Log (Error):")
    print(api_log_error.to_log_entry())
    print()

    # Example: Application Log - User Action
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
    print("Application Log (User Action):")
    print(app_log.to_log_entry())
    print()

    # Example: MACD Log - Add Role
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
    print("MACD Log (Add):")
    print(macd_log_add.to_log_entry())
    print()

    # Example: MACD Log - Change Config
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
    print("MACD Log (Change):")
    print(macd_log_change.to_log_entry())
    print()

    print("\n=== Log Format Specifications ===")
    print(f"Column Separator: '{LogForwarderFormat.SEPARATOR}' (single space - per LOG-8)")
    print(f"Supported Formats: {', '.join(LogForwarderFormat.SUPPORTED_FORMATS)}")
    print(f"Minimum Retention: {LogForwarderFormat.RETENTION_DAYS} days")
    print(f"Storage Route: AWS CloudWatch → S3")
    print(f"Compression: NOT allowed (per LOG-12)")
