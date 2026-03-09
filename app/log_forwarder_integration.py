"""
Practical Log Forwarder Integration Examples

This module demonstrates real-world usage patterns for the CFC SOC log forwarder,
including AWS CloudWatch integration and file export scenarios.
"""

from datetime import datetime, timedelta
from log_forwarder_format import (
    LogForwarderFormat,
    OperationStatus,
    ApiDirection,
    LogType
)
import json
from pathlib import Path


class LogForwarderIntegration:
    """Integration examples for the log forwarder"""

    @staticmethod
    def get_current_timestamp() -> str:
        """Get current timestamp in required format"""
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

    @staticmethod
    def export_logs_to_file(logs: list, filename: str, format_type: str = "txt"):
        """Export logs to file (txt or csv)"""
        output_path = Path(filename)
        with open(output_path, 'w') as f:
            for log in logs:
                f.write(log.to_log_entry() + "\n")
        print(f"✓ Exported {len(logs)} logs to {filename}")
        return output_path

    @staticmethod
    def generate_session_logs():
        """Generate logs for a complete user session"""
        logs = []
        timestamp_base = datetime.now()
        user_id = "doctor@lilly.com"
        app_name = "patient-portal"
        platform = "CFC"
        ip_address = "203.0.113.88"

        # 1. Login
        login_log = LogForwarderFormat.create_login_log(
            timestamp=timestamp_base.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3],
            platform=platform,
            app_name=app_name,
            user_id=user_id,
            ip_address=ip_address,
            status=OperationStatus.SUCCESS,
            auth_method="Azure_AD",
            session_id="sess-" + datetime.now().strftime("%Y%m%d%H%M%S")
        )
        logs.append(login_log)

        # 2. API calls while using the app
        api_calls = [
            {
                "timestamp": (timestamp_base + timedelta(seconds=5)),
                "api_name": "getPatientList",
                "method": "GET",
                "path": "/api/v1/patients",
                "size": 256,
                "duration": 120
            },
            {
                "timestamp": (timestamp_base + timedelta(seconds=15)),
                "api_name": "getPatientDetails",
                "method": "GET",
                "path": "/api/v1/patients/P123456",
                "size": 512,
                "duration": 85
            },
            {
                "timestamp": (timestamp_base + timedelta(seconds=45)),
                "api_name": "updatePatientRecord",
                "method": "PUT",
                "path": "/api/v1/patients/P123456",
                "size": 1024,
                "duration": 250
            }
        ]

        for api_call in api_calls:
            api_log = LogForwarderFormat.create_api_log(
                timestamp=api_call["timestamp"].strftime("%Y-%m-%d %H:%M:%S.%f")[:-3],
                platform=platform,
                app_name=app_name,
                user_id=user_id,
                ip_address=ip_address,
                api_direction=ApiDirection.OUTBOUND,
                api_name=api_call["api_name"],
                api_version="v1",
                request_method=api_call["method"],
                request_path=api_call["path"],
                remote_system="data-service",
                status_code=200,
                response_status=OperationStatus.SUCCESS,
                request_size=api_call["size"],
                response_size=api_call["size"] * 2,
                duration_ms=api_call["duration"]
            )
            logs.append(api_log)

        # 3. Application logs for user actions
        user_actions = [
            {
                "timestamp": (timestamp_base + timedelta(seconds=60)),
                "action": "VIEW",
                "resource": "patient_record_P123456"
            },
            {
                "timestamp": (timestamp_base + timedelta(seconds=120)),
                "action": "UPDATE",
                "resource": "patient_medications"
            },
            {
                "timestamp": (timestamp_base + timedelta(seconds=180)),
                "action": "EXPORT",
                "resource": "patient_report"
            }
        ]

        for action in user_actions:
            app_log = LogForwarderFormat.create_application_log(
                timestamp=action["timestamp"].strftime("%Y-%m-%d %H:%M:%S.%f")[:-3],
                platform=platform,
                app_name=app_name,
                user_id=user_id,
                ip_address=ip_address,
                action=action["action"],
                resource=action["resource"],
                log_type=LogType.ENDUSER,
                status=OperationStatus.SUCCESS
            )
            logs.append(app_log)

        return logs

    @staticmethod
    def generate_admin_session_logs():
        """Generate logs for an admin maintenance session"""
        logs = []
        timestamp_base = datetime.now()
        admin_user = "admin@lilly.com"
        app_name = "admin-console"
        platform = "CFC"
        ip_address = "192.168.1.1"

        # 1. Admin login
        login_log = LogForwarderFormat.create_login_log(
            timestamp=timestamp_base.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3],
            platform=platform,
            app_name=app_name,
            user_id=admin_user,
            ip_address=ip_address,
            status=OperationStatus.SUCCESS,
            auth_method="Azure_AD",
            session_id="admin-sess-" + datetime.now().strftime("%Y%m%d%H%M%S")
        )
        logs.append(login_log)

        # 2. Admin operations (MACD)
        operations = [
            {
                "timestamp": (timestamp_base + timedelta(seconds=10)),
                "op_type": "ADD",
                "object_type": "User",
                "object_id": "new_user@lilly.com",
                "new_value": "Doctor role in CFC platform",
                "reason": "New doctor onboarded"
            },
            {
                "timestamp": (timestamp_base + timedelta(seconds=30)),
                "op_type": "CHANGE",
                "object_type": "Role",
                "object_id": "viewer-role",
                "old_value": "read-only access",
                "new_value": "read-only + export access",
                "reason": "Permissions update for auditors"
            },
            {
                "timestamp": (timestamp_base + timedelta(seconds=50)),
                "op_type": "CHANGE",
                "object_type": "Configuration",
                "object_id": "session-timeout",
                "old_value": "15 minutes",
                "new_value": "30 minutes",
                "reason": "User feedback - reduce timeouts"
            }
        ]

        for op in operations:
            macd_log = LogForwarderFormat.create_macd_log(
                timestamp=op["timestamp"].strftime("%Y-%m-%d %H:%M:%S.%f")[:-3],
                platform=platform,
                app_name=app_name,
                user_id=admin_user,
                ip_address=ip_address,
                operation_type=op["op_type"],
                object_type=op["object_type"],
                object_id=op["object_id"],
                status=OperationStatus.SUCCESS,
                old_value=op.get("old_value", ""),
                new_value=op.get("new_value", ""),
                reason=op["reason"]
            )
            logs.append(macd_log)

        return logs

    @staticmethod
    def generate_api_integration_logs():
        """Generate logs for API integration between systems"""
        logs = []
        timestamp_base = datetime.now()
        platform = "CFC"

        # Scenario: HIS system calling patient data service
        inbound_apis = [
            {
                "timestamp": timestamp_base,
                "api_name": "searchPatients",
                "method": "POST",
                "path": "/api/v2/patients/search",
                "remote_system": "HIS-System",
                "user": "his_integration@partner.com",
                "ip": "198.51.100.50",
                "status": 200,
                "duration": 145,
                "request_size": 512,
                "response_size": 2048
            },
            {
                "timestamp": timestamp_base + timedelta(seconds=15),
                "api_name": "getPatientMedications",
                "method": "GET",
                "path": "/api/v2/patients/P123456/medications",
                "remote_system": "HIS-System",
                "user": "his_integration@partner.com",
                "ip": "198.51.100.50",
                "status": 200,
                "duration": 89,
                "request_size": 256,
                "response_size": 1024
            }
        ]

        for api in inbound_apis:
            inbound_log = LogForwarderFormat.create_api_log(
                timestamp=api["timestamp"].strftime("%Y-%m-%d %H:%M:%S.%f")[:-3],
                platform=platform,
                app_name="data-service",
                user_id=api["user"],
                ip_address=api["ip"],
                api_direction=ApiDirection.INBOUND,
                api_name=api["api_name"],
                api_version="v2",
                request_method=api["method"],
                request_path=api["path"],
                remote_system=api["remote_system"],
                status_code=api["status"],
                response_status=OperationStatus.SUCCESS,
                request_size=api["request_size"],
                response_size=api["response_size"],
                duration_ms=api["duration"]
            )
            logs.append(inbound_log)

        # Scenario: Our system calling ERP for order creation
        outbound_apis = [
            {
                "timestamp": timestamp_base + timedelta(seconds=30),
                "api_name": "createOrder",
                "method": "POST",
                "path": "/api/v1/orders",
                "remote_system": "ERP-System",
                "user": "app-integration@lilly.com",
                "ip": "192.168.1.50",
                "status": 201,
                "duration": 320,
                "request_size": 1024,
                "response_size": 512
            },
            {
                "timestamp": timestamp_base + timedelta(seconds=45),
                "api_name": "updateOrderStatus",
                "method": "PATCH",
                "path": "/api/v1/orders/ORD-2024-001",
                "remote_system": "ERP-System",
                "user": "app-integration@lilly.com",
                "ip": "192.168.1.50",
                "status": 200,
                "duration": 215,
                "request_size": 256,
                "response_size": 384
            }
        ]

        for api in outbound_apis:
            outbound_log = LogForwarderFormat.create_api_log(
                timestamp=api["timestamp"].strftime("%Y-%m-%d %H:%M:%S.%f")[:-3],
                platform=platform,
                app_name="integration-service",
                user_id=api["user"],
                ip_address=api["ip"],
                api_direction=ApiDirection.OUTBOUND,
                api_name=api["api_name"],
                api_version="v1",
                request_method=api["method"],
                request_path=api["path"],
                remote_system=api["remote_system"],
                status_code=api["status"],
                response_status=OperationStatus.SUCCESS,
                request_size=api["request_size"],
                response_size=api["response_size"],
                duration_ms=api["duration"]
            )
            logs.append(outbound_log)

        # Error scenario: Failed API call
        error_log = LogForwarderFormat.create_api_log(
            timestamp=(timestamp_base + timedelta(seconds=60)).strftime("%Y-%m-%d %H:%M:%S.%f")[:-3],
            platform=platform,
            app_name="data-service",
            user_id="batch_job@lilly.com",
            ip_address="192.168.1.100",
            api_direction=ApiDirection.OUTBOUND,
            api_name="syncDatabase",
            api_version="v1",
            request_method="POST",
            request_path="/api/v1/sync",
            remote_system="backup-service",
            status_code=500,
            response_status=OperationStatus.ERROR,
            request_size=2048,
            response_size=128,
            duration_ms=5000,
            error_message="Database connection timeout after 5 seconds"
        )
        logs.append(error_log)

        return logs

    @staticmethod
    def generate_platform_event_logs():
        """Generate platform/infrastructure logs"""
        logs = []
        timestamp_base = datetime.now()
        platform = "CFC"

        events = [
            {
                "timestamp": timestamp_base,
                "event_type": "CloudTrail",
                "event_name": "CreateBucket",
                "resource": "arn:aws:s3:::cfc-new-bucket",
                "user": "admin@lilly.com",
                "ip": "192.168.1.1",
                "status": OperationStatus.SUCCESS
            },
            {
                "timestamp": timestamp_base + timedelta(seconds=30),
                "event_type": "GuardDuty",
                "event_name": "UnauthorizedAccess",
                "resource": "i-0123456789abcdef0",
                "user": "system",
                "ip": "192.168.1.100",
                "status": OperationStatus.SUCCESS,
                "details": "Suspicious login attempts detected"
            },
            {
                "timestamp": timestamp_base + timedelta(seconds=60),
                "event_type": "Config",
                "event_name": "ConfigurationChange",
                "resource": "sg-12345678",
                "user": "automation@lilly.com",
                "ip": "192.168.1.50",
                "status": OperationStatus.SUCCESS,
                "details": "Security group rule added"
            }
        ]

        for event in events:
            platform_log = LogForwarderFormat.create_platform_log(
                timestamp=event["timestamp"].strftime("%Y-%m-%d %H:%M:%S.%f")[:-3],
                platform=platform,
                app_name="infrastructure",
                user_id=event["user"],
                ip_address=event["ip"],
                event_type=event["event_type"],
                event_name=event["event_name"],
                resource_id=event["resource"],
                status=event["status"],
                details=event.get("details", "")
            )
            logs.append(platform_log)

        return logs


def main():
    """Main demonstration"""
    print("=" * 80)
    print("CFC SOC LOG FORWARDER - PRACTICAL INTEGRATION EXAMPLES")
    print("=" * 80)

    # Example 1: User session logs
    print("\n[1] REGULAR USER SESSION LOGS")
    print("-" * 80)
    user_logs = LogForwarderIntegration.generate_session_logs()
    for log in user_logs:
        print(log.to_log_entry())
    LogForwarderIntegration.export_logs_to_file(user_logs, "logs_user_session.txt")

    # Example 2: Admin session logs
    print("\n[2] ADMIN MAINTENANCE SESSION LOGS")
    print("-" * 80)
    admin_logs = LogForwarderIntegration.generate_admin_session_logs()
    for log in admin_logs:
        print(log.to_log_entry())
    LogForwarderIntegration.export_logs_to_file(admin_logs, "logs_admin_session.txt")

    # Example 3: API integration logs
    print("\n[3] API INTEGRATION LOGS (INBOUND + OUTBOUND + ERRORS)")
    print("-" * 80)
    api_logs = LogForwarderIntegration.generate_api_integration_logs()
    for log in api_logs:
        print(log.to_log_entry())
    LogForwarderIntegration.export_logs_to_file(api_logs, "logs_api_integration.txt")

    # Example 4: Platform event logs
    print("\n[4] PLATFORM/INFRASTRUCTURE LOGS")
    print("-" * 80)
    platform_logs = LogForwarderIntegration.generate_platform_event_logs()
    for log in platform_logs:
        print(log.to_log_entry())
    LogForwarderIntegration.export_logs_to_file(platform_logs, "logs_platform_events.txt")

    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"User Session Logs: {len(user_logs)} entries")
    print(f"Admin Session Logs: {len(admin_logs)} entries")
    print(f"API Integration Logs: {len(api_logs)} entries")
    print(f"Platform Event Logs: {len(platform_logs)} entries")
    print(f"Total Logs Generated: {len(user_logs) + len(admin_logs) + len(api_logs) + len(platform_logs)}")
    print("\nLog files exported:")
    print("  - logs_user_session.txt")
    print("  - logs_admin_session.txt")
    print("  - logs_api_integration.txt")
    print("  - logs_platform_events.txt")
    print("\nAll logs follow CFC SOC Logging Guidelines 4.0 format specifications:")
    print("  ✓ Space-separated columns (per LOG-8)")
    print("  ✓ Platform, App, and API types supported")
    print("  ✓ Ready for CloudWatch/S3 ingestion")


if __name__ == "__main__":
    main()
