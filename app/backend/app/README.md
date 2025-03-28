# Backend API Documentation

## Table of Contents

- [Overview](#overview)
- [Setup and Environment Configuration](#setup-and-environment-configuration)
  - [Development Environment Setup](#development-environment-setup)
  - [Environment Variables Configuration](#environment-variables-configuration)
- [FastAPI + SQLAlchemy Architecture](#fastapi-sqlalchemy-architecture)
  - [Database Session Management with Dependency Injection](#database-session-management-with-dependency-injection)
  - [Async vs. Sync Routes](#async-vs-sync-routes)
- [Database Models](#database-models)
- [API Endpoint Documentation](#api-endpoint-documentation)
- [Postman Testing](#postman-testing)
- [Summary](#summary)

## Overview <a id="overview"></a>

The backend system is a **RESTful API** built with **FastAPI** (a high-performance Python web framework) and SQLAlchemy (an Object-Relational Mapper for database access). It provides a set of endpoints that allow other applications (like a frontend or mobile app) to perform operations such as user authentication, booking creation and management, and retrieving various records. In simple terms, this system handles the server-side logic for the project — receiving requests, interacting with the database, and returning responses — all while enforcing business rules and data validation. FastAPI was chosen for its ease of use and automatic interactive documentation features, which help both developers and stakeholders understand the API. SQLAlchemy is used so that developers can work with the database in Python objects (models) instead of writing raw SQL queries, improving code maintainability. This combination of FastAPI and SQLAlchemy also boosts developer productivity with built-in features like data validation and an interactive API browser[^1].

> [!NOTE]
> This overview is written to be accessible to non-technical team members. It omits low-level implementation details while highlighting what the system does and why these technologies were used.

## Setup and Environment Configuration <a id="setup-and-environment-configuration"></a>

Setting up the development environment for this project involves installing dependencies, configuring environment variables (like the database connection), and running the FastAPI server locally. Below are the general steps to get started:

### Development Environment Setup <a id="development-environment-setup"></a>

- **Prerequisites**: Ensure you have met the [prerequisites](../../../README.md#prerequisites) in the [Getting Started](../../../README.md#getting-started) section. It’s recommended to use a **virtual environment** for development (for example, using `python -m venv env` and then activating it) to isolate project dependencies. This prevents conflicts with other projects on your machine. Refer to the [Create a Virtual Environment](../../../README.md#create-a-virtual-environment) section for more details.

- **Install Dependencies**: Refer to the [Install Dependencies](../../../README.md#install-dependencies) section for instructions on how to install the project dependencies. Following the steps will download and install FastAPI, SQLAlchemy, and other libraries the project needs. It’s important to do this inside your virtual environment so that the packages are scoped to this project.

- **Starting the FastAPI Server**: Refer to the [Running Locally](../../../README.md#running-locally) section for instructions on how you can start the development server. The project uses **Uvicorn** (an ASGI server) to run FastAPI.

> [!NOTE]
> Ensure any required services (like a database server) are running and accessible before launching the API. For example, if using a local PostgreSQL database, start the database server; if using SQLite, this is not necessary since it’s file-based.

### Environment Variables Configuration <a id="environment-variables-configuration"></a>

The project uses environment variables to configure settings such as the database connection. Using environment variables (or a `.env` file) keeps sensitive or environment-specific information (like database URLs or secrets) out of the source code. For instance, there may be an environment variable like `DATABASE_URL` which contains the database connection string (e.g., for SQLite it could be `sqlite:///./app.db`, or for PostgreSQL something like `postgresql://user:password@localhost:5432/mydb`).

You will find a [`.env.sample`](.env.sample). It should look like this:

```yaml
secret_key=
algorithm=
access_token_expire_minutes=
refresh_token_expire_days=
```

Create an `.env` file and copy and paste the contents from above into it. Before running the application, make sure to **set the required environment variables**.

> [!NOTE]
> We are using SQLite for this project which is a file-based database. Please make sure you follow the steps in the [Retrieving Data](../../../docs/DATA_MANAGEMENT.md#retrieving-data) section of the [Data Management](../../../docs/DATA_MANAGEMENT.md) guide to ensure the database has been sucessfully retrieved from remote storege and up-to-date before proceeding with this guide.

## FastAPI + SQLAlchemy Architecture <a id="fastapi-sqlalchemy-architecture"></a>

This section describes how the FastAPI framework and the SQLAlchemy ORM work together in our project’s code. The goal is to outline the **architecture of the backend** — essentially, how requests are processed and how database operations are handled — in a way that’s understandable to both developers and interested non-developers.

FastAPI follows a **model-view-controller-like** pattern where **path operation functions** (the functions behind each API endpoint) act as the “controller” logic. When a request comes in to a certain URL, FastAPI routes it to the corresponding function. Inside these functions, we often need to interact with the database. That’s where SQLAlchemy comes in: the project defines **database models** (Python classes corresponding to database tables) and uses a database session to query or save data.

A key part of this architecture is FastAPI’s **dependency injection system**. This allows us to easily provide a database session to any endpoint that needs it, without manually creating or passing sessions around in every function.

### Database Session Management with Dependency Injection <a id="database-session-management-with-dependency-injection"></a>

To integrate SQLAlchemy with FastAPI, our project uses a **session generator dependency** to handle database sessions. In practice, we set up a global `SessionLocal` (created via `sessionmaker`) and a function dependency (often named `get_db`) that yields database session objects. Each API request that needs database access will “depend” on `get_db`, thus automatically receiving a session and ensuring it’s closed afterward. This approach ensures that each request uses an isolated database session and that connections are properly cleaned up, preventing resource leaks.

In code, it looks roughly like this:

```python
# Somewhere in database.py or similar module:

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

# Engine is created using the DATABASE_URL (from environment variable)
engine = create_engine(DATABASE_URL, connect_args={...})  # connect_args may include options, e.g., for SQLite

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency function
def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

When a FastAPI endpoint function includes a parameter like `db: Session = Depends(get_db)`, FastAPI will call this `get_db` function to get a database session and pass it into the function, then ensure the session is closed when the request is complete. This pattern is recommended by FastAPI for database integration and is used in our project. By using dependency injection, we can also easily swap out or override the database connection (for example, using a different `DATABASE_URL` for testing) without changing the core logic[^2].

**Why this matters**: For developers, this means less boilerplate — you don’t have to manually open or close connections for each request. For non-technical stakeholders, the takeaway is that the system is designed to be robust and maintainable: it cleanly separates database access logic and ensures consistency across all API calls.

### Async vs. Sync Routes <a id="async-vs-sync-routes"></a>

FastAPI supports defining endpoints as either synchronous (a normal `def` function) or asynchronous (`async def` function). In this project, we have to consider the database access pattern when choosing one or the other:

- **Synchronous routes**: If an endpoint is defined with a normal function (no `async` keyword), FastAPI will run that function in a threadpool. This means even if the function performs blocking operations (like traditional SQLAlchemy database calls, which are synchronous), it [won’t block the main server event loop](https://stackoverflow.com/questions/79382645/fastapi-why-does-synchronous-code-do-not-block-the-event-loop). FastAPI offloads such routes to a separate thread to avoid blocking other requests. Using the standard SQLAlchemy ORM (which is synchronous), typically defines routes as regular `def` functions. This way, when a database query is made, it runs in a separate thread, allowing the server to handle other requests in the meantime.

- **Asynchronous routes**: These are useful when the code inside the route uses awaitable calls (for example, if using an `async` database client or making external HTTP calls with `asyncio`). In our case, if we were to use an asynchronous database library or SQLAlchemy’s `async` ORM features, we could define `async def` endpoints. However, mixing `sync` database calls inside `async` functions can lead to blocking the event loop (which is not ideal). Therefore, unless the project is configured for fully async database operations, we stick to synchronous endpoints.

> [!NOTE]
> In this project, database operations are configured to be fully asynchronous.

In summary, the **current architecture uses asynchronous routes** and the more advanced setup of an asynchronous database driver and the `async` session of SQLAlchemy. This ensures that performance remains optimal and that the API can handle multiple requests concurrently without issues. (For the curious: switching to synchronous routes is feasible with FastAPI’s built-in threadpool handling, which is suitable given the synchronous nature of SQLAlchemy’s ORM.)

## Database Models <a id="database-models"></a>

In this project, **database models** are Python classes that represent tables in the database. We use SQLAlchemy’s **declarative system** to define these models. Each model class inherits from a base class (commonly named `Base`) that SQLAlchemy provides/uses to keep track of models. Attributes of the class correspond to columns in the database table.

For example, a simple model might look like:

```python
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Booking(Base):
    __tablename__ = "bookings"
    id = Column(Integer, primary_key=True, index=True)
    customer_name = Column(String, nullable=False)
    date = Column(String, nullable=False)
    notes = Column(String, nullable=True)
    # ... additional fields ...
```

Each attribute uses a `Column` type (`Integer`, `String`, etc.) to define the data type and constraints. In the example above, `Booking.id` is an integer primary key, and `customer_name`, date, and `notes` are columns for storing information about a booking. The `__tablename__` specifies the table name in the database. SQLAlchemy will use this model to read from and write to the `bookings` table.

In our project, we have several models corresponding to different concepts (for instance, `User`, `BookingSlot`, `Record`, etc.). All models inherit from the common `Base` (which is typically defined once when setting up SQLAlchemy). After defining models, typically the database tables can be created from them (for example, by calling `Base.metadata.create_all(engine)` during development or using migration tools). The structure of these model classes defines the structure of our database.

> [!NOTE]
> For the actual model definitions used in this project, refer to the [Database Models](../../../docs/DATABASE_MODELS.md) guide. For the full implementation of the database models used in this project, refer to the [models.py](./models/models.py) file.

## API Endpoint Documentation <a id="api-endpoint-documentation"></a>

Refer to the [API Endpoints](../../../docs/API_ENDPOINTS.md) guide for a detailed outline of the API endpoints provided by the backend, organized by feature/module.

## Postman Testing <a id="postman-testing"></a>

Refer to the [Postman Testing](../../../docs/POSTMAN_TESTING.md) guide for instructions on how to test the API endpoints using Postman.

## Summary <a id="summary"></a>

In this documentation, we covered an overview of the backend API, how to set up the project locally, the integration of FastAPI with SQLAlchemy (including handling database sessions and route types), definitions of the database models (schema), and a breakdown of all API endpoints by feature. We also explained how to use the interactive Swagger UI and provided a guide for testing endpoints with Postman, making it easier for the team to collaborate on testing and understanding the API.

This document should serve as a living reference for the development team and interested stakeholders to understand how the backend functions and how to interact with it. As development continues, keep this documentation up to date: when new endpoints are added or existing ones change, update the endpoint tables and descriptions in the [API Endpoints](../../../docs/API_ENDPOINTS.md) guide; when new models are introduced, add them to the [Database Models](../../../docs/DATABASE_MODELS.md) guide; and maintain the Postman collections alongside changes [here](../../../postman/).

<!-- **Next Steps**: With a solid understanding of the local setup and API usage, the next focus is typically on moving from development to production. We recommend proceeding to the Deployment and CI/CD Guide for this project (see the document “Managing Deployment and CI/CD for FastAPI Projects”). That guide will cover how to deploy the FastAPI application to a server or cloud platform, environment-specific configurations, and setting up continuous integration/continuous deployment pipelines for automated testing and deployment. It will ensure that the process of releasing new versions of this backend is as smooth and reliable as the development process. -->

Lastly, always feel free to refer to [FastAPI](https://fastapi.tiangolo.com/)’s and [SQLAlchemy](https://www.sqlalchemy.org/)’s official documentation for deeper insights. They are excellent resources for best practices and troubleshooting. With this documentation and the tools at hand, both developers and non-technical team members should be well-equipped to work with the backend API effectively.

[^1]: [How to Integrate FastAPI With SQLAlchemy](https://www.neurelo.com/post/how-to-integrate-fastapi-with-sqlalchemy#:~:text=,as%20SQLAlchemy%20increases%20developer%20productivity)
[^2]: [Dependency Injection : Connecting to Database](https://www.fastapitutorial.com/blog/dependencies-in-fastapi/#:~:text=our%20database%20settings%20and%20not,I%20think%20you%20should%20have)
