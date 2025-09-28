# Neo4j Database Setup Documentation

## Installation Details

Neo4j Community Edition has been successfully installed and configured for the Brazil Knowledge Graph project.

### Version Information
- **Neo4j Version**: Latest Community Edition (2025.09.0)
- **Java Runtime**: OpenJDK 21.0.7 LTS
- **Operating System**: Ubuntu 24.04.2 LTS

### Database Configuration

- **Database Name**: brazil-kg (default database)
- **Username**: neo4j
- **Password**: neo4j123
- **Port**: 7474 (HTTP)
- **Bolt Port**: 7687 (Database connection)

### Access Points

- **Neo4j Browser**: http://localhost:7474
- **Bolt Connection**: bolt://localhost:7687

### Service Management

```bash
# Start Neo4j
sudo service neo4j start

# Stop Neo4j
sudo service neo4j stop

# Check Status
sudo service neo4j status

# Restart Neo4j
sudo service neo4j restart
```

### Connection Details for Development

#### Python Connection Example
```python
from neo4j import GraphDatabase

uri = "bolt://localhost:7687"
driver = GraphDatabase.driver(uri, auth=("neo4j", "neo4j123"))

def test_connection():
    with driver.session() as session:
        result = session.run("MATCH (n) RETURN count(n) as count")
        return result.single()["count"]

# Close the driver when done
driver.close()
```

#### JavaScript/Node.js Connection Example
```javascript
const neo4j = require('neo4j-driver');

const driver = neo4j.driver(
    'bolt://localhost:7687',
    neo4j.auth.basic('neo4j', 'neo4j123')
);

async function testConnection() {
    const session = driver.session();
    try {
        const result = await session.run('MATCH (n) RETURN count(n) as count');
        const count = result.records[0].get('count');
        console.log(`Node count: ${count}`);
    } finally {
        await session.close();
    }
}

// Close driver when done
await driver.close();
```

### Cypher Shell Access

You can interact with the database using cypher-shell:

```bash
# Connect to the database
cypher-shell -u neo4j -p neo4j123

# Example queries
MATCH (n) RETURN count(n);
CREATE (n:Test {name: 'TestNode'}) RETURN n;
```

### Important Directories

- **Home**: /var/lib/neo4j
- **Configuration**: /etc/neo4j
- **Logs**: /var/log/neo4j
- **Plugins**: /var/lib/neo4j/plugins
- **Import**: /var/lib/neo4j/import
- **Data**: /var/lib/neo4j/data

### Configuration Files

The main configuration file is located at `/etc/neo4j/neo4j.conf`. Key settings:

- Memory heap size configuration
- Network connector settings
- Database settings
- Security configurations

### Troubleshooting

1. **Check if Neo4j is running**:
   ```bash
   sudo service neo4j status
   curl -I http://localhost:7474
   ```

2. **View logs for errors**:
   ```bash
   tail -f /var/log/neo4j/neo4j.log
   ```

3. **Test database connection**:
   ```bash
   echo "RETURN 1;" | cypher-shell -u neo4j -p neo4j123
   ```

### Security Notes

- The default password has been set to `neo4j123` for development purposes
- For production environments, use a stronger password
- Consider enabling SSL/TLS for production deployments
- Review and configure authentication/authorization settings as needed

### Next Steps for Development

1. **Install Neo4j drivers** for your preferred programming language:
   - Python: `pip install neo4j`
   - Node.js: `npm install neo4j-driver`
   - Java: Add Neo4j Java driver to your dependencies

2. **Create your graph schema** based on Brazil data requirements

3. **Import initial data** using CSV imports or programmatic creation

4. **Set up indexes and constraints** for optimal query performance

### Useful Cypher Queries for Development

```cypher
-- Check database status
:sysinfo

-- Show all node labels
MATCH (n) RETURN DISTINCT labels(n);

-- Show all relationship types
MATCH ()-[r]->() RETURN DISTINCT type(r);

-- Count nodes by label
MATCH (n) RETURN labels(n) as label, count(*) as count;

-- Clear all data (use with caution)
MATCH (n) DETACH DELETE n;
```

## Database is Ready for Development

The Neo4j database is now running with an empty brazil-kg database, ready for your knowledge graph development. You can access the Neo4j Browser at http://localhost:7474 using the credentials provided above.

> update .gitignore

● Updated .gitignore with additional exclusions for:
  - Neo4j database files
  - Security credentials and certificates
  - Large data files (CSV, JSON, XML)
  - Machine learning models
  - Documentation builds
  - Various cache and session files
  - Local configuration files