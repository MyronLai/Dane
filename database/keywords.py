from enum import Enum

class SQLKeywords(Enum):
    SELECT = 'SELECT'
    INSERT = 'INSERT INTO'
    CREATE = 'CREATE'
    DELETE = 'DELETE FROM'
    ALTER_COLUMN = 'ALTER COLUMN'
    ALTER_TABLE = 'ALTER TABLE'
    