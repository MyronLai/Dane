from enum import Enum

class SQLKeywords(Enum):
    SELECT = 'SELECT'
    INSERT = 'INSERT INTO'
    CREATE = 'CREATE'
    DELETE = 'DELETE FROM'
    ALTER_COLUMN = 'ALTER COLUMN'
    ALTER_TABLE = 'ALTER TABLE'

    WHERE = 'WHERE'
    
class SQLTables(Enum):
    GUILDS = 'Guilds'
    USERS = 'Users'