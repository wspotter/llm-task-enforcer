#!/usr/bin/env python3
"""
SuperManUS Task Enforcement Metrics
Comprehensive analytics for task discipline and productivity measurement
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, asdict
from collections import defaultdict, Counter
import statistics


@dataclass
class MetricPoint:
    """Single metric data point"""
    timestamp: str
    value: Union[int, float]
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class ProductivityPoint:
    """Productivity metric data point"""
    timestamp: str
    tasks_completed: int
    tasks_started: int
    deviation_attempts: int
    review_time: float
    developer: Optional[str] = None


@dataclass
class CompletionPrediction:
    """Task completion prediction"""
    task_id: str
    estimated_completion: str
    confidence: float
    factors: List[str]
    current_progress: float


@dataclass
class BottleneckReport:
    """System bottleneck analysis"""
    bottleneck_type: str
    severity: str  # "low", "medium", "high", "critical"
    description: str
    affected_tasks: List[str]
    suggested_actions: List[str]
    estimated_impact: str


@dataclass
class RiskAssessment:
    """Project risk assessment"""
    overall_risk: str  # "low", "medium", "high", "critical"
    risk_factors: List[Dict[str, Any]]
    recommendations: List[str]
    risk_score: float


class TaskEnforcementMetrics:
    """
    Comprehensive metrics and analytics for SuperManUS task enforcement
    Tracks productivity, quality, and deviation prevention effectiveness
    """
    
    def __init__(
        self,
        session_state_path: str = "SESSION_STATE.json",
        work_logs_dir: str = "work_logs",
        history_days: int = 30
    ):
        self.session_state_path = Path(session_state_path)
        self.work_logs_dir = Path(work_logs_dir)
        self.history_days = history_days
        
        # Load session state
        self.session_data = self._load_session_state()
        
        # Initialize metrics storage
        self.metrics_cache = {}
        self.last_update = None
    
    def _load_session_state(self) -> Dict[str, Any]:
        """Load current session state"""
        if not self.session_state_path.exists():
            return {}
        
        try:
            with open(self.session_state_path, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {}
    
    def _get_work_logs(self) -> List[Dict[str, Any]]:
        """Get all work log files and parse metadata"""
        if not self.work_logs_dir.exists():
            return []
        
        work_logs = []
        for log_file in self.work_logs_dir.glob("*.md"):
            try:
                with open(log_file, 'r') as f:
                    content = f.read()
                
                # Extract metadata from work log
                metadata = self._parse_work_log_metadata(content, log_file.name)
                if metadata:
                    work_logs.append(metadata)
            
            except IOError:
                continue
        
        return sorted(work_logs, key=lambda x: x.get('timestamp', ''))
    
    def _parse_work_log_metadata(self, content: str, filename: str) -> Dict[str, Any]:
        """Parse metadata from work log content"""
        metadata = {
            'filename': filename,
            'timestamp': self._extract_timestamp_from_content(content),
            'task_id': self._extract_task_id_from_content(content),
            'developer': self._extract_developer_from_content(content),
            'steps_count': content.count('### Step'),
            'validation_checks': content.count('- [x]'),
            'total_checks': content.count('- [ ]') + content.count('- [x]'),
            'file_modifications': self._count_file_modifications(content),
            'duration_estimate': self._extract_duration_estimate(content)
        }
        
        # Calculate completion rate
        if metadata['total_checks'] > 0:
            metadata['completion_rate'] = metadata['validation_checks'] / metadata['total_checks']
        else:
            metadata['completion_rate'] = 0.0
        
        return metadata
    
    def _extract_timestamp_from_content(self, content: str) -> str:
        """Extract timestamp from work log content"""
        import re
        
        # Look for ISO timestamp pattern
        iso_pattern = r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}'
        match = re.search(iso_pattern, content)
        if match:
            return match.group(0)
        
        # Fallback to current time
        return datetime.now().isoformat()
    
    def _extract_task_id_from_content(self, content: str) -> str:
        """Extract task ID from work log content"""
        import re
        
        # Look for task ID patterns
        patterns = [
            r'Task ID:\*\*\s*([^\n]+)',
            r'# Work Log for ([^\n]+)',
            r'Task:\s*([^\n]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return "Unknown"
    
    def _extract_developer_from_content(self, content: str) -> str:
        """Extract developer name from work log content"""
        import re
        
        patterns = [
            r'Developer:\*\*\s*([^\n]+)',
            r'Assigned to:\s*([^\n]+)',
            r'Author:\s*([^\n]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return "Unknown"
    
    def _count_file_modifications(self, content: str) -> int:
        """Count file modifications mentioned in work log"""
        import re
        
        # Look for file modification patterns
        patterns = [
            r'Files Created/Modified:.*?(?=\n##|\n###|\Z)',
            r'Modified files?:.*?(?=\n##|\n###|\Z)',
            r'Created:.*?(?=\n##|\n###|\Z)'
        ]
        
        total_files = 0
        for pattern in patterns:
            matches = re.findall(pattern, content, re.DOTALL | re.IGNORECASE)
            for match in matches:
                # Count file paths mentioned
                file_count = len(re.findall(r'\S+\.\w+', match))
                total_files += file_count
        
        return total_files
    
    def _extract_duration_estimate(self, content: str) -> float:
        """Extract duration estimate from work log"""
        import re
        
        patterns = [
            r'Estimated Duration:\*\*\s*(\d+\.?\d*)\s*(hours?|hrs?|minutes?|mins?)',
            r'Duration:\s*(\d+\.?\d*)\s*(hours?|hrs?|minutes?|mins?)',
            r'Time spent:\s*(\d+\.?\d*)\s*(hours?|hrs?|minutes?|mins?)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                value = float(match.group(1))
                unit = match.group(2).lower()
                
                # Convert to hours
                if 'min' in unit:
                    value = value / 60
                
                return value
        
        return 0.0
    
    def task_completion_rate(self) -> float:
        """Calculate overall task completion rate"""
        completed = len(self.session_data.get('completed_tasks', []))
        active = len(self.session_data.get('active_tasks', []))
        total = completed + active
        
        if total == 0:
            return 0.0
        
        return completed / total
    
    def average_task_duration(self) -> timedelta:
        """Calculate average task duration from work logs"""
        work_logs = self._get_work_logs()
        
        if not work_logs:
            return timedelta(0)
        
        durations = [log.get('duration_estimate', 0.0) for log in work_logs]
        durations = [d for d in durations if d > 0]  # Filter out zero durations
        
        if not durations:
            return timedelta(0)
        
        avg_hours = statistics.mean(durations)
        return timedelta(hours=avg_hours)
    
    def deviation_prevention_rate(self) -> float:
        """Calculate deviation prevention effectiveness"""
        # This would typically be tracked by the enforcement system
        # For now, we'll estimate based on work log quality
        work_logs = self._get_work_logs()
        
        if not work_logs:
            return 1.0  # Assume perfect if no data
        
        # High-quality work logs suggest good task discipline
        quality_scores = []
        for log in work_logs:
            quality_score = 0.0
            
            # Check for task alignment
            if log.get('task_id') != "Unknown":
                quality_score += 0.3
            
            # Check for structured documentation
            if log.get('steps_count', 0) > 0:
                quality_score += 0.3
            
            # Check for validation
            if log.get('completion_rate', 0) > 0.5:
                quality_score += 0.2
            
            # Check for file tracking
            if log.get('file_modifications', 0) > 0:
                quality_score += 0.2
            
            quality_scores.append(quality_score)
        
        if not quality_scores:
            return 0.5
        
        return statistics.mean(quality_scores)
    
    def completion_quality_score(self) -> float:
        """Calculate task completion quality score"""
        work_logs = self._get_work_logs()
        
        if not work_logs:
            return 0.0
        
        # Calculate quality based on work log completeness
        quality_factors = []
        
        for log in work_logs:
            factors = [
                log.get('completion_rate', 0.0),  # Validation check completion
                min(log.get('steps_count', 0) / 5, 1.0),  # Documentation thoroughness
                min(log.get('file_modifications', 0) / 3, 1.0),  # Implementation scope
                1.0 if log.get('duration_estimate', 0) > 0 else 0.0  # Time tracking
            ]
            
            quality_factors.append(statistics.mean(factors))
        
        return statistics.mean(quality_factors)
    
    def task_rework_rate(self) -> float:
        """Calculate rate of tasks requiring rework"""
        # This would be tracked by monitoring failed validations
        # For now, estimate based on work log patterns
        work_logs = self._get_work_logs()
        
        if not work_logs:
            return 0.0
        
        # Look for indicators of rework
        rework_indicators = 0
        total_logs = len(work_logs)
        
        for log in work_logs:
            # Low completion rate suggests issues
            if log.get('completion_rate', 1.0) < 0.7:
                rework_indicators += 1
            
            # Excessive steps might indicate problems
            if log.get('steps_count', 0) > 10:
                rework_indicators += 0.5
        
        return min(rework_indicators / total_logs, 1.0)
    
    def human_review_efficiency(self) -> float:
        """Calculate human review process efficiency"""
        # This would be tracked by the human validation system
        # For now, estimate based on completion patterns
        
        completed_tasks = len(self.session_data.get('completed_tasks', []))
        total_tasks = completed_tasks + len(self.session_data.get('active_tasks', []))
        
        if total_tasks == 0:
            return 0.0
        
        # Assume higher completion rates indicate efficient review
        completion_rate = completed_tasks / total_tasks
        
        # Factor in work log quality (indicates thorough preparation)
        quality_score = self.completion_quality_score()
        
        # Combine metrics
        efficiency = (completion_rate * 0.7) + (quality_score * 0.3)
        return min(efficiency, 1.0)
    
    def team_productivity_metrics(self) -> Dict[str, float]:
        """Calculate productivity metrics by team member"""
        work_logs = self._get_work_logs()
        
        if not work_logs:
            return {}
        
        developer_metrics = defaultdict(lambda: {
            'tasks_worked': 0,
            'total_steps': 0,
            'total_files': 0,
            'total_duration': 0.0,
            'quality_scores': []
        })
        
        # Aggregate metrics by developer
        for log in work_logs:
            dev = log.get('developer', 'Unknown')
            metrics = developer_metrics[dev]
            
            metrics['tasks_worked'] += 1
            metrics['total_steps'] += log.get('steps_count', 0)
            metrics['total_files'] += log.get('file_modifications', 0)
            metrics['total_duration'] += log.get('duration_estimate', 0.0)
            metrics['quality_scores'].append(log.get('completion_rate', 0.0))
        
        # Calculate productivity scores
        productivity = {}
        for dev, metrics in developer_metrics.items():
            if metrics['tasks_worked'] == 0:
                continue
            
            # Calculate various productivity indicators
            avg_steps_per_task = metrics['total_steps'] / metrics['tasks_worked']
            avg_files_per_task = metrics['total_files'] / metrics['tasks_worked']
            avg_quality = statistics.mean(metrics['quality_scores']) if metrics['quality_scores'] else 0.0
            
            # Productivity score (normalized)
            productivity_score = (
                min(avg_steps_per_task / 5, 1.0) * 0.3 +  # Documentation thoroughness
                min(avg_files_per_task / 3, 1.0) * 0.3 +   # Implementation scope
                avg_quality * 0.4                           # Quality score
            )
            
            productivity[dev] = {
                'tasks_worked': metrics['tasks_worked'],
                'avg_steps_per_task': avg_steps_per_task,
                'avg_files_per_task': avg_files_per_task,
                'avg_quality_score': avg_quality,
                'total_duration_hours': metrics['total_duration'],
                'productivity_score': productivity_score
            }
        
        return productivity
    
    def collaboration_effectiveness(self) -> float:
        """Calculate team collaboration effectiveness"""
        team_assignments = self.session_data.get('team_assignments', {})
        
        if not team_assignments:
            return 0.0
        
        # Calculate distribution of work
        task_counts = [len(tasks) for tasks in team_assignments.values()]
        
        if not task_counts:
            return 0.0
        
        # Good collaboration shows balanced work distribution
        work_balance = 1.0 - (statistics.stdev(task_counts) / statistics.mean(task_counts))
        work_balance = max(0.0, work_balance)
        
        # Factor in team size (larger teams need better coordination)
        team_size = len(team_assignments)
        size_factor = min(team_size / 5, 1.0)  # Optimal around 5 people
        
        # Overall collaboration score
        collaboration_score = work_balance * (1.0 - size_factor * 0.2)
        return min(collaboration_score, 1.0)
    
    def get_completion_trend(
        self,
        start_date: datetime,
        end_date: datetime,
        granularity: str = "day"
    ) -> List[MetricPoint]:
        """Get task completion trend over time"""
        work_logs = self._get_work_logs()
        
        # Filter logs by date range
        filtered_logs = []
        for log in work_logs:
            try:
                log_date = datetime.fromisoformat(log.get('timestamp', ''))
                if start_date <= log_date <= end_date:
                    filtered_logs.append(log)
            except ValueError:
                continue
        
        # Group by time granularity
        time_buckets = defaultdict(int)
        
        for log in filtered_logs:
            try:
                log_date = datetime.fromisoformat(log.get('timestamp', ''))
                
                if granularity == "hour":
                    bucket_key = log_date.strftime("%Y-%m-%d %H:00")
                elif granularity == "day":
                    bucket_key = log_date.strftime("%Y-%m-%d")
                elif granularity == "week":
                    # Get Monday of the week
                    monday = log_date - timedelta(days=log_date.weekday())
                    bucket_key = monday.strftime("%Y-%m-%d")
                else:
                    bucket_key = log_date.strftime("%Y-%m-%d")
                
                time_buckets[bucket_key] += 1
                
            except ValueError:
                continue
        
        # Convert to MetricPoint objects
        trend_points = []
        for timestamp, count in sorted(time_buckets.items()):
            trend_points.append(MetricPoint(
                timestamp=timestamp,
                value=count,
                metadata={"granularity": granularity}
            ))
        
        return trend_points
    
    def get_productivity_trend(
        self,
        developer: Optional[str] = None,
        task_type: Optional[str] = None
    ) -> List[ProductivityPoint]:
        """Get productivity trend for developer or task type"""
        work_logs = self._get_work_logs()
        
        # Filter by developer and/or task type
        filtered_logs = work_logs
        if developer:
            filtered_logs = [log for log in filtered_logs 
                           if log.get('developer') == developer]
        
        if task_type:
            filtered_logs = [log for log in filtered_logs
                           if task_type.lower() in log.get('task_id', '').lower()]
        
        # Group by day and calculate productivity metrics
        daily_productivity = defaultdict(lambda: {
            'tasks_completed': 0,
            'tasks_started': 0,
            'total_steps': 0,
            'total_files': 0
        })
        
        for log in filtered_logs:
            try:
                log_date = datetime.fromisoformat(log.get('timestamp', ''))
                day_key = log_date.strftime("%Y-%m-%d")
                
                daily_metrics = daily_productivity[day_key]
                daily_metrics['tasks_started'] += 1
                
                # Consider task completed if high completion rate
                if log.get('completion_rate', 0.0) > 0.8:
                    daily_metrics['tasks_completed'] += 1
                
                daily_metrics['total_steps'] += log.get('steps_count', 0)
                daily_metrics['total_files'] += log.get('file_modifications', 0)
                
            except ValueError:
                continue
        
        # Convert to ProductivityPoint objects
        productivity_points = []
        for day, metrics in sorted(daily_productivity.items()):
            productivity_points.append(ProductivityPoint(
                timestamp=day,
                tasks_completed=metrics['tasks_completed'],
                tasks_started=metrics['tasks_started'],
                deviation_attempts=0,  # Would be tracked separately
                review_time=0.0,  # Would be tracked separately
                developer=developer
            ))
        
        return productivity_points
    
    def predict_task_completion(
        self,
        task_id: str,
        current_progress: Optional[float] = None
    ) -> CompletionPrediction:
        """Predict when a task will be completed"""
        # Get historical data for similar tasks
        work_logs = self._get_work_logs()
        
        # Find similar tasks (by type or developer)
        similar_tasks = []
        task_type = task_id.split('.')[0] if '.' in task_id else task_id[:4]
        
        for log in work_logs:
            log_task_id = log.get('task_id', '')
            if (task_type in log_task_id or 
                log_task_id.split('.')[0] == task_type):
                similar_tasks.append(log)
        
        if not similar_tasks:
            # No historical data, make conservative estimate
            return CompletionPrediction(
                task_id=task_id,
                estimated_completion=(datetime.now() + timedelta(hours=8)).isoformat(),
                confidence=0.3,
                factors=["No historical data available"],
                current_progress=current_progress or 0.0
            )
        
        # Calculate average completion time
        durations = [log.get('duration_estimate', 4.0) for log in similar_tasks]
        avg_duration_hours = statistics.mean(durations)
        
        # Adjust based on current progress
        if current_progress:
            remaining_work = 1.0 - current_progress
            estimated_hours = avg_duration_hours * remaining_work
        else:
            estimated_hours = avg_duration_hours
        
        estimated_completion = datetime.now() + timedelta(hours=estimated_hours)
        
        # Calculate confidence based on data quality
        confidence = min(len(similar_tasks) / 5, 1.0)  # Higher with more data points
        
        factors = [
            f"Based on {len(similar_tasks)} similar tasks",
            f"Average duration: {avg_duration_hours:.1f} hours",
            f"Current progress: {(current_progress or 0.0) * 100:.0f}%"
        ]
        
        return CompletionPrediction(
            task_id=task_id,
            estimated_completion=estimated_completion.isoformat(),
            confidence=confidence,
            factors=factors,
            current_progress=current_progress or 0.0
        )
    
    def analyze_bottlenecks(self) -> List[BottleneckReport]:
        """Analyze system bottlenecks and constraints"""
        bottlenecks = []
        
        # Analyze team workload distribution
        team_assignments = self.session_data.get('team_assignments', {})
        if team_assignments:
            task_counts = [len(tasks) for tasks in team_assignments.values()]
            if task_counts:
                max_tasks = max(task_counts)
                avg_tasks = statistics.mean(task_counts)
                
                if max_tasks > avg_tasks * 1.5:
                    overloaded_devs = [dev for dev, tasks in team_assignments.items()
                                     if len(tasks) == max_tasks]
                    
                    bottlenecks.append(BottleneckReport(
                        bottleneck_type="workload_imbalance",
                        severity="medium",
                        description=f"Workload imbalance detected. Some developers have {max_tasks} tasks vs average of {avg_tasks:.1f}",
                        affected_tasks=[task for dev in overloaded_devs 
                                      for task in team_assignments[dev]],
                        suggested_actions=[
                            "Redistribute tasks more evenly across team",
                            "Consider adding resources to overloaded developers",
                            "Review task complexity and size"
                        ],
                        estimated_impact="Could delay project by 20-30%"
                    ))
        
        # Analyze task completion patterns
        work_logs = self._get_work_logs()
        if work_logs:
            # Check for consistently low completion rates
            low_quality_tasks = [log for log in work_logs 
                               if log.get('completion_rate', 0.0) < 0.5]
            
            if len(low_quality_tasks) > len(work_logs) * 0.3:
                bottlenecks.append(BottleneckReport(
                    bottleneck_type="quality_issues",
                    severity="high",
                    description=f"{len(low_quality_tasks)} tasks show low completion quality",
                    affected_tasks=[log.get('task_id', 'Unknown') for log in low_quality_tasks],
                    suggested_actions=[
                        "Improve work log template and guidance",
                        "Increase human review frequency",
                        "Provide additional training on task documentation",
                        "Review task complexity and scope"
                    ],
                    estimated_impact="Significant rework and delays expected"
                ))
        
        # Check for blocked tasks
        active_tasks = self.session_data.get('active_tasks', [])
        blockers = self.session_data.get('blockers', [])
        
        if blockers and len(blockers) > len(active_tasks) * 0.2:
            bottlenecks.append(BottleneckReport(
                bottleneck_type="external_dependencies",
                severity="high" if len(blockers) > len(active_tasks) * 0.4 else "medium",
                description=f"{len(blockers)} blockers identified for active tasks",
                affected_tasks=active_tasks,
                suggested_actions=[
                    "Prioritize resolution of external blockers",
                    "Identify alternative approaches for blocked work",
                    "Improve stakeholder communication",
                    "Create contingency plans for dependencies"
                ],
                estimated_impact="Project timeline at risk"
            ))
        
        return bottlenecks
    
    def assess_project_risks(self) -> RiskAssessment:
        """Assess overall project risks"""
        risk_factors = []
        risk_score = 0.0
        
        # Task completion risk
        completion_rate = self.task_completion_rate()
        if completion_rate < 0.3:
            risk_factors.append({
                "factor": "Low task completion rate",
                "severity": "high",
                "description": f"Only {completion_rate:.1%} of tasks completed",
                "impact": "Project delivery at risk"
            })
            risk_score += 0.3
        elif completion_rate < 0.6:
            risk_factors.append({
                "factor": "Moderate task completion rate",
                "severity": "medium", 
                "description": f"{completion_rate:.1%} of tasks completed",
                "impact": "May miss deadlines"
            })
            risk_score += 0.15
        
        # Quality risk
        quality_score = self.completion_quality_score()
        if quality_score < 0.5:
            risk_factors.append({
                "factor": "Low quality score",
                "severity": "high",
                "description": f"Quality score: {quality_score:.1%}",
                "impact": "High rework and technical debt risk"
            })
            risk_score += 0.25
        elif quality_score < 0.7:
            risk_factors.append({
                "factor": "Moderate quality concerns",
                "severity": "medium",
                "description": f"Quality score: {quality_score:.1%}",
                "impact": "Some rework expected"
            })
            risk_score += 0.1
        
        # Team productivity risk
        team_metrics = self.team_productivity_metrics()
        if team_metrics:
            low_productivity_devs = [dev for dev, metrics in team_metrics.items()
                                   if metrics.get('productivity_score', 0) < 0.4]
            
            if len(low_productivity_devs) > len(team_metrics) * 0.3:
                risk_factors.append({
                    "factor": "Team productivity issues",
                    "severity": "medium",
                    "description": f"{len(low_productivity_devs)} developers with low productivity",
                    "impact": "Reduced team velocity"
                })
                risk_score += 0.2
        
        # Deviation risk
        deviation_rate = 1.0 - self.deviation_prevention_rate()
        if deviation_rate > 0.3:
            risk_factors.append({
                "factor": "High deviation rate",
                "severity": "medium",
                "description": f"Estimated {deviation_rate:.1%} deviation from task requirements",
                "impact": "Scope creep and wasted effort"
            })
            risk_score += 0.15
        
        # Generate recommendations
        recommendations = []
        
        if risk_score > 0.4:
            recommendations.extend([
                "Implement daily stand-ups to track progress",
                "Increase human review frequency",
                "Consider adding resources or reducing scope",
                "Review and simplify task requirements"
            ])
        elif risk_score > 0.2:
            recommendations.extend([
                "Monitor progress more closely",
                "Address identified bottlenecks promptly",
                "Improve team communication and coordination"
            ])
        else:
            recommendations.extend([
                "Continue current practices",
                "Monitor metrics regularly",
                "Look for optimization opportunities"
            ])
        
        # Determine overall risk level
        if risk_score >= 0.4:
            overall_risk = "high"
        elif risk_score >= 0.25:
            overall_risk = "medium"
        elif risk_score >= 0.1:
            overall_risk = "low"
        else:
            overall_risk = "minimal"
        
        return RiskAssessment(
            overall_risk=overall_risk,
            risk_factors=risk_factors,
            recommendations=recommendations,
            risk_score=risk_score
        )
    
    def generate_summary_report(self) -> Dict[str, Any]:
        """Generate comprehensive metrics summary"""
        return {
            "timestamp": datetime.now().isoformat(),
            "project_name": self.session_data.get('project_name', 'Unknown'),
            "metrics": {
                "task_completion_rate": self.task_completion_rate(),
                "average_task_duration_hours": self.average_task_duration().total_seconds() / 3600,
                "deviation_prevention_rate": self.deviation_prevention_rate(),
                "completion_quality_score": self.completion_quality_score(),
                "task_rework_rate": self.task_rework_rate(),
                "human_review_efficiency": self.human_review_efficiency(),
                "collaboration_effectiveness": self.collaboration_effectiveness()
            },
            "team_productivity": self.team_productivity_metrics(),
            "bottlenecks": [asdict(b) for b in self.analyze_bottlenecks()],
            "risk_assessment": asdict(self.assess_project_risks()),
            "task_counts": {
                "active": len(self.session_data.get('active_tasks', [])),
                "completed": len(self.session_data.get('completed_tasks', [])),
                "total": len(self.session_data.get('active_tasks', [])) + len(self.session_data.get('completed_tasks', []))
            }
        }