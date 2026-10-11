"""
Generic query builder for Quiet Corner Finder.
Designed to absorb unreleased constraints with zero schema migration:
- Maps query parameters to the EAV space_attributes table dynamically
- Handles text search (q) and opening hours (open_now)
- Returns parameterized SQL to prevent SQL injection
"""
from datetime import datetime, timezone, timedelta
import config

IST_ZONE = timezone(timedelta(hours=5, minutes=30), name="IST")

# Generic mapping of query parameter names to space_attributes keys.
# Absorbs new constraints by simply adding (param_name -> attribute_key).
ATTRIBUTE_FILTERS = {
    'activity': 'activities',
    'indoor_outdoor': 'indoor_outdoor',
    'seating_type': 'seating'
}

def build_spaces_query(params, now_ist=None):
    """
    Constructs parameterized SQL and values list based on request query parameters.
    Returns: (sql: str, params_list: list)
    """
    now_ist = now_ist or datetime.now(IST_ZONE)
    current_weekday = now_ist.weekday() # 0 = Monday ... 6 = Sunday
    current_time_str = now_ist.strftime("%H:%M")

    sql_parts = ["SELECT DISTINCT s.* FROM spaces s"]
    joins = []
    where_clauses = []
    sql_params = []

    attr_join_counter = 0

    # 1. Text search across name, building, description
    q = params.get('q', '').strip()
    if q:
        where_clauses.append("(s.name LIKE ? OR s.building LIKE ? OR s.description LIKE ?)")
        like_pattern = f"%{q}%"
        sql_params.extend([like_pattern, like_pattern, like_pattern])

    # 2. Dynamic Attribute Filters (EAV store)
    for param_name, attr_key in ATTRIBUTE_FILTERS.items():
        val = params.get(param_name, '').strip()
        if val:
            alias = f"sa_{attr_join_counter}"
            attr_join_counter += 1
            joins.append(f"JOIN space_attributes {alias} ON s.id = {alias}.space_id")
            where_clauses.append(f"{alias}.key = ? AND {alias}.value LIKE ?")
            sql_params.extend([attr_key, f"%{val}%"])

    # 3. Open Now Filter
    open_now = params.get('open_now')
    if open_now in ('1', 'true', 'yes', True):
        joins.append("""
            JOIN opening_hours oh_now ON s.id = oh_now.space_id
        """)
        where_clauses.append("""
            oh_now.weekday = ? AND oh_now.open_time <= ? AND oh_now.close_time > ?
        """)
        sql_params.extend([current_weekday, current_time_str, current_time_str])

    # Assemble query
    if joins:
        sql_parts.append(" ".join(joins))
    if where_clauses:
        sql_parts.append("WHERE " + " AND ".join(where_clauses))

    sql_parts.append("ORDER BY s.name ASC")
    final_sql = " ".join(sql_parts)

    return final_sql, sql_params
