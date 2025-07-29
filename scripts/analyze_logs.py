#!/usr/bin/env python3
"""
Log analysis utility for the Telegram bot.
Provides tools to analyze and extract insights from bot logs.
"""

import json
import argparse
import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from collections import defaultdict, Counter


class LogAnalyzer:
    """Analyzes bot logs and provides insights."""
    
    def __init__(self, logs_dir: str = "logs"):
        self.logs_dir = Path(logs_dir)
        if not self.logs_dir.exists():
            raise FileNotFoundError(f"Logs directory not found: {logs_dir}")
    
    def load_json_logs(self, hours_back: int = 24) -> List[Dict[str, Any]]:
        """Load JSON logs from the specified time period."""
        json_log_file = self.logs_dir / "bot.json"
        if not json_log_file.exists():
            return []
        
        cutoff_time = datetime.now() - timedelta(hours=hours_back)
        logs = []
        
        try:
            with open(json_log_file, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        log_entry = json.loads(line.strip())
                        log_time = datetime.fromisoformat(log_entry['timestamp'])
                        if log_time >= cutoff_time:
                            logs.append(log_entry)
                    except (json.JSONDecodeError, KeyError, ValueError):
                        continue
        except FileNotFoundError:
            pass
        
        return logs
    
    def analyze_user_activity(self, hours_back: int = 24) -> Dict[str, Any]:
        """Analyze user activity patterns."""
        logs = self.load_json_logs(hours_back)
        
        user_stats = defaultdict(lambda: {
            'total_actions': 0,
            'commands': Counter(),
            'first_seen': None,
            'last_seen': None,
            'errors': 0
        })
        
        for log in logs:
            if 'user_id' in log:
                user_id = str(log['user_id'])
                timestamp = datetime.fromisoformat(log['timestamp'])
                
                user_stats[user_id]['total_actions'] += 1
                
                if user_stats[user_id]['first_seen'] is None or timestamp < user_stats[user_id]['first_seen']:
                    user_stats[user_id]['first_seen'] = timestamp
                
                if user_stats[user_id]['last_seen'] is None or timestamp > user_stats[user_id]['last_seen']:
                    user_stats[user_id]['last_seen'] = timestamp
                
                if 'command' in log:
                    user_stats[user_id]['commands'][log['command']] += 1
                
                if log['level'] == 'ERROR':
                    user_stats[user_id]['errors'] += 1
        
        return dict(user_stats)
    
    def analyze_performance(self, hours_back: int = 24) -> Dict[str, Any]:
        """Analyze performance metrics."""
        logs = self.load_json_logs(hours_back)
        
        performance_data = defaultdict(list)
        
        for log in logs:
            if log.get('logger', '').endswith('.performance'):
                message = log.get('message', '')
                if 'took' in message:
                    try:
                        # Extract operation name and duration
                        parts = message.split("'")
                        if len(parts) >= 2:
                            operation = parts[1]
                            duration_part = message.split('took ')[1].split('s')[0]
                            duration = float(duration_part)
                            performance_data[operation].append(duration)
                    except (IndexError, ValueError):
                        continue
        
        # Calculate statistics
        stats = {}
        for operation, durations in performance_data.items():
            if durations:
                stats[operation] = {
                    'count': len(durations),
                    'avg_duration': sum(durations) / len(durations),
                    'min_duration': min(durations),
                    'max_duration': max(durations),
                    'total_duration': sum(durations)
                }
        
        return stats
    
    def analyze_errors(self, hours_back: int = 24) -> Dict[str, Any]:
        """Analyze error patterns."""
        logs = self.load_json_logs(hours_back)
        
        error_stats = {
            'total_errors': 0,
            'error_types': Counter(),
            'error_contexts': Counter(),
            'users_with_errors': set(),
            'recent_errors': []
        }
        
        for log in logs:
            if log['level'] in ['ERROR', 'CRITICAL']:
                error_stats['total_errors'] += 1
                
                if 'error_type' in log:
                    error_stats['error_types'][log['error_type']] += 1
                
                if 'user_id' in log:
                    error_stats['users_with_errors'].add(log['user_id'])
                
                # Extract context from logger name
                logger_parts = log.get('logger', '').split('.')
                if len(logger_parts) > 1:
                    context = logger_parts[-1]
                    error_stats['error_contexts'][context] += 1
                
                # Keep recent errors for detailed analysis
                if len(error_stats['recent_errors']) < 10:
                    error_stats['recent_errors'].append({
                        'timestamp': log['timestamp'],
                        'message': log['message'],
                        'error_type': log.get('error_type', 'Unknown'),
                        'user_id': log.get('user_id')
                    })
        
        error_stats['users_with_errors'] = len(error_stats['users_with_errors'])
        return error_stats
    
    def analyze_commands(self, hours_back: int = 24) -> Dict[str, Any]:
        """Analyze command usage patterns."""
        logs = self.load_json_logs(hours_back)
        
        command_stats = {
            'total_commands': 0,
            'command_counts': Counter(),
            'command_performance': defaultdict(list),
            'hourly_distribution': defaultdict(int)
        }
        
        for log in logs:
            if 'command' in log and log.get('logger', '').endswith('.user_actions'):
                command = log['command']
                timestamp = datetime.fromisoformat(log['timestamp'])
                hour = timestamp.hour
                
                command_stats['total_commands'] += 1
                command_stats['command_counts'][command] += 1
                command_stats['hourly_distribution'][hour] += 1
        
        return command_stats
    
    def generate_report(self, hours_back: int = 24) -> str:
        """Generate a comprehensive analysis report."""
        print(f"Analyzing logs from the last {hours_back} hours...")
        
        user_activity = self.analyze_user_activity(hours_back)
        performance = self.analyze_performance(hours_back)
        errors = self.analyze_errors(hours_back)
        commands = self.analyze_commands(hours_back)
        
        report = []
        report.append("=" * 60)
        report.append(f"TELEGRAM BOT LOG ANALYSIS REPORT")
        report.append(f"Time Period: Last {hours_back} hours")
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("=" * 60)
        
        # User Activity Summary
        report.append("\n📊 USER ACTIVITY SUMMARY")
        report.append("-" * 30)
        report.append(f"Total Active Users: {len(user_activity)}")
        
        if user_activity:
            most_active = max(user_activity.items(), key=lambda x: x[1]['total_actions'])
            report.append(f"Most Active User: {most_active[0]} ({most_active[1]['total_actions']} actions)")
            
            total_actions = sum(stats['total_actions'] for stats in user_activity.values())
            report.append(f"Total User Actions: {total_actions}")
        
        # Command Usage
        report.append("\n🤖 COMMAND USAGE")
        report.append("-" * 20)
        report.append(f"Total Commands Executed: {commands['total_commands']}")
        
        if commands['command_counts']:
            report.append("\nTop Commands:")
            for cmd, count in commands['command_counts'].most_common(5):
                report.append(f"  • {cmd}: {count} times")
        
        # Performance Analysis
        report.append("\n⚡ PERFORMANCE METRICS")
        report.append("-" * 25)
        
        if performance:
            report.append("Average Response Times:")
            for operation, stats in sorted(performance.items()):
                avg_ms = stats['avg_duration'] * 1000
                report.append(f"  • {operation}: {avg_ms:.1f}ms (count: {stats['count']})")
        else:
            report.append("No performance data available")
        
        # Error Analysis
        report.append("\n🚨 ERROR ANALYSIS")
        report.append("-" * 18)
        report.append(f"Total Errors: {errors['total_errors']}")
        report.append(f"Users Affected: {errors['users_with_errors']}")
        
        if errors['error_types']:
            report.append("\nError Types:")
            for error_type, count in errors['error_types'].most_common(5):
                report.append(f"  • {error_type}: {count} occurrences")
        
        if errors['recent_errors']:
            report.append("\nRecent Errors:")
            for error in errors['recent_errors'][-3:]:
                timestamp = datetime.fromisoformat(error['timestamp']).strftime('%H:%M:%S')
                report.append(f"  • [{timestamp}] {error['error_type']}: {error['message'][:50]}...")
        
        # Activity Distribution
        report.append("\n📈 HOURLY ACTIVITY DISTRIBUTION")
        report.append("-" * 35)
        
        if commands['hourly_distribution']:
            for hour in range(24):
                count = commands['hourly_distribution'][hour]
                if count > 0:
                    bar = "█" * min(count // 2, 20)
                    report.append(f"  {hour:02d}:00 │{bar:<20}│ {count}")
        
        report.append("\n" + "=" * 60)
        
        return "\n".join(report)


def main():
    """Main function for the log analyzer CLI."""
    parser = argparse.ArgumentParser(description="Analyze Telegram bot logs")
    parser.add_argument(
        "--hours", 
        type=int, 
        default=24, 
        help="Number of hours to analyze (default: 24)"
    )
    parser.add_argument(
        "--logs-dir", 
        type=str, 
        default="logs", 
        help="Path to logs directory (default: logs)"
    )
    parser.add_argument(
        "--output", 
        type=str, 
        help="Output file for the report (default: stdout)"
    )
    
    args = parser.parse_args()
    
    try:
        analyzer = LogAnalyzer(args.logs_dir)
        report = analyzer.generate_report(args.hours)
        
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(report)
            print(f"Report saved to: {args.output}")
        else:
            print(report)
            
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()