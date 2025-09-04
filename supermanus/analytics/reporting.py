#!/usr/bin/env python3
"""
SuperManUS Analytics Reporting
Generate comprehensive reports and visualizations for task enforcement metrics
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
import statistics
from dataclasses import asdict

try:
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    from matplotlib.figure import Figure
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

from .metrics import TaskEnforcementMetrics


class AnalyticsReporter:
    """
    Generate comprehensive reports and visualizations for SuperManUS analytics
    """
    
    def __init__(self, metrics: TaskEnforcementMetrics, output_dir: str = "analytics_reports"):
        self.metrics = metrics
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Report templates
        self.templates = {
            "executive_summary": self._executive_summary_template,
            "detailed_metrics": self._detailed_metrics_template,
            "team_productivity": self._team_productivity_template,
            "risk_analysis": self._risk_analysis_template,
            "trend_analysis": self._trend_analysis_template
        }
    
    def generate_executive_summary(self, save_to_file: bool = True) -> str:
        """Generate executive summary report"""
        report = self.templates["executive_summary"]()
        
        if save_to_file:
            filename = f"executive_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            self._save_report(report, filename)
        
        return report
    
    def generate_detailed_report(self, save_to_file: bool = True) -> str:
        """Generate detailed metrics report"""
        report = self.templates["detailed_metrics"]()
        
        if save_to_file:
            filename = f"detailed_metrics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            self._save_report(report, filename)
        
        return report
    
    def generate_team_report(self, save_to_file: bool = True) -> str:
        """Generate team productivity report"""
        report = self.templates["team_productivity"]()
        
        if save_to_file:
            filename = f"team_productivity_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            self._save_report(report, filename)
        
        return report
    
    def generate_risk_report(self, save_to_file: bool = True) -> str:
        """Generate risk analysis report"""
        report = self.templates["risk_analysis"]()
        
        if save_to_file:
            filename = f"risk_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            self._save_report(report, filename)
        
        return report
    
    def generate_trend_report(self, days: int = 30, save_to_file: bool = True) -> str:
        """Generate trend analysis report"""
        report = self.templates["trend_analysis"](days)
        
        if save_to_file:
            filename = f"trend_analysis_{days}d_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            self._save_report(report, filename)
        
        return report
    
    def generate_complete_report(self, include_visualizations: bool = True) -> str:
        """Generate comprehensive report with all sections"""
        sections = [
            ("# SuperManUS Task Enforcement Analytics Report", ""),
            (f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ""),
            (f"**Project:** {self.metrics.session_data.get('project_name', 'Unknown')}", ""),
            ("", "---"),
            ("## Executive Summary", self.templates["executive_summary"]()),
            ("## Detailed Metrics", self.templates["detailed_metrics"]()),
            ("## Team Productivity", self.templates["team_productivity"]()),
            ("## Risk Analysis", self.templates["risk_analysis"]()),
            ("## Trend Analysis", self.templates["trend_analysis"](30))
        ]
        
        complete_report = "\n\n".join([
            section[0] + "\n\n" + section[1] if section[1] else section[0]
            for section in sections
        ])
        
        # Add visualizations if available
        if include_visualizations and MATPLOTLIB_AVAILABLE:
            viz_section = self._generate_visualization_section()
            complete_report += "\n\n## Visualizations\n\n" + viz_section
        
        # Save complete report
        filename = f"complete_analytics_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        self._save_report(complete_report, filename)
        
        return complete_report
    
    def _executive_summary_template(self) -> str:
        """Generate executive summary"""
        summary = self.metrics.generate_summary_report()
        metrics = summary["metrics"]
        risk = summary["risk_assessment"]
        
        # Determine overall project health
        completion_rate = metrics["task_completion_rate"]
        quality_score = metrics["completion_quality_score"]
        deviation_prevention = metrics["deviation_prevention_rate"]
        
        if completion_rate >= 0.8 and quality_score >= 0.8 and deviation_prevention >= 0.8:
            health_status = "🟢 **EXCELLENT**"
            health_desc = "Project is on track with high quality and discipline"
        elif completion_rate >= 0.6 and quality_score >= 0.6 and deviation_prevention >= 0.6:
            health_status = "🟡 **GOOD**"
            health_desc = "Project is progressing well with minor areas for improvement"
        elif completion_rate >= 0.4 or quality_score >= 0.4:
            health_status = "🟠 **ATTENTION NEEDED**"
            health_desc = "Project has significant challenges requiring immediate attention"
        else:
            health_status = "🔴 **CRITICAL**"
            health_desc = "Project is at high risk and needs urgent intervention"
        
        report = f"""
### Project Health: {health_status}

{health_desc}

### Key Metrics
- **Task Completion Rate:** {completion_rate:.1%}
- **Quality Score:** {quality_score:.1%}
- **Deviation Prevention:** {deviation_prevention:.1%}
- **Team Productivity:** {metrics["collaboration_effectiveness"]:.1%}

### Risk Level: {risk["overall_risk"].title()}
**Risk Score:** {risk["risk_score"]:.1f}/1.0

### Active Tasks: {summary["task_counts"]["active"]} | Completed: {summary["task_counts"]["completed"]}

### Top Priorities
"""
        
        # Add top recommendations
        recommendations = risk["recommendations"][:3]
        for i, rec in enumerate(recommendations, 1):
            report += f"{i}. {rec}\n"
        
        # Add critical bottlenecks if any
        critical_bottlenecks = [b for b in summary["bottlenecks"] if b["severity"] == "critical"]
        if critical_bottlenecks:
            report += "\n### Critical Issues\n"
            for bottleneck in critical_bottlenecks:
                report += f"- **{bottleneck['bottleneck_type']}:** {bottleneck['description']}\n"
        
        return report.strip()
    
    def _detailed_metrics_template(self) -> str:
        """Generate detailed metrics report"""
        summary = self.metrics.generate_summary_report()
        metrics = summary["metrics"]
        
        report = f"""
### Task Completion Metrics
- **Completion Rate:** {metrics["task_completion_rate"]:.1%}
- **Average Task Duration:** {metrics["average_task_duration_hours"]:.1f} hours
- **Rework Rate:** {metrics["task_rework_rate"]:.1%}

### Quality Metrics
- **Completion Quality Score:** {metrics["completion_quality_score"]:.1%}
- **Human Review Efficiency:** {metrics["human_review_efficiency"]:.1%}
- **Deviation Prevention Rate:** {metrics["deviation_prevention_rate"]:.1%}

### Team Collaboration
- **Collaboration Effectiveness:** {metrics["collaboration_effectiveness"]:.1%}

### Task Distribution
- **Active Tasks:** {summary["task_counts"]["active"]}
- **Completed Tasks:** {summary["task_counts"]["completed"]}
- **Total Tasks:** {summary["task_counts"]["total"]}
"""
        
        # Add team assignments if available
        team_assignments = self.metrics.session_data.get('team_assignments', {})
        if team_assignments:
            report += "\n### Team Task Assignments\n"
            for developer, tasks in team_assignments.items():
                report += f"- **{developer}:** {len(tasks)} tasks\n"
        
        return report.strip()
    
    def _team_productivity_template(self) -> str:
        """Generate team productivity report"""
        team_metrics = self.metrics.team_productivity_metrics()
        
        if not team_metrics:
            return "No team productivity data available."
        
        report = "### Individual Developer Metrics\n\n"
        
        # Sort developers by productivity score
        sorted_devs = sorted(team_metrics.items(), 
                           key=lambda x: x[1].get('productivity_score', 0), 
                           reverse=True)
        
        for developer, metrics in sorted_devs:
            productivity_score = metrics.get('productivity_score', 0)
            
            # Determine performance level
            if productivity_score >= 0.8:
                performance_icon = "🟢"
                performance_level = "Excellent"
            elif productivity_score >= 0.6:
                performance_icon = "🟡"
                performance_level = "Good"
            elif productivity_score >= 0.4:
                performance_icon = "🟠"
                performance_level = "Needs Improvement"
            else:
                performance_icon = "🔴"
                performance_level = "Attention Required"
            
            report += f"""
#### {developer} {performance_icon} ({performance_level})

- **Productivity Score:** {productivity_score:.1%}
- **Tasks Worked:** {metrics.get('tasks_worked', 0)}
- **Avg Steps per Task:** {metrics.get('avg_steps_per_task', 0):.1f}
- **Avg Files per Task:** {metrics.get('avg_files_per_task', 0):.1f}
- **Quality Score:** {metrics.get('avg_quality_score', 0):.1%}
- **Total Hours:** {metrics.get('total_duration_hours', 0):.1f}
"""
        
        # Calculate team averages
        all_scores = [m.get('productivity_score', 0) for m in team_metrics.values()]
        all_quality = [m.get('avg_quality_score', 0) for m in team_metrics.values()]
        
        if all_scores:
            report += f"""
### Team Averages
- **Average Productivity Score:** {statistics.mean(all_scores):.1%}
- **Average Quality Score:** {statistics.mean(all_quality):.1%}
- **Team Size:** {len(team_metrics)} developers
- **Productivity Range:** {min(all_scores):.1%} - {max(all_scores):.1%}
"""
        
        return report.strip()
    
    def _risk_analysis_template(self) -> str:
        """Generate risk analysis report"""
        risk_assessment = self.metrics.assess_project_risks()
        bottlenecks = self.metrics.analyze_bottlenecks()
        
        # Risk level emoji and description
        risk_icons = {
            "minimal": "🟢",
            "low": "🟡", 
            "medium": "🟠",
            "high": "🔴",
            "critical": "🚨"
        }
        
        risk_icon = risk_icons.get(risk_assessment.overall_risk, "❓")
        
        report = f"""
### Overall Risk Level: {risk_icon} {risk_assessment.overall_risk.title()}
**Risk Score:** {risk_assessment.risk_score:.2f}/1.0

### Risk Factors
"""
        
        if not risk_assessment.risk_factors:
            report += "No significant risk factors identified.\n"
        else:
            for factor in risk_assessment.risk_factors:
                severity_icons = {"low": "🟡", "medium": "🟠", "high": "🔴", "critical": "🚨"}
                severity_icon = severity_icons.get(factor["severity"], "❓")
                
                report += f"""
#### {severity_icon} {factor["factor"]} ({factor["severity"].title()})
- **Description:** {factor["description"]}
- **Impact:** {factor["impact"]}
"""
        
        # Add bottlenecks
        if bottlenecks:
            report += "\n### Identified Bottlenecks\n"
            for bottleneck in bottlenecks:
                severity_icon = {"low": "🟡", "medium": "🟠", "high": "🔴", "critical": "🚨"}[bottleneck.severity]
                
                report += f"""
#### {severity_icon} {bottleneck.bottleneck_type.replace('_', ' ').title()}
- **Severity:** {bottleneck.severity.title()}
- **Description:** {bottleneck.description}
- **Estimated Impact:** {bottleneck.estimated_impact}
- **Affected Tasks:** {len(bottleneck.affected_tasks)} tasks
"""
        
        # Add recommendations
        report += "\n### Recommendations\n"
        for i, recommendation in enumerate(risk_assessment.recommendations, 1):
            report += f"{i}. {recommendation}\n"
        
        return report.strip()
    
    def _trend_analysis_template(self, days: int = 30) -> str:
        """Generate trend analysis report"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Get completion trend
        completion_trend = self.metrics.get_completion_trend(start_date, end_date, "day")
        
        report = f"### Task Completion Trend (Last {days} Days)\n\n"
        
        if not completion_trend:
            report += "No task completion data available for the specified period.\n"
            return report
        
        # Calculate trend statistics
        daily_completions = [point.value for point in completion_trend]
        total_completions = sum(daily_completions)
        avg_daily = statistics.mean(daily_completions) if daily_completions else 0
        
        # Determine trend direction
        if len(daily_completions) >= 7:
            recent_avg = statistics.mean(daily_completions[-7:])  # Last 7 days
            earlier_avg = statistics.mean(daily_completions[:-7])  # Earlier days
            
            if recent_avg > earlier_avg * 1.1:
                trend_direction = "📈 **Improving**"
                trend_desc = "Task completion rate is trending upward"
            elif recent_avg < earlier_avg * 0.9:
                trend_direction = "📉 **Declining**"
                trend_desc = "Task completion rate is trending downward"
            else:
                trend_direction = "➡️ **Stable**"
                trend_desc = "Task completion rate is relatively stable"
        else:
            trend_direction = "📊 **Insufficient Data**"
            trend_desc = "Not enough data to determine trend"
        
        report += f"""
**Trend Direction:** {trend_direction}
{trend_desc}

**Summary Statistics:**
- **Total Completions:** {total_completions}
- **Average Daily Completions:** {avg_daily:.1f}
- **Peak Day:** {max(daily_completions)} completions
- **Active Days:** {len([x for x in daily_completions if x > 0])}/{len(daily_completions)}
"""
        
        # Show recent daily data
        report += "\n**Recent Daily Completions:**\n"
        for point in completion_trend[-7:]:  # Last 7 days
            report += f"- {point.timestamp}: {point.value} tasks\n"
        
        return report.strip()
    
    def _generate_visualization_section(self) -> str:
        """Generate visualization section with charts"""
        if not MATPLOTLIB_AVAILABLE:
            return "Visualizations require matplotlib. Install with: pip install matplotlib"
        
        viz_files = []
        
        # Generate productivity chart
        try:
            productivity_chart = self._create_productivity_chart()
            if productivity_chart:
                viz_files.append(productivity_chart)
        except Exception as e:
            print(f"Warning: Could not generate productivity chart: {e}")
        
        # Generate completion trend chart
        try:
            trend_chart = self._create_completion_trend_chart()
            if trend_chart:
                viz_files.append(trend_chart)
        except Exception as e:
            print(f"Warning: Could not generate trend chart: {e}")
        
        # Generate risk assessment chart
        try:
            risk_chart = self._create_risk_assessment_chart()
            if risk_chart:
                viz_files.append(risk_chart)
        except Exception as e:
            print(f"Warning: Could not generate risk chart: {e}")
        
        if not viz_files:
            return "No visualizations could be generated."
        
        viz_section = "The following charts have been generated:\n\n"
        for viz_file in viz_files:
            viz_section += f"- ![Chart]({viz_file})\n"
        
        return viz_section
    
    def _create_productivity_chart(self) -> Optional[str]:
        """Create team productivity visualization"""
        team_metrics = self.metrics.team_productivity_metrics()
        
        if not team_metrics:
            return None
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
        
        # Productivity scores
        developers = list(team_metrics.keys())
        productivity_scores = [metrics.get('productivity_score', 0) for metrics in team_metrics.values()]
        
        ax1.bar(developers, productivity_scores, color=['#2E8B57' if score >= 0.7 else '#FF6347' if score < 0.5 else '#FFD700' for score in productivity_scores])
        ax1.set_title('Developer Productivity Scores')
        ax1.set_ylabel('Productivity Score')
        ax1.set_ylim(0, 1)
        plt.setp(ax1.get_xticklabels(), rotation=45, ha='right')
        
        # Quality scores
        quality_scores = [metrics.get('avg_quality_score', 0) for metrics in team_metrics.values()]
        ax2.bar(developers, quality_scores, color=['#4169E1' if score >= 0.7 else '#DC143C' if score < 0.5 else '#FF8C00' for score in quality_scores])
        ax2.set_title('Developer Quality Scores')
        ax2.set_ylabel('Quality Score')
        ax2.set_ylim(0, 1)
        plt.setp(ax2.get_xticklabels(), rotation=45, ha='right')
        
        plt.tight_layout()
        
        filename = f"productivity_chart_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        filepath = self.output_dir / filename
        plt.savefig(filepath, dpi=150, bbox_inches='tight')
        plt.close()
        
        return filename
    
    def _create_completion_trend_chart(self) -> Optional[str]:
        """Create task completion trend visualization"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        completion_trend = self.metrics.get_completion_trend(start_date, end_date, "day")
        
        if not completion_trend:
            return None
        
        # Prepare data
        dates = [datetime.fromisoformat(point.timestamp) for point in completion_trend]
        values = [point.value for point in completion_trend]
        
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Plot trend line
        ax.plot(dates, values, marker='o', linewidth=2, markersize=4, color='#2E8B57')
        ax.fill_between(dates, values, alpha=0.3, color='#2E8B57')
        
        # Add trend line
        if len(values) > 1:
            z = np.polyfit(range(len(values)), values, 1)
            p = np.poly1d(z)
            ax.plot(dates, p(range(len(values))), "--", color='#FF6347', linewidth=2, label='Trend')
        
        ax.set_title('Task Completion Trend (30 Days)', fontsize=14, fontweight='bold')
        ax.set_xlabel('Date')
        ax.set_ylabel('Tasks Completed')
        ax.grid(True, alpha=0.3)
        ax.legend()
        
        # Format x-axis
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
        ax.xaxis.set_major_locator(mdates.DayLocator(interval=5))
        plt.setp(ax.get_xticklabels(), rotation=45)
        
        plt.tight_layout()
        
        filename = f"completion_trend_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        filepath = self.output_dir / filename
        plt.savefig(filepath, dpi=150, bbox_inches='tight')
        plt.close()
        
        return filename
    
    def _create_risk_assessment_chart(self) -> Optional[str]:
        """Create risk assessment visualization"""
        risk_assessment = self.metrics.assess_project_risks()
        
        # Create risk factor severity chart
        severity_counts = {"low": 0, "medium": 0, "high": 0, "critical": 0}
        
        for factor in risk_assessment.risk_factors:
            severity = factor.get("severity", "medium")
            severity_counts[severity] += 1
        
        if sum(severity_counts.values()) == 0:
            return None
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
        
        # Risk factors pie chart
        labels = [f"{sev.title()}\n({count})" for sev, count in severity_counts.items() if count > 0]
        sizes = [count for count in severity_counts.values() if count > 0]
        colors = ['#FFD700', '#FF8C00', '#FF6347', '#DC143C'][:len(sizes)]
        
        ax1.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
        ax1.set_title('Risk Factors by Severity')
        
        # Risk score gauge
        risk_score = risk_assessment.risk_score
        
        # Create a simple risk gauge
        risk_levels = ['Minimal', 'Low', 'Medium', 'High', 'Critical']
        risk_colors = ['#2E8B57', '#FFD700', '#FF8C00', '#FF6347', '#DC143C']
        
        bars = ax2.barh(risk_levels, [0.2, 0.2, 0.2, 0.2, 0.2], color=risk_colors, alpha=0.3)
        
        # Highlight current risk level
        current_level_index = min(int(risk_score * 5), 4)
        bars[current_level_index].set_alpha(1.0)
        bars[current_level_index].set_edgecolor('black')
        bars[current_level_index].set_linewidth(2)
        
        ax2.set_xlim(0, 0.2)
        ax2.set_title(f'Current Risk Level: {risk_assessment.overall_risk.title()}')
        ax2.set_xlabel('Risk Score')
        
        plt.tight_layout()
        
        filename = f"risk_assessment_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        filepath = self.output_dir / filename
        plt.savefig(filepath, dpi=150, bbox_inches='tight')
        plt.close()
        
        return filename
    
    def _save_report(self, content: str, filename: str):
        """Save report to file"""
        filepath = self.output_dir / filename
        with open(filepath, 'w') as f:
            f.write(content)
        print(f"Report saved: {filepath}")
    
    def generate_json_report(self, save_to_file: bool = True) -> Dict[str, Any]:
        """Generate machine-readable JSON report"""
        summary = self.metrics.generate_summary_report()
        
        # Add additional computed metrics
        summary["analytics_metadata"] = {
            "generated_at": datetime.now().isoformat(),
            "analysis_period_days": self.metrics.history_days,
            "report_version": "1.0"
        }
        
        if save_to_file:
            filename = f"analytics_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            filepath = self.output_dir / filename
            with open(filepath, 'w') as f:
                json.dump(summary, f, indent=2)
            print(f"JSON report saved: {filepath}")
        
        return summary
    
    def export_csv_data(self, save_to_file: bool = True) -> str:
        """Export metrics data as CSV"""
        team_metrics = self.metrics.team_productivity_metrics()
        
        csv_content = "Developer,Tasks_Worked,Avg_Steps_Per_Task,Avg_Files_Per_Task,Quality_Score,Productivity_Score,Total_Hours\n"
        
        for developer, metrics in team_metrics.items():
            csv_content += f"{developer},{metrics.get('tasks_worked', 0)},{metrics.get('avg_steps_per_task', 0):.2f},{metrics.get('avg_files_per_task', 0):.2f},{metrics.get('avg_quality_score', 0):.3f},{metrics.get('productivity_score', 0):.3f},{metrics.get('total_duration_hours', 0):.1f}\n"
        
        if save_to_file:
            filename = f"team_metrics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            filepath = self.output_dir / filename
            with open(filepath, 'w') as f:
                f.write(csv_content)
            print(f"CSV data exported: {filepath}")
        
        return csv_content


# Add missing numpy import for trend chart
try:
    import numpy as np
except ImportError:
    np = None