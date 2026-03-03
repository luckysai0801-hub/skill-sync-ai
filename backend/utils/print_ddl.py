import os, sys

# compute project root and add to path
root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, root)

from backend.database import Base
# import models so they register themselves with Base.metadata
from backend.models import user, resume, job, match
from sqlalchemy.dialects import postgresql
from sqlalchemy.schema import CreateTable
from sqlalchemy import Enum as SAEnum

# first print any custom enum types used in the models
seen = set()
for table in Base.metadata.sorted_tables:
    for col in table.columns:
        if isinstance(col.type, SAEnum):
            enum_obj = col.type
            # SQLAlchemy generates a custom type name based on the Python enum
            typname = enum_obj.name or enum_obj.enum.__name__.lower()
            if typname not in seen:
                seen.add(typname)
                # `enum_obj.enums` may contain Python enum members or raw strings
                vals_list = []
                for v in enum_obj.enums:
                    if hasattr(v, 'value'):
                        vals_list.append(v.value)
                    else:
                        vals_list.append(v)
                vals = ", ".join(f"'{val}'" for val in vals_list)
                print(f"CREATE TYPE {typname} AS ENUM ({vals});\n")

for table in Base.metadata.sorted_tables:
    print(str(CreateTable(table).compile(dialect=postgresql.dialect())))
