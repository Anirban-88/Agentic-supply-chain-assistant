

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import time
import random
from datetime import datetime, timedelta
from pymongo import MongoClient
from config.db_config import MONGO_CONFIG

def simulate_realtime_updates(interval_minutes=5):
    """Simulate real-time supply chain updates"""
    
    try:
        client = MongoClient(MONGO_CONFIG['uri'], serverSelectionTimeoutMS=5000)
        db = client[MONGO_CONFIG['database']]
        
        print(f"🔄 Starting real-time simulation (updates every {interval_minutes} minutes)...")
        print("Press Ctrl+C to stop\n")
        
    except Exception as e:
        print(f"❌ Cannot connect to MongoDB: {e}")
        return
    
    cities = ['Mumbai', 'Pune', 'Delhi', 'Bangalore', 'Chennai', 'Kolkata', 
              'Nashik', 'Lonavala', 'Thane', 'Surat']
    
    iteration = 0
    
    while True:
        try:
            iteration += 1
            print(f"\n{'='*60}")
            print(f"⏰ Update Cycle #{iteration} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"{'='*60}")
            
            # Update shipments
            active_shipments = db.shipments.find({
                'status': {'$in': ['picked_up', 'in_transit', 'out_for_delivery']}
            })
            
            shipment_count = 0
            for shipment in active_shipments:
                new_location = random.choice(cities)
                
                status_progression = {
                    'picked_up': 'in_transit',
                    'in_transit': random.choice(['in_transit', 'out_for_delivery']),
                    'out_for_delivery': random.choice(['out_for_delivery', 'delivered'])
                }
                
                new_status = status_progression.get(shipment['status'], shipment['status'])
                
                departed = datetime.fromisoformat(shipment['origin']['departed_at'])
                eta = datetime.fromisoformat(shipment['destination']['estimated_arrival'])
                total_time = (eta - departed).total_seconds()
                elapsed_time = (datetime.now() - departed).total_seconds()
                progress = min(int((elapsed_time / total_time) * 100), 100)
                
                db.shipments.update_one(
                    {'shipment_id': shipment['shipment_id']},
                    {
                        '$set': {
                            'status': new_status,
                            'current_location': {
                                'city': new_location,
                                'coordinates': [
                                    round(random.uniform(72, 78), 4),
                                    round(random.uniform(18, 29), 4)
                                ],
                                'updated_at': datetime.now().isoformat()
                            },
                            'progress_percentage': progress,
                            'last_updated': datetime.now().isoformat()
                        }
                    }
                )
                
                shipment_count += 1
                print(f"  📦 {shipment['shipment_id']}: {shipment['status']} → {new_status} | {new_location} ({progress}%)")
            
            if shipment_count == 0:
                print("  ℹ️  No active shipments to update")
            else:
                print(f"\n  ✅ Updated {shipment_count} shipments")
            
            # Update warehouse inventory
            warehouses = db.warehouses.find()
            warehouse_count = 0
            
            for warehouse in warehouses:
                num_updates = random.randint(1, 5)
                products_to_update = random.sample(warehouse['products'], 
                                                   min(num_updates, len(warehouse['products'])))
                
                for product in products_to_update:
                    quantity_change = random.randint(-50, 100)
                    new_quantity = max(0, product['quantity'] + quantity_change)
                    new_reserved = random.randint(0, int(new_quantity * 0.2))
                    
                    db.warehouses.update_one(
                        {
                            'warehouse_id': warehouse['warehouse_id'],
                            'products.product_id': product['product_id']
                        },
                        {
                            '$set': {
                                'products.$.quantity': new_quantity,
                                'products.$.reserved': new_reserved,
                                'products.$.available': new_quantity - new_reserved,
                                'products.$.last_updated': datetime.now().isoformat(),
                                'last_updated': datetime.now().isoformat()
                            }
                        }
                    )
                
                warehouse_count += 1
                print(f"  🏢 {warehouse['warehouse_id']}: Updated {num_updates} products")
            
            print(f"\n  ✅ Updated {warehouse_count} warehouses")
            print(f"\n⏰ Next update in {interval_minutes} minutes...")
            
            time.sleep(interval_minutes * 60)
            
        except KeyboardInterrupt:
            print("\n\n🛑 Stopping simulation...")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            print("Retrying in 60 seconds...")
            time.sleep(60)
    
    client.close()
    print("✅ Simulation stopped")

if __name__ == "__main__":
    # You can change the interval here (in minutes)
    simulate_realtime_updates(interval_minutes=5)