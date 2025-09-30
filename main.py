"""
Brazilian Soccer MCP Knowledge Graph - Main Entry Point

CONTEXT:
Main entry point for the Brazilian Soccer MCP Knowledge Graph application.
This script provides a command-line interface for building and managing
the graph database, loading data, and performing basic operations.

PHASE: 1 (Core Data)
COMPONENT: Application Entry Point
DEPENDENCIES: click, logging, src package

ARCHITECTURE:
The main script provides several command-line operations:

COMMANDS:
- build: Build the complete graph from scratch
- load-data: Load data from specific sources
- stats: Show graph statistics
- validate: Validate graph integrity
- clear: Clear the database (with confirmation)
- test-connection: Test database connectivity

CONFIGURATION:
- Uses environment variables for database connection
- Supports different environments (dev, test, prod)
- Configurable logging levels
- Batch size optimization

USAGE:
```bash
python main.py build --clear-first
python main.py stats
python main.py validate
python main.py load-data --source kaggle
```

This provides a user-friendly interface for managing the Brazilian Soccer
Knowledge Graph without requiring detailed knowledge of the internal APIs.
"""

import click
import logging
import json
import os
from pathlib import Path
from datetime import datetime
from typing import Optional

from src import (
    Neo4jConnection, GraphBuilder, KaggleLoader, GraphSchema
)


# Configure logging
def setup_logging(level: str = "INFO"):
    """Setup logging configuration."""
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('logs/brazilian_soccer_mcp.log')
        ]
    )


# Load configuration
def load_config(env: str = "development") -> dict:
    """Load configuration from config file."""
    config_path = Path("config/database.json")
    if config_path.exists():
        with open(config_path) as f:
            config = json.load(f)
            return config.get(env, config.get("development", {}))

    # Default configuration
    return {
        "neo4j": {
            "uri": os.getenv("NEO4J_URI", "bolt://localhost:7687"),
            "username": os.getenv("NEO4J_USERNAME", "neo4j"),
            "password": os.getenv("NEO4J_PASSWORD", "neo4j123"),
            "database": os.getenv("NEO4J_DATABASE")
        },
        "batch_size": int(os.getenv("BATCH_SIZE", "1000")),
        "logging": {"level": "INFO"}
    }


@click.group()
@click.option('--env', default='development', help='Environment (development, testing, production)')
@click.option('--log-level', default='INFO', help='Logging level')
@click.pass_context
def cli(ctx, env, log_level):
    """Brazilian Soccer MCP Knowledge Graph Management CLI."""
    # Ensure logs directory exists
    Path("logs").mkdir(exist_ok=True)

    # Setup logging
    setup_logging(log_level)

    # Load configuration
    config = load_config(env)

    # Create database connection
    neo4j_config = config["neo4j"]
    db_connection = Neo4jConnection(
        uri=neo4j_config["uri"],
        username=neo4j_config["username"],
        password=neo4j_config["password"]
    )

    # Store in context for subcommands
    ctx.ensure_object(dict)
    ctx.obj['db'] = db_connection
    ctx.obj['config'] = config
    ctx.obj['env'] = env


@cli.command()
@click.option('--clear-first', is_flag=True, help='Clear database before building')
@click.option('--validate', is_flag=True, default=True, help='Validate graph after building')
@click.pass_context
def build(ctx, clear_first, validate):
    """Build the complete graph database from scratch."""
    db = ctx.obj['db']
    config = ctx.obj['config']

    logger = logging.getLogger(__name__)
    logger.info("Starting graph build process...")

    try:
        # Test connection first
        if not db.test_connection():
            click.echo("❌ Database connection failed. Please check your Neo4j configuration.")
            return

        click.echo("✅ Database connection successful")

        # Clear database if requested
        if clear_first:
            if click.confirm("This will delete all data in the database. Continue?"):
                builder = GraphBuilder(db)
                builder.clear_database()
                click.echo("🗑️ Database cleared")
            else:
                click.echo("❌ Build cancelled")
                return

        # Build the graph
        click.echo("🔨 Building graph...")
        builder = GraphBuilder(db)

        # Set batch size from config
        builder.batch_size = config.get("batch_size", 1000)

        with click.progressbar(length=100, label="Building graph") as bar:
            # This is a simplified progress bar
            # In a real implementation, you'd update progress during build
            stats = builder.build_complete_graph()
            bar.update(100)

        # Display results
        if stats.get("success", False):
            click.echo("✅ Graph build completed successfully!")
            click.echo(f"📊 Created {stats['nodes_created']} nodes and {stats['relationships_created']} relationships")
            click.echo(f"⏱️ Build time: {stats['duration_seconds']:.2f} seconds")

            if stats.get("errors"):
                click.echo(f"⚠️ {len(stats['errors'])} warnings/errors:")
                for error in stats["errors"][:5]:  # Show first 5 errors
                    click.echo(f"   • {error}")
        else:
            click.echo("❌ Graph build failed!")
            if stats.get("error"):
                click.echo(f"Error: {stats['error']}")

        # Validate if requested
        if validate and stats.get("success"):
            click.echo("\n🔍 Validating graph integrity...")
            validation = builder.validate_graph_integrity()

            if validation.get("success"):
                click.echo("✅ Graph validation passed")
            else:
                click.echo("⚠️ Graph validation found issues:")
                for error in validation.get("errors", []):
                    click.echo(f"   • {error}")

    except Exception as e:
        logger.error(f"Build failed: {e}")
        click.echo(f"❌ Build failed: {e}")


@cli.command()
@click.pass_context
def stats(ctx):
    """Show graph database statistics."""
    db = ctx.obj['db']

    try:
        if not db.test_connection():
            click.echo("❌ Database connection failed")
            return

        builder = GraphBuilder(db)
        stats = builder.get_graph_statistics()

        if "error" in stats:
            click.echo(f"❌ Failed to get statistics: {stats['error']}")
            return

        click.echo("📊 Graph Database Statistics")
        click.echo("=" * 40)

        # Node counts
        click.echo("\n🏷️ Nodes:")
        for label, count in stats.get("nodes", {}).items():
            click.echo(f"   {label.capitalize()}: {count:,}")

        # Relationship counts
        click.echo("\n🔗 Relationships:")
        for rel_type, count in stats.get("relationships", {}).items():
            click.echo(f"   {rel_type.replace('_', ' ').title()}: {count:,}")

        click.echo(f"\n📈 Total Nodes: {stats.get('total_nodes', 0):,}")
        click.echo(f"📈 Total Relationships: {stats.get('total_relationships', 0):,}")

    except Exception as e:
        click.echo(f"❌ Failed to get statistics: {e}")


@cli.command()
@click.pass_context
def validate(ctx):
    """Validate graph integrity and data quality."""
    db = ctx.obj['db']

    try:
        if not db.test_connection():
            click.echo("❌ Database connection failed")
            return

        builder = GraphBuilder(db)
        validation = builder.validate_graph_integrity()

        click.echo("🔍 Graph Validation Results")
        click.echo("=" * 40)

        # Show successful checks
        if validation.get("checks"):
            click.echo("\n✅ Passed Checks:")
            for check in validation["checks"]:
                click.echo(f"   • {check}")

        # Show warnings
        if validation.get("warnings"):
            click.echo("\n⚠️ Warnings:")
            for warning in validation["warnings"]:
                click.echo(f"   • {warning}")

        # Show errors
        if validation.get("errors"):
            click.echo("\n❌ Errors:")
            for error in validation["errors"]:
                click.echo(f"   • {error}")

        # Overall result
        if validation.get("success"):
            click.echo("\n✅ Overall: Graph validation passed")
        else:
            click.echo("\n❌ Overall: Graph validation failed")

    except Exception as e:
        click.echo(f"❌ Validation failed: {e}")


@cli.command()
@click.option('--source', default='sample', help='Data source (sample, kaggle)')
@click.pass_context
def load_data(ctx, source):
    """Load data from specified source."""
    db = ctx.obj['db']

    try:
        if not db.test_connection():
            click.echo("❌ Database connection failed")
            return

        loader = KaggleLoader()

        if source == 'sample':
            click.echo("📥 Loading sample data...")
            data = loader.load_brazilian_championship_data()
        else:
            click.echo(f"❌ Unknown data source: {source}")
            return

        # Show data summary
        click.echo("📊 Data Summary:")
        for entity_type, entities in data.items():
            click.echo(f"   {entity_type.capitalize()}: {len(entities)}")

        # Validate data
        validation = loader.validate_data(data)
        if validation.get("issues"):
            click.echo(f"\n⚠️ Data validation found {len(validation['issues'])} issues")
        else:
            click.echo("\n✅ Data validation passed")

    except Exception as e:
        click.echo(f"❌ Data loading failed: {e}")


@cli.command()
@click.confirmation_option(prompt='Are you sure you want to clear all data?')
@click.pass_context
def clear(ctx):
    """Clear all data from the database."""
    db = ctx.obj['db']

    try:
        if not db.test_connection():
            click.echo("❌ Database connection failed")
            return

        builder = GraphBuilder(db)
        builder.clear_database()
        click.echo("✅ Database cleared successfully")

    except Exception as e:
        click.echo(f"❌ Failed to clear database: {e}")


@cli.command()
@click.pass_context
def test_connection(ctx):
    """Test database connection."""
    db = ctx.obj['db']
    config = ctx.obj['config']

    click.echo("🔌 Testing database connection...")
    click.echo(f"URI: {config['neo4j']['uri']}")
    click.echo(f"Username: {config['neo4j']['username']}")

    try:
        if db.test_connection():
            click.echo("✅ Connection successful!")

            # Get database info if possible
            info = db.get_database_info()
            if info and not info.get("error"):
                click.echo("\n📊 Database Info:")
                for label, count in info.get("node_counts", {}).items():
                    click.echo(f"   {label}: {count}")
        else:
            click.echo("❌ Connection failed!")

    except Exception as e:
        click.echo(f"❌ Connection test failed: {e}")


@cli.command()
@click.pass_context
def schema(ctx):
    """Manage database schema."""
    db = ctx.obj['db']

    try:
        if not db.test_connection():
            click.echo("❌ Database connection failed")
            return

        schema = GraphSchema(db)

        click.echo("🏗️ Creating database schema...")
        schema.create_schema()
        click.echo("✅ Schema created successfully")

        # Show schema info
        info = schema.get_schema_info()
        if "error" not in info:
            click.echo(f"\n📋 Constraints: {len(info.get('constraints', []))}")
            click.echo(f"📋 Indexes: {len(info.get('indexes', []))}")

    except Exception as e:
        click.echo(f"❌ Schema operation failed: {e}")


if __name__ == '__main__':
    cli()