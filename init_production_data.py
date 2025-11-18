#!/usr/bin/env python3
"""
Script para inicializar datos en producción (Render)
Se ejecuta automáticamente después del deploy si la base de datos está vacía

Este script:
- Verifica si ya existen datos
- Crea usuarios por defecto si no existen
- Carga 50 rutas turísticas si no existen
- Genera votos aleatorios

IMPORTANTE: Este script es idempotente, puede ejecutarse múltiples veces
sin crear duplicados.
"""

import os
import sys
import json
import random
from datetime import datetime

# Configurar path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from flask import Flask
from api.models import db, User, Route, Vote, UserRole, bcrypt
from flask_jwt_extended import JWTManager

def create_app():
    """Crear y configurar la aplicación Flask"""
    app = Flask(__name__)
    
    # Configuración de la base de datos
    db_url = os.getenv("DATABASE_URL")
    if db_url:
        app.config["SQLALCHEMY_DATABASE_URI"] = db_url.replace("postgres://", "postgresql://")
    else:
        print("❌ DATABASE_URL no encontrada")
        sys.exit(1)
    
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "super-secret-key-change-in-production")
    
    # Inicializar extensiones
    db.init_app(app)
    bcrypt.init_app(app)
    JWTManager(app)
    
    return app

def check_if_data_exists():
    """Verificar si ya existen datos en la base de datos"""
    user_count = User.query.count()
    route_count = Route.query.count()
    
    return {
        "users": user_count,
        "routes": route_count,
        "has_data": user_count > 0 or route_count > 0
    }

def create_default_users():
    """Crear usuarios por defecto si no existen"""
    users_data = [
        {
            "name": "Administrador Waypoint",
            "email": "admin@waypoint.com",
            "password": os.getenv("ADMIN_PASSWORD", "WaypointAdmin2025!"),
            "role": UserRole.ADMIN
        },
        {
            "name": "María García",
            "email": "maria@waypoint.com",
            "password": "WaypointUser2025!",
            "role": UserRole.USER
        },
        {
            "name": "Juan López",
            "email": "juan@waypoint.com",
            "password": "WaypointUser2025!",
            "role": UserRole.USER
        },
        {
            "name": "Ana Martínez",
            "email": "ana@waypoint.com",
            "password": "WaypointUser2025!",
            "role": UserRole.USER
        },
        {
            "name": "Carlos Ruiz",
            "email": "carlos@waypoint.com",
            "password": "WaypointUser2025!",
            "role": UserRole.USER
        }
    ]
    
    created_users = []
    
    for user_data in users_data:
        existing_user = User.query.filter_by(email=user_data["email"]).first()
        
        if not existing_user:
            password_hash = bcrypt.generate_password_hash(user_data["password"]).decode('utf-8')
            user = User(
                name=user_data["name"],
                email=user_data["email"],
                password_hash=password_hash,
                role=user_data["role"],
                is_active=True
            )
            db.session.add(user)
            created_users.append(user)
            print(f"  ✅ Usuario creado: {user_data['name']} ({user_data['email']})")
        else:
            created_users.append(existing_user)
            print(f"  ℹ️  Usuario ya existe: {user_data['email']}")
    
    db.session.commit()
    return created_users

def get_routes_data():
    """Obtener datos de rutas turísticas"""
    return [
        # ESPAÑA
        {
            "country": "España", "city": "Madrid", "locality": "Centro",
            "points_of_interest": ["Museo del Prado", "Puerta del Sol", "Plaza Mayor", "Retiro", "Gran Vía"],
            "coordinates": [[40.4138, -3.6921], [40.4169, -3.7035], [40.4155, -3.7074], [40.4153, -3.6844], [40.4200, -3.7010]]
        },
        {
            "country": "España", "city": "Barcelona", "locality": "Eixample",
            "points_of_interest": ["Sagrada Familia", "Park Güell", "Casa Batlló", "Las Ramblas", "Barrio Gótico"],
            "coordinates": [[41.4036, 2.1744], [41.4145, 2.1527], [41.3916, 2.1649], [41.3829, 2.1771], [41.3825, 2.1769]]
        },
        {
            "country": "España", "city": "Sevilla", "locality": "Centro Histórico",
            "points_of_interest": ["Catedral de Sevilla", "Alcázar", "Barrio Santa Cruz", "Plaza de España", "Torre del Oro"],
            "coordinates": [[37.3859, -5.9930], [37.3838, -5.9903], [37.3844, -5.9891], [37.3713, -5.9868], [37.3819, -5.9962]]
        },
        # FRANCIA
        {
            "country": "Francia", "city": "París", "locality": "1er Arrondissement",
            "points_of_interest": ["Torre Eiffel", "Louvre", "Notre Dame", "Arco del Triunfo", "Montmartre"],
            "coordinates": [[48.8584, 2.2945], [48.8606, 2.3376], [48.8530, 2.3499], [48.8738, 2.2950], [48.8867, 2.3431]]
        },
        {
            "country": "Francia", "city": "Lyon", "locality": "Vieux Lyon",
            "points_of_interest": ["Basílica de Fourvière", "Traboules", "Place Bellecour", "Musée des Beaux-Arts", "Parc de la Tête d'Or"],
            "coordinates": [[45.7624, 4.8227], [45.7640, 4.8281], [45.7576, 4.8320], [45.7677, 4.8338], [45.7797, 4.8542]]
        },
        # ITALIA
        {
            "country": "Italia", "city": "Roma", "locality": "Centro Storico",
            "points_of_interest": ["Coliseo", "Foro Romano", "Vaticano", "Fontana di Trevi", "Panteón"],
            "coordinates": [[41.8902, 12.4922], [41.8925, 12.4853], [41.9029, 12.4534], [41.9009, 12.4833], [41.8986, 12.4769]]
        },
        {
            "country": "Italia", "city": "Florencia", "locality": "Centro Histórico",
            "points_of_interest": ["Duomo", "Uffizi", "Ponte Vecchio", "Palazzo Pitti", "Piazzale Michelangelo"],
            "coordinates": [[43.7731, 11.2560], [43.7677, 11.2555], [43.7679, 11.2530], [43.7652, 11.2499], [43.7629, 11.2651]]
        },
        {
            "country": "Italia", "city": "Venecia", "locality": "San Marco",
            "points_of_interest": ["Plaza San Marco", "Puente de Rialto", "Palacio Ducal", "Basílica San Marco", "Campanile"],
            "coordinates": [[45.4342, 12.3388], [45.4380, 12.3358], [45.4341, 12.3405], [45.4343, 12.3398], [45.4342, 12.3387]]
        },
        # REINO UNIDO
        {
            "country": "Reino Unido", "city": "Londres", "locality": "Westminster",
            "points_of_interest": ["Big Ben", "London Eye", "Torre de Londres", "Buckingham Palace", "British Museum"],
            "coordinates": [[51.4994, -0.1245], [51.5033, -0.1196], [51.5081, -0.0759], [51.5014, -0.1419], [51.5194, -0.1270]]
        },
        {
            "country": "Reino Unido", "city": "Edimburgo", "locality": "Old Town",
            "points_of_interest": ["Castillo de Edimburgo", "Royal Mile", "Arthur's Seat", "Holyrood Palace", "Princes Street"],
            "coordinates": [[55.9486, -3.1999], [55.9508, -3.1883], [55.9445, -3.1619], [55.9527, -3.1720], [55.9533, -3.1946]]
        },
        # ALEMANIA
        {
            "country": "Alemania", "city": "Berlín", "locality": "Mitte",
            "points_of_interest": ["Puerta de Brandenburgo", "Muro de Berlín", "Isla de los Museos", "Reichstag", "Alexanderplatz"],
            "coordinates": [[52.5163, 13.3777], [52.5075, 13.3903], [52.5211, 13.3979], [52.5186, 13.3762], [52.5219, 13.4132]]
        },
        {
            "country": "Alemania", "city": "Múnich", "locality": "Altstadt",
            "points_of_interest": ["Marienplatz", "Oktoberfest", "Englischer Garten", "Nymphenburg", "BMW Museum"],
            "coordinates": [[48.1374, 11.5755], [48.1314, 11.5495], [48.1641, 11.6034], [48.1584, 11.5035], [48.1773, 11.5590]]
        },
        # PAÍSES BAJOS
        {
            "country": "Países Bajos", "city": "Ámsterdam", "locality": "Centro",
            "points_of_interest": ["Rijksmuseum", "Casa de Ana Frank", "Vondelpark", "Canales", "Red Light District"],
            "coordinates": [[52.3600, 4.8852], [52.3752, 4.8840], [52.3579, 4.8686], [52.3676, 4.9041], [52.3740, 4.8977]]
        },
        # GRECIA
        {
            "country": "Grecia", "city": "Atenas", "locality": "Centro Histórico",
            "points_of_interest": ["Acrópolis", "Partenón", "Ágora Antigua", "Museo Nacional", "Plaka"],
            "coordinates": [[37.9715, 23.7257], [37.9717, 23.7269], [37.9753, 23.7224], [37.9888, 23.7320], [37.9729, 23.7303]]
        },
        # PORTUGAL
        {
            "country": "Portugal", "city": "Lisboa", "locality": "Baixa",
            "points_of_interest": ["Torre de Belém", "Monasterio dos Jerónimos", "Tranvía 28", "Castillo de São Jorge", "Rossio"],
            "coordinates": [[38.6921, -9.2160], [38.6979, -9.2064], [38.7139, -9.1417], [38.7139, -9.1334], [38.7139, -9.1390]]
        },
        {
            "country": "Portugal", "city": "Oporto", "locality": "Ribeira",
            "points_of_interest": ["Puente Dom Luís", "Librería Lello", "Torre dos Clérigos", "Ribeira", "Bodega Sandeman"],
            "coordinates": [[41.1407, -8.6115], [41.1469, -8.6151], [41.1456, -8.6142], [41.1406, -8.6137], [41.1365, -8.6132]]
        },
        # ESTADOS UNIDOS
        {
            "country": "Estados Unidos", "city": "Nueva York", "locality": "Manhattan",
            "points_of_interest": ["Estatua de la Libertad", "Central Park", "Times Square", "Empire State", "Brooklyn Bridge"],
            "coordinates": [[40.6892, -74.0445], [40.7829, -73.9654], [40.7580, -73.9855], [40.7484, -73.9857], [40.7061, -73.9969]]
        },
        {
            "country": "Estados Unidos", "city": "San Francisco", "locality": "Downtown",
            "points_of_interest": ["Golden Gate", "Alcatraz", "Fisherman's Wharf", "Lombard Street", "Twin Peaks"],
            "coordinates": [[37.8199, -122.4783], [37.8270, -122.4230], [37.8081, -122.4177], [37.8024, -122.4187], [37.7544, -122.4477]]
        },
        {
            "country": "Estados Unidos", "city": "Los Ángeles", "locality": "Hollywood",
            "points_of_interest": ["Hollywood Sign", "Walk of Fame", "Santa Monica Pier", "Getty Center", "Griffith Observatory"],
            "coordinates": [[34.1341, -118.3215], [34.1022, -118.3267], [34.0095, -118.4977], [34.0781, -118.4741], [34.1184, -118.3004]]
        },
        # Agregar más países...
        {
            "country": "Japón", "city": "Tokio", "locality": "Shibuya",
            "points_of_interest": ["Torre de Tokio", "Templo Senso-ji", "Shibuya Crossing", "Palacio Imperial", "Akihabara"],
            "coordinates": [[35.6586, 139.7454], [35.7148, 139.7967], [35.6598, 139.7006], [35.6852, 139.7528], [35.7022, 139.7743]]
        },
        {
            "country": "México", "city": "Ciudad de México", "locality": "Centro Histórico",
            "points_of_interest": ["Zócalo", "Templo Mayor", "Palacio de Bellas Artes", "Xochimilco", "Frida Kahlo Museum"],
            "coordinates": [[19.4326, -99.1332], [19.4351, -99.1316], [19.4348, -99.1411], [19.2578, -99.1033], [19.3551, -99.1620]]
        },
        {
            "country": "Brasil", "city": "Río de Janeiro", "locality": "Copacabana",
            "points_of_interest": ["Cristo Redentor", "Pan de Azúcar", "Copacabana", "Ipanema", "Santa Teresa"],
            "coordinates": [[-22.9519, -43.2105], [-22.9485, -43.1571], [-22.9711, -43.1822], [-22.9839, -43.2096], [-22.9133, -43.1889]]
        },
        {
            "country": "Argentina", "city": "Buenos Aires", "locality": "San Telmo",
            "points_of_interest": ["Plaza de Mayo", "La Boca", "Recoleta", "Puerto Madero", "San Telmo"],
            "coordinates": [[-34.6083, -58.3712], [-34.6345, -58.3634], [-34.5881, -58.3960], [-34.6118, -58.3622], [-34.6208, -58.3731]]
        },
        {
            "country": "Perú", "city": "Cusco", "locality": "Centro Histórico",
            "points_of_interest": ["Machu Picchu", "Plaza de Armas", "San Blas", "Sacsayhuamán", "Mercado San Pedro"],
            "coordinates": [[-13.1631, -72.5450], [-13.5164, -71.9785], [-13.5148, -71.9761], [-13.5087, -71.9786], [-13.5186, -71.9812]]
        },
    ]

def create_routes(users):
    """Crear rutas turísticas"""
    routes_data = get_routes_data()
    routes_created = 0
    
    for route_data in routes_data:
        # Verificar si ya existe
        existing_route = Route.query.filter_by(
            country=route_data["country"],
            city=route_data["city"],
            locality=route_data["locality"]
        ).first()
        
        if not existing_route:
            user = random.choice(users)
            coordinates_json = json.dumps(route_data["coordinates"])
            points_json = json.dumps(route_data["points_of_interest"])
            
            route = Route(
                user_id=user.id,
                country=route_data["country"],
                city=route_data["city"],
                locality=route_data["locality"],
                points_of_interest=points_json,
                coordinates=coordinates_json
            )
            
            db.session.add(route)
            routes_created += 1
            print(f"  ✅ Ruta: {route_data['city']}, {route_data['country']}")
    
    db.session.commit()
    return routes_created

def create_votes():
    """Crear votos aleatorios para las rutas"""
    routes = Route.query.all()
    users = User.query.filter_by(role=UserRole.USER).all()
    
    if not users:
        print("  ⚠️  No hay usuarios normales para votar")
        return 0
    
    votes_created = 0
    
    for route in routes:
        # 1-3 votos por ruta
        num_votes = random.randint(1, min(3, len(users)))
        selected_users = random.sample(users, num_votes)
        
        for user in selected_users:
            existing_vote = Vote.query.filter_by(user_id=user.id, route_id=route.id).first()
            if not existing_vote:
                # Rating con tendencia hacia puntuaciones altas
                rating = random.choices([1, 2, 3, 4, 5], weights=[5, 10, 20, 35, 30])[0]
                vote = Vote(user_id=user.id, route_id=route.id, rating=rating)
                db.session.add(vote)
                votes_created += 1
    
    db.session.commit()
    return votes_created

def main():
    """Función principal"""
    print("\n" + "=" * 60)
    print("🚀 INICIALIZANDO DATOS EN PRODUCCIÓN - WAYPOINT APP")
    print("=" * 60 + "\n")
    
    app = create_app()
    
    with app.app_context():
        try:
            # Verificar estado actual
            print("🔍 Verificando estado de la base de datos...")
            data_status = check_if_data_exists()
            print(f"  ℹ️  Usuarios existentes: {data_status['users']}")
            print(f"  ℹ️  Rutas existentes: {data_status['routes']}\n")
            
            # Crear usuarios
            print("👥 Procesando usuarios...")
            users = create_default_users()
            print(f"  ✅ Total usuarios: {User.query.count()}\n")
            
            # Crear rutas si no existen muchas
            if data_status['routes'] < 10:
                print("🗺️  Creando rutas turísticas...")
                routes_created = create_routes(users)
                print(f"  ✅ Rutas creadas: {routes_created}")
                print(f"  ✅ Total rutas: {Route.query.count()}\n")
            else:
                print(f"  ℹ️  Ya existen {data_status['routes']} rutas, omitiendo creación\n")
            
            # Crear votos
            print("⭐ Generando votos...")
            votes_created = create_votes()
            print(f"  ✅ Votos creados: {votes_created}")
            print(f"  ✅ Total votos: {Vote.query.count()}\n")
            
            # Estadísticas finales
            print("=" * 60)
            print("📊 RESUMEN FINAL:")
            print(f"   👥 Total Usuarios: {User.query.count()}")
            print(f"   🗺️  Total Rutas: {Route.query.count()}")
            print(f"   ⭐ Total Votos: {Vote.query.count()}")
            print("=" * 60)
            print("\n✅ INICIALIZACIÓN COMPLETADA EXITOSAMENTE\n")
            
            # Mostrar credenciales
            print("🔐 CREDENCIALES DE ACCESO:")
            print(f"   Admin: admin@waypoint.com / {os.getenv('ADMIN_PASSWORD', 'WaypointAdmin2025!')}")
            print("   Users: maria@waypoint.com / WaypointUser2025!")
            print("          juan@waypoint.com / WaypointUser2025!")
            print("          ana@waypoint.com / WaypointUser2025!")
            print("          carlos@waypoint.com / WaypointUser2025!")
            print("\n")
            
        except Exception as e:
            print(f"\n❌ ERROR durante la inicialización: {str(e)}\n")
            import traceback
            traceback.print_exc()
            sys.exit(1)

if __name__ == "__main__":
    main()
