## Room Data Model

The `Room` model defines the structure of room data stored in the SQLite database. Key fields include:

- `id`: Unique identifier for each room record
- `supplier_code`: Numeric code assigned by the supplier
- `supplier_name`: Name of the supplier providing the room data
- `supplier_room_name`: Original room name as reported by the supplier

This model is central to the standardization process. When new room data is received from suppliers via the `/services/loader.py` service, it is stored in this model. The `supplier_room_name` field serves as the raw input that needs to be matched against other suppliers' data to identify duplicates and generate standardized names.

### Model Usage
1. Created using SQLAlchemy declarative base
2. Tables are initialized in `app/database.py`
3. ORM operations are handled through `app/database.py` methods