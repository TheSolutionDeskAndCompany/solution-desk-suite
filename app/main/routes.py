from flask import Blueprint, render_template, abort, redirect, url_for
from flask_login import current_user
from ..extensions import pages, db
from ..models import Tool, Purchase

main_bp = Blueprint('main', __name__, template_folder='templates')

def get_tool_descriptions():
    """Get problem-solution descriptions for each tool"""
    return {
        'example-tool': {
            'problem': 'Scattered workflows and missed deadlines',
            'solution': 'Unified productivity dashboard with intelligent task management'
        },
        'smart-budget-tracker': {
            'problem': 'Overspending and financial stress',
            'solution': 'AI-powered expense tracking with predictive bill alerts'
        },
        'team-sync-hub': {
            'problem': 'Endless meetings and team misalignment', 
            'solution': 'Async-first collaboration that eliminates meeting fatigue'
        },
        'lead-magnet-machine': {
            'problem': 'Low conversion rates and slow email list growth',
            'solution': 'AI-generated lead magnets with conversion-optimized landing pages'
        }
    }

@main_bp.route('/')
def index():
    tools = Tool.query.all()
    tool_descriptions = get_tool_descriptions()
    
    # Define flagship tool (FlowMatic) and Spotlight demo
    flagship = {
        'name': 'FlowMatic',
        'problem': 'Scattered process steps slow you down',
        'solution': 'Auto-generate interactive flowcharts from plain text',
        'route': 'flowmatic.index'
    }
    
    spotlight_tool = {
        'name': 'Spotlight',
        'problem': 'Hidden bottlenecks eat your efficiency',
        'solution': 'Instant Pareto chart from your top metrics—no signup',
        'route': 'spotlight.index'
    }
    
    return render_template('main/index.html', 
                         tools=tools, 
                         tool_descriptions=tool_descriptions,
                         flagship=flagship,
                         spotlight_tool=spotlight_tool)

@main_bp.route('/tools/<path:path>')
def tool_detail(path):
    # Get the markdown page
    page = pages.get_or_404(path)
    
    # Get the tool from database
    tool = Tool.query.filter_by(slug=path).first_or_404()
    
    # Check if user has purchased this tool
    has_purchased = False
    if current_user.is_authenticated:
        purchase = Purchase.query.filter_by(
            user_id=current_user.id,
            tool_id=tool.id
        ).first()
        has_purchased = purchase is not None
    
    return render_template('main/tool_detail.html', 
                         page=page, 
                         tool=tool, 
                         has_purchased=has_purchased)

@main_bp.route('/dashboard')
def dashboard():
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))
    
    # Get user's purchases
    purchases = Purchase.query.filter_by(user_id=current_user.id).all()
    purchased_tools = [purchase.tool for purchase in purchases]
    
    return render_template('main/dashboard.html', 
                         purchased_tools=purchased_tools)
