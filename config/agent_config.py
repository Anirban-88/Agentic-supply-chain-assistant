# config/agent_config.py

# Agent Configuration
AGENT_CONFIG = {
    'product_agent': {
        'name': 'Product & Inventory Agent',
        'description': 'Handles queries about products, inventory, locations, and stock levels',
        'keywords': ['product', 'inventory', 'stock', 'quantity', 'price', 'location', 'aisle', 'rack', 'reorder']
    },
    'supply_chain_agent': {
        'name': 'Supply Chain Agent',
        'description': 'Handles queries about shipments, warehouses, and deliveries',
        'keywords': ['shipment', 'delivery', 'warehouse', 'tracking', 'eta', 'transit', 'carrier']
    },
    'expiry_agent': {
        'name': 'Expiry Management Agent',
        'description': 'Handles queries about product expiry, batches, and freshness',
        'keywords': ['expiry', 'expire', 'expiring', 'batch', 'fresh', 'shelf life', 'perishable']
    },
    'graph_agent': {
        'name': 'Knowledge Graph Agent',
        'description': 'Handles complex cross-database queries and relationships',
        'keywords': ['relationship', 'connected', 'supplier for', 'supply chain', 'everything about', 'complete']
    }
}

# Orchestrator Configuration
ORCHESTRATOR_CONFIG = {
    'max_agents_per_query': 3,
    'timeout_seconds': 30,
    'enable_logging': True,
    'confidence_threshold': 0.3  # Minimum confidence to select agent
}