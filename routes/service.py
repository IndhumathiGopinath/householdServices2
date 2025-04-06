from flask import Blueprint, render_template, jsonify
from models import Service, Professional

service_bp = Blueprint('service', __name__)

@service_bp.route('/list')
def list_services():
    services = Service.query.filter_by(is_active=True).all()
    return render_template('services/list.html', services=services)

@service_bp.route('/detail/<int:service_id>')
def service_detail(service_id):
    service = Service.query.get_or_404(service_id)
    professionals = Professional.query.filter_by(
        service_id=service.id,
        is_verified=True
    ).all()
    return render_template('services/detail.html', service=service, professionals=professionals)

@service_bp.route('/search/<query>')
def search_services(query):
    services = Service.query.filter(
        Service.name.ilike(f'%{query}%') | 
        Service.description.ilike(f'%{query}%')
    ).filter_by(is_active=True).all()
    
    return render_template('services/search_results.html', services=services, query=query)

@service_bp.route('/api/list')
def api_list_services():
    services = Service.query.filter_by(is_active=True).all()
    return jsonify([{
        'id': s.id,
        'name': s.name,
        'description': s.description,
        'base_price': s.base_price,
        'time_required': s.time_required
    } for s in services])
