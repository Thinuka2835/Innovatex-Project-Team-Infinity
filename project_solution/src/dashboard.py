"""
Interactive Dashboard for Project Sentinel

What it is: A web-based visualization dashboard using Plotly Dash
Why created: To provide real-time visualization of detected events and metrics
How it works: Loads event data and creates interactive charts and tables
How to use: python dashboard.py --events <events_file> --port 8050
"""

import argparse
import json
from pathlib import Path
from datetime import datetime
from collections import Counter, defaultdict

try:
    import dash
    from dash import dcc, html, dash_table
    import plotly.graph_objs as go
    import plotly.express as px
    import pandas as pd
    DASH_AVAILABLE = True
except ImportError:
    DASH_AVAILABLE = False
    print("Warning: Dash not installed. Install with: pip install dash plotly pandas")


class EventDashboard:
    """Interactive dashboard for visualizing detected events."""
    
    def __init__(self, events_file: str):
        """
        Initialize dashboard with events data.
        
        Args:
            events_file: Path to events JSONL file
        """
        self.events = self.load_events(events_file)
        self.df = self.create_dataframe()
        
    def load_events(self, events_file: str):
        """Load events from JSONL file."""
        events = []
        with open(events_file, 'r') as f:
            for line in f:
                if line.strip():
                    events.append(json.loads(line))
        return events
    
    def create_dataframe(self):
        """Convert events to pandas DataFrame for analysis."""
        if not self.events:
            return pd.DataFrame()
        
        rows = []
        for event in self.events:
            row = {
                'timestamp': event['timestamp'],
                'event_id': event['event_id'],
                'event_name': event['event_data']['event_name'],
                'station_id': event['event_data'].get('station_id', 'N/A'),
            }
            
            # Add event-specific fields
            for key, value in event['event_data'].items():
                if key not in ['event_name', 'station_id']:
                    row[key] = value
            
            rows.append(row)
        
        df = pd.DataFrame(rows)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        return df
    
    def create_app(self):
        """Create the Dash application."""
        app = dash.Dash(__name__)
        
        # Modern color palette
        colors = {
            'background': '#f8f9fa',
            'card': '#ffffff',
            'primary': '#3b82f6',
            'success': '#10b981',
            'warning': '#f59e0b',
            'danger': '#ef4444',
            'secondary': '#6366f1',
            'text': '#1f2937',
            'text_light': '#6b7280'
        }
        
        # Event type distribution with modern styling
        event_counts = Counter([e['event_data']['event_name'] for e in self.events])
        
        # Color mapping for different event types
        event_colors = {
            'Scanner Avoidance': '#ef4444',
            'Barcode Switching': '#f59e0b',
            'Weight Discrepancies': '#8b5cf6',
            'Long Queue Length': '#ec4899',
            'Long Wait Time': '#f97316',
            'Inventory Discrepancy': '#06b6d4',
            'System Crash': '#64748b',
            'Staffing Needs': '#10b981'
        }
        
        fig_event_types = go.Figure(data=[
            go.Bar(
                x=list(event_counts.keys()),
                y=list(event_counts.values()),
                marker=dict(
                    color=[event_colors.get(k, colors['primary']) for k in event_counts.keys()],
                    line=dict(color='rgba(255,255,255,0.8)', width=2)
                ),
                text=list(event_counts.values()),
                textposition='outside',
                hovertemplate='<b>%{x}</b><br>Count: %{y}<extra></extra>'
            )
        ])
        fig_event_types.update_layout(
            title={
                'text': '📊 Event Type Distribution',
                'font': {'size': 20, 'color': colors['text'], 'family': 'Arial, sans-serif'}
            },
            xaxis_title='Event Type',
            yaxis_title='Count',
            height=450,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(family='Arial, sans-serif', color=colors['text']),
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=True, gridcolor='rgba(0,0,0,0.05)'),
            margin=dict(l=60, r=40, t=80, b=100),
            hoverlabel=dict(bgcolor="white", font_size=14)
        )
        
        # Timeline with enhanced styling
        timeline_data = self.df.groupby(['timestamp', 'event_name']).size().reset_index(name='count')
        fig_timeline = px.scatter(
            timeline_data,
            x='timestamp',
            y='event_name',
            size='count',
            color='event_name',
            title='📅 Event Timeline',
            height=450,
            color_discrete_map=event_colors
        )
        fig_timeline.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(family='Arial, sans-serif', color=colors['text']),
            title_font=dict(size=20),
            xaxis=dict(showgrid=True, gridcolor='rgba(0,0,0,0.05)'),
            yaxis=dict(showgrid=True, gridcolor='rgba(0,0,0,0.05)'),
            margin=dict(l=60, r=40, t=80, b=60)
        )
        
        # Station-wise event distribution with modern styling
        station_events = self.df[self.df['station_id'] != 'N/A'].groupby(
            ['station_id', 'event_name']
        ).size().reset_index(name='count')
        
        fig_stations = px.bar(
            station_events,
            x='station_id',
            y='count',
            color='event_name',
            title='🏪 Events by Station',
            height=450,
            color_discrete_map=event_colors,
            barmode='stack'
        )
        fig_stations.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(family='Arial, sans-serif', color=colors['text']),
            title_font=dict(size=20),
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=True, gridcolor='rgba(0,0,0,0.05)'),
            margin=dict(l=60, r=40, t=80, b=60),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.3,
                xanchor="center",
                x=0.5
            )
        )
        
        # Events over time (hourly aggregation) with modern styling
        self.df['hour'] = self.df['timestamp'].dt.floor('h')
        hourly_events = self.df.groupby('hour').size().reset_index(name='count')
        
        fig_hourly = go.Figure(data=[
            go.Scatter(
                x=hourly_events['hour'],
                y=hourly_events['count'],
                mode='lines+markers',
                line=dict(color=colors['secondary'], width=3),
                marker=dict(size=10, line=dict(width=2, color='white')),
                fill='tozeroy',
                fillcolor='rgba(99, 102, 241, 0.1)',
                hovertemplate='<b>Time:</b> %{x}<br><b>Events:</b> %{y}<extra></extra>'
            )
        ])
        fig_hourly.update_layout(
            title={
                'text': '⏰ Events Over Time (Hourly)',
                'font': {'size': 20, 'color': colors['text'], 'family': 'Arial, sans-serif'}
            },
            xaxis_title='Time',
            yaxis_title='Event Count',
            height=450,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(family='Arial, sans-serif', color=colors['text']),
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=True, gridcolor='rgba(0,0,0,0.05)'),
            margin=dict(l=60, r=40, t=80, b=60),
            hovermode='x unified'
        )
        
        # Create summary statistics
        total_events = len(self.events)
        unique_event_types = len(event_counts)
        
        if 'station_id' in self.df.columns:
            affected_stations = self.df[self.df['station_id'] != 'N/A']['station_id'].nunique()
        else:
            affected_stations = 0
        
        # Modern card style
        card_style = {
            'backgroundColor': colors['card'],
            'padding': '30px',
            'borderRadius': '16px',
            'boxShadow': '0 4px 6px rgba(0, 0, 0, 0.07)',
            'textAlign': 'center',
            'border': '1px solid rgba(0, 0, 0, 0.05)',
            'transition': 'transform 0.2s, box-shadow 0.2s'
        }
        
        # Layout with modern design
        app.layout = html.Div([
            # Header
            html.Div([
                html.H1([
                    html.Span('🛡️ ', style={'fontSize': '48px'}),
                    'Project Sentinel'
                ], style={
                    'textAlign': 'center',
                    'color': colors['text'],
                    'marginBottom': '10px',
                    'fontWeight': '700',
                    'fontSize': '42px',
                    'fontFamily': 'Arial, sans-serif'
                }),
                html.P('Real-time Event Detection Dashboard',
                       style={
                           'textAlign': 'center',
                           'color': colors['text_light'],
                           'fontSize': '18px',
                           'marginBottom': '40px',
                           'fontFamily': 'Arial, sans-serif'
                       })
            ]),
            
            # Summary cards with modern styling
            html.Div([
                html.Div([
                    html.Div('🔔', style={'fontSize': '48px', 'marginBottom': '10px'}),
                    html.H3('Total Events', style={
                        'color': colors['text_light'],
                        'fontSize': '16px',
                        'fontWeight': '500',
                        'marginBottom': '5px'
                    }),
                    html.H2(f'{total_events:,}', style={
                        'color': colors['primary'],
                        'fontSize': '36px',
                        'fontWeight': '700',
                        'margin': '0'
                    })
                ], style={**card_style, 'flex': '1', 'margin': '10px'}),
                
                html.Div([
                    html.Div('📋', style={'fontSize': '48px', 'marginBottom': '10px'}),
                    html.H3('Event Types', style={
                        'color': colors['text_light'],
                        'fontSize': '16px',
                        'fontWeight': '500',
                        'marginBottom': '5px'
                    }),
                    html.H2(f'{unique_event_types}', style={
                        'color': colors['success'],
                        'fontSize': '36px',
                        'fontWeight': '700',
                        'margin': '0'
                    })
                ], style={**card_style, 'flex': '1', 'margin': '10px'}),
                
                html.Div([
                    html.Div('🏪', style={'fontSize': '48px', 'marginBottom': '10px'}),
                    html.H3('Affected Stations', style={
                        'color': colors['text_light'],
                        'fontSize': '16px',
                        'fontWeight': '500',
                        'marginBottom': '5px'
                    }),
                    html.H2(f'{affected_stations}', style={
                        'color': colors['warning'],
                        'fontSize': '36px',
                        'fontWeight': '700',
                        'margin': '0'
                    })
                ], style={**card_style, 'flex': '1', 'margin': '10px'})
            ], style={
                'display': 'flex',
                'justifyContent': 'space-between',
                'marginBottom': '40px',
                'flexWrap': 'wrap'
            }),
            
            # Charts grid with modern styling
            html.Div([
                html.Div([
                    dcc.Graph(figure=fig_event_types, config={'displayModeBar': False})
                ], style={**card_style, 'flex': '1', 'minWidth': '48%', 'margin': '10px'}),
                
                html.Div([
                    dcc.Graph(figure=fig_stations, config={'displayModeBar': False})
                ], style={**card_style, 'flex': '1', 'minWidth': '48%', 'margin': '10px'})
            ], style={'display': 'flex', 'flexWrap': 'wrap', 'marginBottom': '20px'}),
            
            html.Div([
                html.Div([
                    dcc.Graph(figure=fig_timeline, config={'displayModeBar': False})
                ], style={**card_style, 'margin': '10px'})
            ]),
            
            html.Div([
                html.Div([
                    dcc.Graph(figure=fig_hourly, config={'displayModeBar': False})
                ], style={**card_style, 'margin': '10px'})
            ]),
            
            # Event details table with modern styling
            html.Div([
                html.H2([
                    html.Span('📄 ', style={'fontSize': '32px'}),
                    'Event Details'
                ], style={
                    'color': colors['text'],
                    'marginTop': '40px',
                    'marginBottom': '20px',
                    'fontWeight': '600',
                    'fontFamily': 'Arial, sans-serif'
                }),
                html.Div([
                    dash_table.DataTable(
                        data=self.df.head(100).to_dict('records'),
                        columns=[{'name': col, 'id': col} for col in self.df.columns],
                        style_table={
                            'overflowX': 'auto',
                            'borderRadius': '12px',
                            'overflow': 'hidden'
                        },
                        style_cell={
                            'textAlign': 'left',
                            'padding': '15px',
                            'fontFamily': 'Arial, sans-serif',
                            'fontSize': '14px',
                            'color': colors['text']
                        },
                        style_header={
                            'backgroundColor': colors['secondary'],
                            'color': 'white',
                            'fontWeight': '600',
                            'fontSize': '14px',
                            'padding': '15px',
                            'textTransform': 'uppercase',
                            'letterSpacing': '0.5px'
                        },
                        style_data_conditional=[
                            {
                                'if': {'row_index': 'odd'},
                                'backgroundColor': '#f9fafb'
                            },
                            {
                                'if': {'state': 'active'},
                                'backgroundColor': 'rgba(59, 130, 246, 0.1)',
                                'border': f'1px solid {colors["primary"]}'
                            }
                        ],
                        style_data={
                            'border': '1px solid rgba(0, 0, 0, 0.05)'
                        },
                        page_size=20
                    )
                ], style={**card_style, 'padding': '0'})
            ])
        ], style={
            'padding': '40px',
            'fontFamily': 'Arial, sans-serif',
            'backgroundColor': colors['background'],
            'minHeight': '100vh'
        })
        
        return app


def main():
    """Main execution function."""
    if not DASH_AVAILABLE:
        print("Error: Required packages not installed.")
        print("Install with: pip install dash plotly pandas")
        return
    
    parser = argparse.ArgumentParser(description='Project Sentinel Dashboard')
    parser.add_argument(
        '--events',
        type=str,
        default='../evidence/output/test/events.jsonl',
        help='Path to events JSONL file'
    )
    parser.add_argument(
        '--port',
        type=int,
        default=8050,
        help='Port to run dashboard on'
    )
    
    args = parser.parse_args()
    
    if not Path(args.events).exists():
        print(f"Error: Events file not found: {args.events}")
        return
    
    print(f"Loading events from {args.events}...")
    dashboard = EventDashboard(args.events)
    
    print(f"Starting dashboard on http://localhost:{args.port}")
    print("Press Ctrl+C to stop")
    
    app = dashboard.create_app()
    app.run(debug=False, port=args.port)


if __name__ == '__main__':
    main()
