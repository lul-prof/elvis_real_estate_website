from flask.cli import FlaskGroup
from app import create_app, db
from app.models import User
import click

cli = FlaskGroup(create_app=create_app)

@cli.command("create-admin")
@click.argument("email")
@click.argument("username")
@click.argument("password")
def create_admin(email, username, password):
    """Create a new admin user"""
    try:
        user = User(
            email=email,
            username=username,
            role='admin'
        )
        user.set_password(password)  # Use the set_password method instead
        db.session.add(user)
        db.session.commit()
        click.echo(f"Admin user {username} created successfully!")
    except Exception as e:
        click.echo(f"Error creating admin user: {str(e)}")

@cli.command("create-agent")
@click.argument("email")
@click.argument("username")
@click.argument("password")
def create_agent(email, username, password):
    """Create a new agent user"""
    try:
        user = User(
            email=email,
            username=username,
            role='agent'
        )
        user.set_password(password)  # Use the set_password method instead
        db.session.add(user)
        db.session.commit()
        click.echo(f"Agent user {username} created successfully!")
    except Exception as e:
        click.echo(f"Error creating agent user: {str(e)}")

if __name__ == '__main__':
    cli()