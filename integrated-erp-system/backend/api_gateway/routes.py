# API Gateway Routes for Integrated ERP System

from flask import Blueprint, request, jsonify, current_app
from functools import wraps
import jwt
import frappe
from frappe import _
from frappe.utils import now, get_datetime
import json

# Create Blueprint
api = Blueprint('api', __name__, url_prefix='/api')

# JWT Secret Key (should be in environment variables)
JWT_SECRET_KEY = 'your-secret-key-here'

def token_required(f):
    """Decorator to require JWT token"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        
        if not token:
            return jsonify({'error': 'No token provided'}), 401
        
        try:
            if token.startswith('Bearer '):
                token = token[7:]
            
            data = jwt.decode(token, JWT_SECRET_KEY, algorithms=['HS256'])
            current_user = frappe.get_doc('User', data['user_id'])
            
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401
        except Exception as e:
            return jsonify({'error': 'Token validation failed'}), 401
        
        return f(current_user, *args, **kwargs)
    return decorated

def require_permission(permission):
    """Decorator to require specific permission"""
    def decorator(f):
        @wraps(f)
        def decorated(current_user, *args, **kwargs):
            if not current_user.has_permission(permission):
                return jsonify({'error': 'Insufficient permissions'}), 403
            return f(current_user, *args, **kwargs)
        return decorated
    return decorator

# Authentication Routes
@api.route('/auth/login', methods=['POST'])
def login():
    """User login endpoint"""
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({'error': 'Email and password required'}), 400
        
        # Authenticate user
        user = frappe.get_doc('User', email)
        if not user or not user.check_password(password):
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # Generate JWT token
        token = jwt.encode({
            'user_id': user.name,
            'email': user.email,
            'exp': get_datetime(now()).timestamp() + 3600  # 1 hour expiry
        }, JWT_SECRET_KEY, algorithm='HS256')
        
        return jsonify({
            'success': True,
            'token': token,
            'user': {
                'name': user.name,
                'email': user.email,
                'full_name': user.full_name,
                'roles': [role.role for role in user.roles]
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/auth/refresh', methods=['POST'])
@token_required
def refresh_token(current_user):
    """Refresh JWT token"""
    try:
        token = jwt.encode({
            'user_id': current_user.name,
            'email': current_user.email,
            'exp': get_datetime(now()).timestamp() + 3600
        }, JWT_SECRET_KEY, algorithm='HS256')
        
        return jsonify({
            'success': True,
            'token': token
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Maintenance Module Routes
@api.route('/maintenance/tickets', methods=['GET'])
@token_required
def get_tickets(current_user):
    """Get maintenance tickets"""
    try:
        filters = request.args.to_dict()
        
        # Build query filters
        query_filters = {}
        if filters.get('status'):
            query_filters['status'] = filters['status']
        if filters.get('priority'):
            query_filters['priority'] = filters['priority']
        if filters.get('assigned_to'):
            query_filters['assigned_to'] = filters['assigned_to']
        
        # Get tickets
        tickets = frappe.get_all('Maintenance Ticket',
            filters=query_filters,
            fields=['*'],
            order_by='creation desc',
            limit=50
        )
        
        return jsonify({
            'success': True,
            'data': tickets
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/maintenance/tickets', methods=['POST'])
@token_required
@require_permission('Maintenance Ticket')
def create_ticket(current_user):
    """Create maintenance ticket"""
    try:
        data = request.get_json()
        
        # Create ticket
        ticket = frappe.get_doc({
            'doctype': 'Maintenance Ticket',
            'subject': data.get('subject'),
            'description': data.get('description'),
            'priority': data.get('priority', 'Medium'),
            'customer': data.get('customer'),
            'assigned_to': data.get('assigned_to'),
            'ticket_type': data.get('ticket_type', 'Support'),
            'source': data.get('source', 'API')
        })
        
        ticket.insert()
        
        return jsonify({
            'success': True,
            'data': {
                'ticket_id': ticket.name,
                'ticket_number': ticket.ticket_number
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/maintenance/tickets/<ticket_id>', methods=['GET'])
@token_required
def get_ticket(current_user, ticket_id):
    """Get specific ticket"""
    try:
        ticket = frappe.get_doc('Maintenance Ticket', ticket_id)
        
        return jsonify({
            'success': True,
            'data': ticket.as_dict()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/maintenance/tickets/<ticket_id>', methods=['PUT'])
@token_required
@require_permission('Maintenance Ticket')
def update_ticket(current_user, ticket_id):
    """Update ticket"""
    try:
        data = request.get_json()
        ticket = frappe.get_doc('Maintenance Ticket', ticket_id)
        
        # Update fields
        for field, value in data.items():
            if hasattr(ticket, field):
                setattr(ticket, field, value)
        
        ticket.save()
        
        return jsonify({
            'success': True,
            'data': ticket.as_dict()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/maintenance/tickets/<ticket_id>/escalate', methods=['POST'])
@token_required
@require_permission('Maintenance Ticket')
def escalate_ticket(current_user, ticket_id):
    """Escalate ticket"""
    try:
        data = request.get_json()
        reason = data.get('reason', 'Manual escalation')
        
        # Import the escalate function
        from erpnext.maintenance.doctype.maintenance_ticket.maintenance_ticket import escalate_ticket as escalate_func
        
        result = escalate_func(ticket_id, reason)
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/maintenance/analytics', methods=['GET'])
@token_required
def get_maintenance_analytics(current_user):
    """Get maintenance analytics"""
    try:
        from erpnext.maintenance.doctype.maintenance_ticket.maintenance_ticket import get_ticket_analytics
        
        filters = request.args.to_dict()
        analytics = get_ticket_analytics(filters)
        
        return jsonify({
            'success': True,
            'data': analytics
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Supply Chain Module Routes
@api.route('/supply-chain/inventory', methods=['GET'])
@token_required
def get_inventory(current_user):
    """Get inventory balances"""
    try:
        filters = request.args.to_dict()
        
        # Build query filters
        query_filters = {}
        if filters.get('warehouse'):
            query_filters['warehouse'] = filters['warehouse']
        if filters.get('item_code'):
            query_filters['item_code'] = filters['item_code']
        
        # Get inventory balances
        balances = frappe.get_all('Bin',
            filters=query_filters,
            fields=['item_code', 'warehouse', 'actual_qty', 'reserved_qty', 'projected_qty'],
            order_by='item_code'
        )
        
        return jsonify({
            'success': True,
            'data': balances
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/supply-chain/reorder-recommendations', methods=['GET'])
@token_required
def get_reorder_recommendations(current_user):
    """Get reorder recommendations"""
    try:
        filters = request.args.to_dict()
        
        # Build query filters
        query_filters = {}
        if filters.get('status'):
            query_filters['status'] = filters['status']
        if filters.get('priority'):
            query_filters['priority'] = filters['priority']
        
        # Get recommendations
        recommendations = frappe.get_all('Reorder Recommendation',
            filters=query_filters,
            fields=['*'],
            order_by='creation desc',
            limit=50
        )
        
        return jsonify({
            'success': True,
            'data': recommendations
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/supply-chain/reorder-recommendations', methods=['POST'])
@token_required
@require_permission('Reorder Recommendation')
def create_reorder_recommendation(current_user):
    """Create reorder recommendation"""
    try:
        data = request.get_json()
        
        # Create recommendation
        recommendation = frappe.get_doc({
            'doctype': 'Reorder Recommendation',
            'item_code': data.get('item_code'),
            'warehouse': data.get('warehouse'),
            'recommended_qty': data.get('recommended_qty'),
            'unit_cost': data.get('unit_cost'),
            'required_date': data.get('required_date')
        })
        
        recommendation.insert()
        
        return jsonify({
            'success': True,
            'data': {
                'recommendation_id': recommendation.name
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/supply-chain/reorder-recommendations/<rec_id>/approve', methods=['POST'])
@token_required
@require_permission('Reorder Recommendation')
def approve_recommendation(current_user, rec_id):
    """Approve reorder recommendation"""
    try:
        recommendation = frappe.get_doc('Reorder Recommendation', rec_id)
        recommendation.approve_recommendation()
        
        return jsonify({
            'success': True,
            'data': recommendation.as_dict()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/supply-chain/analytics', methods=['GET'])
@token_required
def get_supply_chain_analytics(current_user):
    """Get supply chain analytics"""
    try:
        from erpnext.supply_chain.doctype.reorder_recommendation.reorder_recommendation import get_recommendation_analytics
        
        filters = request.args.to_dict()
        analytics = get_recommendation_analytics(filters)
        
        return jsonify({
            'success': True,
            'data': analytics
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# CRM Module Routes
@api.route('/crm/customers', methods=['GET'])
@token_required
def get_customers(current_user):
    """Get customers"""
    try:
        filters = request.args.to_dict()
        
        # Build query filters
        query_filters = {}
        if filters.get('customer_group'):
            query_filters['customer_group'] = filters['customer_group']
        if filters.get('territory'):
            query_filters['territory'] = filters['territory']
        
        # Get customers
        customers = frappe.get_all('Customer',
            filters=query_filters,
            fields=['*'],
            order_by='customer_name',
            limit=50
        )
        
        return jsonify({
            'success': True,
            'data': customers
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/crm/customers/<customer_id>', methods=['GET'])
@token_required
def get_customer(current_user, customer_id):
    """Get specific customer"""
    try:
        customer = frappe.get_doc('Customer', customer_id)
        
        return jsonify({
            'success': True,
            'data': customer.as_dict()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/crm/analytics', methods=['GET'])
@token_required
def get_crm_analytics(current_user):
    """Get CRM analytics"""
    try:
        # Get customer statistics
        stats = frappe.db.sql("""
            SELECT 
                COUNT(*) as total_customers,
                SUM(CASE WHEN disabled = 0 THEN 1 ELSE 0 END) as active_customers,
                SUM(CASE WHEN creation >= DATE_SUB(NOW(), INTERVAL 30 DAY) THEN 1 ELSE 0 END) as new_customers
            FROM `tabCustomer`
        """, as_dict=True)
        
        return jsonify({
            'success': True,
            'data': stats[0] if stats else {}
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# AI Analytics Routes
@api.route('/ai/insights', methods=['GET'])
@token_required
def get_ai_insights(current_user):
    """Get AI insights"""
    try:
        module = request.args.get('module', 'all')
        
        insights = {
            'maintenance': {
                'sentiment_trends': get_sentiment_trends(),
                'performance_metrics': get_performance_metrics(),
                'predictions': get_maintenance_predictions()
            },
            'supply_chain': {
                'demand_forecasts': get_demand_forecasts(),
                'optimization_opportunities': get_optimization_opportunities(),
                'risk_alerts': get_risk_alerts()
            },
            'crm': {
                'customer_insights': get_customer_insights(),
                'churn_predictions': get_churn_predictions(),
                'upsell_opportunities': get_upsell_opportunities()
            }
        }
        
        if module != 'all':
            insights = {module: insights.get(module, {})}
        
        return jsonify({
            'success': True,
            'data': insights
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Helper functions for AI insights
def get_sentiment_trends():
    """Get sentiment trends for maintenance tickets"""
    # This would integrate with AI service
    return {
        'overall_sentiment': 0.7,
        'trend': 'improving',
        'key_insights': [
            'Customer satisfaction improved by 15%',
            'Response time reduced by 20%',
            'Resolution rate increased by 10%'
        ]
    }

def get_performance_metrics():
    """Get performance metrics"""
    return {
        'avg_resolution_time': 4.2,
        'customer_satisfaction': 4.5,
        'first_response_time': 2.1,
        'escalation_rate': 0.15
    }

def get_maintenance_predictions():
    """Get maintenance predictions"""
    return {
        'predicted_tickets': 45,
        'resource_requirements': 8,
        'priority_distribution': {
            'critical': 2,
            'high': 8,
            'medium': 25,
            'low': 10
        }
    }

def get_demand_forecasts():
    """Get demand forecasts"""
    return {
        'next_month_demand': 1250,
        'confidence_level': 0.85,
        'trend': 'increasing',
        'seasonal_factors': ['Holiday season', 'Product launch']
    }

def get_optimization_opportunities():
    """Get optimization opportunities"""
    return [
        'Consolidate orders with Vendor A to save 15%',
        'Implement just-in-time inventory for fast-moving items',
        'Negotiate volume discounts with top 3 suppliers'
    ]

def get_risk_alerts():
    """Get risk alerts"""
    return [
        'Supplier X has 20% delivery delay risk',
        'Item Y stockout probability: 35%',
        'Currency fluctuation impact: 5% cost increase'
    ]

def get_customer_insights():
    """Get customer insights"""
    return {
        'top_customers': ['Customer A', 'Customer B', 'Customer C'],
        'growth_opportunities': ['Customer D', 'Customer E'],
        'churn_risk': ['Customer F', 'Customer G']
    }

def get_churn_predictions():
    """Get churn predictions"""
    return {
        'high_risk_customers': 5,
        'medium_risk_customers': 12,
        'retention_strategies': [
            'Proactive support outreach',
            'Custom pricing offers',
            'Enhanced service levels'
        ]
    }

def get_upsell_opportunities():
    """Get upsell opportunities"""
    return [
        'Customer A: Premium support package',
        'Customer B: Additional modules',
        'Customer C: Extended warranty'
    ]

# Health check endpoint
@api.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': now().isoformat(),
        'version': '1.0.0'
    })

# Error handlers
@api.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@api.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500
