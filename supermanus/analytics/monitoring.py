#!/usr/bin/env python3
"""
SuperManUS Task Monitoring
Real-time monitoring and event tracking for task enforcement
"""

import json
import time
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable, Union
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
import logging
from enum import Enum


class EventType(Enum):
    """Types of monitoring events"""
    TASK_STARTED = "task_started"
    TASK_COMPLETED = "task_completed"
    TASK_FAILED = "task_failed"
    DEVIATION_ATTEMPT = "deviation_attempt"
    VALIDATION_APPROVED = "validation_approved"
    VALIDATION_REJECTED = "validation_rejected"
    WORK_LOG_CREATED = "work_log_created"
    SESSION_STARTED = "session_started"
    SESSION_ENDED = "session_ended"
    INTEGRATION_EVENT = "integration_event"
    ERROR_OCCURRED = "error_occurred"
    WARNING_ISSUED = "warning_issued"
    METRIC_THRESHOLD = "metric_threshold"
    BOTTLENECK_DETECTED = "bottleneck_detected"


@dataclass
class MonitoringEvent:
    """Single monitoring event"""
    event_type: EventType
    timestamp: str
    data: Dict[str, Any]
    developer: Optional[str] = None
    task_id: Optional[str] = None
    session_id: Optional[str] = None
    severity: str = "info"  # info, warning, error, critical
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        result = asdict(self)
        result["event_type"] = self.event_type.value
        return result


@dataclass
class MonitoringMetrics:
    """Real-time monitoring metrics"""
    events_per_minute: float
    deviation_attempts_per_hour: float
    avg_task_duration: float
    current_active_tasks: int
    validation_success_rate: float
    last_updated: str


class EventBuffer:
    """Thread-safe event buffer with size limit"""
    
    def __init__(self, max_size: int = 10000):
        self.max_size = max_size
        self.events = deque(maxlen=max_size)
        self.lock = threading.Lock()
    
    def add(self, event: MonitoringEvent):
        """Add event to buffer"""
        with self.lock:
            self.events.append(event)
    
    def get_recent(self, count: int = 100) -> List[MonitoringEvent]:
        """Get recent events"""
        with self.lock:
            return list(self.events)[-count:]
    
    def get_by_type(self, event_type: EventType, hours: int = 24) -> List[MonitoringEvent]:
        """Get events by type within time window"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        with self.lock:
            filtered_events = []
            for event in self.events:
                try:
                    event_time = datetime.fromisoformat(event.timestamp)
                    if event_time >= cutoff_time and event.event_type == event_type:
                        filtered_events.append(event)
                except ValueError:
                    continue
            
            return filtered_events
    
    def clear_old_events(self, hours: int = 168):  # 1 week default
        """Clear events older than specified hours"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        with self.lock:
            while self.events and self._is_event_old(self.events[0], cutoff_time):
                self.events.popleft()
    
    def _is_event_old(self, event: MonitoringEvent, cutoff_time: datetime) -> bool:
        """Check if event is older than cutoff time"""
        try:
            event_time = datetime.fromisoformat(event.timestamp)
            return event_time < cutoff_time
        except ValueError:
            return True  # Remove invalid timestamps


class AlertRule:
    """Rule for triggering alerts based on events"""
    
    def __init__(
        self, 
        name: str, 
        condition: Callable[[List[MonitoringEvent]], bool], 
        action: Callable[[List[MonitoringEvent]], None],
        cooldown_minutes: int = 30
    ):
        self.name = name
        self.condition = condition
        self.action = action
        self.cooldown_minutes = cooldown_minutes
        self.last_triggered = None
    
    def check_and_trigger(self, events: List[MonitoringEvent]) -> bool:
        """Check condition and trigger action if needed"""
        # Check cooldown
        if self.last_triggered:
            time_since_last = datetime.now() - self.last_triggered
            if time_since_last < timedelta(minutes=self.cooldown_minutes):
                return False
        
        # Check condition
        if self.condition(events):
            try:
                self.action(events)
                self.last_triggered = datetime.now()
                return True
            except Exception as e:
                logging.error(f"Alert action failed for {self.name}: {e}")
        
        return False


class TaskMonitor:
    """
    Real-time monitoring system for SuperManUS task enforcement
    Tracks events, metrics, and triggers alerts
    """
    
    def __init__(
        self, 
        session_state_path: str = "SESSION_STATE.json",
        monitoring_config: Optional[Dict[str, Any]] = None
    ):
        self.session_state_path = Path(session_state_path)
        self.config = monitoring_config or {}
        
        # Event handling
        self.event_buffer = EventBuffer(
            max_size=self.config.get("max_events", 10000)
        )
        self.event_handlers = defaultdict(list)
        self.alert_rules = []
        
        # Monitoring state
        self.monitoring_active = False
        self.monitoring_thread = None
        self.metrics_update_interval = self.config.get("metrics_interval", 60)  # seconds
        
        # Real-time metrics
        self.current_metrics = MonitoringMetrics(
            events_per_minute=0.0,
            deviation_attempts_per_hour=0.0,
            avg_task_duration=0.0,
            current_active_tasks=0,
            validation_success_rate=0.0,
            last_updated=datetime.now().isoformat()
        )
        
        # Setup logging
        self.setup_logging()
        
        # Setup default alert rules
        self.setup_default_alerts()
    
    def setup_logging(self):
        """Setup monitoring logging"""
        log_level = self.config.get("log_level", "INFO")
        logging.basicConfig(
            level=getattr(logging, log_level),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger("SuperManUS.Monitor")
    
    def setup_default_alerts(self):
        """Setup default monitoring alert rules"""
        
        # High deviation attempt rate
        def high_deviation_condition(events: List[MonitoringEvent]) -> bool:
            deviation_events = [e for e in events 
                              if e.event_type == EventType.DEVIATION_ATTEMPT]
            recent_deviations = [e for e in deviation_events 
                               if self._is_recent(e.timestamp, hours=1)]
            return len(recent_deviations) > 5
        
        def high_deviation_action(events: List[MonitoringEvent]):
            self.logger.warning("High deviation attempt rate detected")
            self._send_alert("High Deviation Rate", 
                           f"{len([e for e in events if e.event_type == EventType.DEVIATION_ATTEMPT])} deviation attempts in last hour")
        
        self.add_alert_rule("high_deviation_rate", high_deviation_condition, high_deviation_action)
        
        # Low validation success rate
        def low_validation_condition(events: List[MonitoringEvent]) -> bool:
            validation_events = [e for e in events 
                               if e.event_type in [EventType.VALIDATION_APPROVED, EventType.VALIDATION_REJECTED]]
            recent_validations = [e for e in validation_events 
                                if self._is_recent(e.timestamp, hours=2)]
            
            if len(recent_validations) < 3:  # Need minimum data
                return False
            
            approved = len([e for e in recent_validations if e.event_type == EventType.VALIDATION_APPROVED])
            success_rate = approved / len(recent_validations)
            return success_rate < 0.6
        
        def low_validation_action(events: List[MonitoringEvent]):
            self.logger.warning("Low validation success rate detected")
            self._send_alert("Low Validation Success", "Validation success rate below 60% in last 2 hours")
        
        self.add_alert_rule("low_validation_success", low_validation_condition, low_validation_action)
        
        # Task completion stall
        def task_stall_condition(events: List[MonitoringEvent]) -> bool:
            completion_events = [e for e in events 
                               if e.event_type == EventType.TASK_COMPLETED]
            recent_completions = [e for e in completion_events 
                                if self._is_recent(e.timestamp, hours=4)]
            return len(recent_completions) == 0
        
        def task_stall_action(events: List[MonitoringEvent]):
            self.logger.warning("Task completion stall detected")
            self._send_alert("Task Completion Stall", "No tasks completed in last 4 hours")
        
        self.add_alert_rule("task_completion_stall", task_stall_condition, task_stall_action)
    
    def _is_recent(self, timestamp: str, hours: int) -> bool:
        """Check if timestamp is within recent hours"""
        try:
            event_time = datetime.fromisoformat(timestamp)
            cutoff = datetime.now() - timedelta(hours=hours)
            return event_time >= cutoff
        except ValueError:
            return False
    
    def _send_alert(self, title: str, message: str, severity: str = "warning"):
        """Send alert (can be extended to integrate with external systems)"""
        alert_event = MonitoringEvent(
            event_type=EventType.WARNING_ISSUED,
            timestamp=datetime.now().isoformat(),
            data={"title": title, "message": message},
            severity=severity
        )
        
        self.record_event(alert_event)
        self.logger.warning(f"ALERT: {title} - {message}")
        
        # Future: integrate with Slack, email, PagerDuty, etc.
        alert_integrations = self.config.get("alert_integrations", [])
        for integration in alert_integrations:
            try:
                self._send_external_alert(integration, title, message, severity)
            except Exception as e:
                self.logger.error(f"Failed to send alert via {integration}: {e}")
    
    def _send_external_alert(self, integration: str, title: str, message: str, severity: str):
        """Send alert to external system (placeholder for future implementation)"""
        # This would integrate with Slack, email, PagerDuty, etc.
        pass
    
    def add_alert_rule(self, name: str, condition: Callable, action: Callable, cooldown_minutes: int = 30):
        """Add custom alert rule"""
        rule = AlertRule(name, condition, action, cooldown_minutes)
        self.alert_rules.append(rule)
        self.logger.info(f"Added alert rule: {name}")
    
    def record_event(self, event: MonitoringEvent):
        """Record a monitoring event"""
        self.event_buffer.add(event)
        
        # Trigger event handlers
        handlers = self.event_handlers.get(event.event_type, [])
        for handler in handlers:
            try:
                handler(event)
            except Exception as e:
                self.logger.error(f"Event handler failed: {e}")
    
    def on(self, event_type: EventType):
        """Decorator for event handlers"""
        def decorator(handler_func: Callable[[MonitoringEvent], None]):
            self.event_handlers[event_type].append(handler_func)
            return handler_func
        return decorator
    
    def on_task_start(self, handler: Callable[[MonitoringEvent], None]):
        """Register handler for task start events"""
        self.event_handlers[EventType.TASK_STARTED].append(handler)
    
    def on_task_completed(self, handler: Callable[[MonitoringEvent], None]):
        """Register handler for task completion events"""
        self.event_handlers[EventType.TASK_COMPLETED].append(handler)
    
    def on_deviation_attempt(self, handler: Callable[[MonitoringEvent], None]):
        """Register handler for deviation attempt events"""
        self.event_handlers[EventType.DEVIATION_ATTEMPT].append(handler)
    
    def on_validation_failed(self, handler: Callable[[MonitoringEvent], None]):
        """Register handler for validation failure events"""
        self.event_handlers[EventType.VALIDATION_REJECTED].append(handler)
    
    def start_monitoring(self):
        """Start real-time monitoring"""
        if self.monitoring_active:
            self.logger.warning("Monitoring already active")
            return
        
        self.monitoring_active = True
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitoring_thread.start()
        
        self.logger.info("SuperManUS monitoring started")
        
        # Record session start event
        self.record_event(MonitoringEvent(
            event_type=EventType.SESSION_STARTED,
            timestamp=datetime.now().isoformat(),
            data={"monitoring_config": self.config}
        ))
    
    def stop_monitoring(self):
        """Stop real-time monitoring"""
        if not self.monitoring_active:
            return
        
        self.monitoring_active = False
        
        if self.monitoring_thread and self.monitoring_thread.is_alive():
            self.monitoring_thread.join(timeout=5)
        
        self.logger.info("SuperManUS monitoring stopped")
        
        # Record session end event
        self.record_event(MonitoringEvent(
            event_type=EventType.SESSION_ENDED,
            timestamp=datetime.now().isoformat(),
            data={"session_duration": "calculated_elsewhere"}
        ))
    
    def _monitoring_loop(self):
        """Main monitoring loop"""
        while self.monitoring_active:
            try:
                # Update real-time metrics
                self._update_metrics()
                
                # Check alert rules
                self._check_alert_rules()
                
                # Clean old events
                self.event_buffer.clear_old_events()
                
                # Sleep until next update
                time.sleep(self.metrics_update_interval)
                
            except Exception as e:
                self.logger.error(f"Monitoring loop error: {e}")
                time.sleep(10)  # Brief pause before retry
    
    def _update_metrics(self):
        """Update real-time monitoring metrics"""
        now = datetime.now()
        one_hour_ago = now - timedelta(hours=1)
        one_minute_ago = now - timedelta(minutes=1)
        
        # Get recent events for calculation
        all_events = self.event_buffer.get_recent(1000)
        
        # Calculate events per minute
        recent_events = [e for e in all_events 
                        if self._is_recent(e.timestamp, hours=0) and 
                           datetime.fromisoformat(e.timestamp) >= one_minute_ago]
        events_per_minute = len(recent_events)
        
        # Calculate deviation attempts per hour
        deviation_events = [e for e in all_events 
                          if e.event_type == EventType.DEVIATION_ATTEMPT and 
                             self._is_recent(e.timestamp, hours=1)]
        deviation_attempts_per_hour = len(deviation_events)
        
        # Calculate validation success rate
        validation_events = [e for e in all_events 
                           if e.event_type in [EventType.VALIDATION_APPROVED, EventType.VALIDATION_REJECTED] and 
                              self._is_recent(e.timestamp, hours=1)]
        
        if validation_events:
            approved = len([e for e in validation_events if e.event_type == EventType.VALIDATION_APPROVED])
            validation_success_rate = approved / len(validation_events)
        else:
            validation_success_rate = 0.0
        
        # Get active tasks count from session state
        active_tasks_count = self._get_active_tasks_count()
        
        # Update metrics
        self.current_metrics = MonitoringMetrics(
            events_per_minute=events_per_minute,
            deviation_attempts_per_hour=deviation_attempts_per_hour,
            avg_task_duration=0.0,  # Would need more complex calculation
            current_active_tasks=active_tasks_count,
            validation_success_rate=validation_success_rate,
            last_updated=now.isoformat()
        )
    
    def _get_active_tasks_count(self) -> int:
        """Get current active tasks count from session state"""
        try:
            if not self.session_state_path.exists():
                return 0
            
            with open(self.session_state_path, 'r') as f:
                session_data = json.load(f)
            
            return len(session_data.get('active_tasks', []))
            
        except (json.JSONDecodeError, IOError):
            return 0
    
    def _check_alert_rules(self):
        """Check all alert rules"""
        recent_events = self.event_buffer.get_recent(500)
        
        for rule in self.alert_rules:
            try:
                rule.check_and_trigger(recent_events)
            except Exception as e:
                self.logger.error(f"Alert rule {rule.name} failed: {e}")
    
    def get_current_metrics(self) -> MonitoringMetrics:
        """Get current real-time metrics"""
        return self.current_metrics
    
    def get_event_summary(self, hours: int = 24) -> Dict[str, int]:
        """Get summary of events by type"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        event_counts = defaultdict(int)
        for event in self.event_buffer.get_recent(1000):
            try:
                event_time = datetime.fromisoformat(event.timestamp)
                if event_time >= cutoff_time:
                    event_counts[event.event_type.value] += 1
            except ValueError:
                continue
        
        return dict(event_counts)
    
    def get_developer_activity(self, hours: int = 24) -> Dict[str, Dict[str, int]]:
        """Get developer activity summary"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        developer_activity = defaultdict(lambda: defaultdict(int))
        
        for event in self.event_buffer.get_recent(1000):
            if not event.developer:
                continue
            
            try:
                event_time = datetime.fromisoformat(event.timestamp)
                if event_time >= cutoff_time:
                    developer_activity[event.developer][event.event_type.value] += 1
            except ValueError:
                continue
        
        return {dev: dict(activity) for dev, activity in developer_activity.items()}
    
    def generate_monitoring_report(self) -> Dict[str, Any]:
        """Generate comprehensive monitoring report"""
        return {
            "timestamp": datetime.now().isoformat(),
            "monitoring_status": "active" if self.monitoring_active else "inactive",
            "current_metrics": asdict(self.current_metrics),
            "event_summary_24h": self.get_event_summary(24),
            "developer_activity_24h": self.get_developer_activity(24),
            "alert_rules_count": len(self.alert_rules),
            "total_events_tracked": len(self.event_buffer.events),
            "recent_critical_events": [
                event.to_dict() for event in self.event_buffer.get_recent(50)
                if event.severity in ["error", "critical"]
            ]
        }
    
    def export_events_json(self, filepath: str, hours: int = 24):
        """Export recent events to JSON file"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        events_to_export = []
        for event in self.event_buffer.get_recent(1000):
            try:
                event_time = datetime.fromisoformat(event.timestamp)
                if event_time >= cutoff_time:
                    events_to_export.append(event.to_dict())
            except ValueError:
                continue
        
        export_data = {
            "export_timestamp": datetime.now().isoformat(),
            "time_range_hours": hours,
            "event_count": len(events_to_export),
            "events": events_to_export
        }
        
        with open(filepath, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        self.logger.info(f"Exported {len(events_to_export)} events to {filepath}")


# Convenience functions for creating common monitoring events

def create_task_start_event(task_id: str, developer: str, session_id: str = None) -> MonitoringEvent:
    """Create task start monitoring event"""
    return MonitoringEvent(
        event_type=EventType.TASK_STARTED,
        timestamp=datetime.now().isoformat(),
        data={"task_id": task_id},
        developer=developer,
        task_id=task_id,
        session_id=session_id
    )


def create_task_completion_event(task_id: str, developer: str, duration_minutes: float, session_id: str = None) -> MonitoringEvent:
    """Create task completion monitoring event"""
    return MonitoringEvent(
        event_type=EventType.TASK_COMPLETED,
        timestamp=datetime.now().isoformat(),
        data={"task_id": task_id, "duration_minutes": duration_minutes},
        developer=developer,
        task_id=task_id,
        session_id=session_id
    )


def create_deviation_event(action: str, justification: str, task_id: str, developer: str, session_id: str = None) -> MonitoringEvent:
    """Create deviation attempt monitoring event"""
    return MonitoringEvent(
        event_type=EventType.DEVIATION_ATTEMPT,
        timestamp=datetime.now().isoformat(),
        data={"action": action, "justification": justification, "blocked": True},
        developer=developer,
        task_id=task_id,
        session_id=session_id,
        severity="warning"
    )


def create_validation_event(approved: bool, action: str, justification: str, task_id: str, developer: str, session_id: str = None) -> MonitoringEvent:
    """Create validation result monitoring event"""
    event_type = EventType.VALIDATION_APPROVED if approved else EventType.VALIDATION_REJECTED
    
    return MonitoringEvent(
        event_type=event_type,
        timestamp=datetime.now().isoformat(),
        data={"action": action, "justification": justification, "approved": approved},
        developer=developer,
        task_id=task_id,
        session_id=session_id,
        severity="info" if approved else "warning"
    )