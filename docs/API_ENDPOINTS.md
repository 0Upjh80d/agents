# API Endpoints

## Table of Contents

- [Overview](#overview)
- [Authentication](#authentication)
- [Object-Relational Mapping (ORM)](#object-relational-mapping-orm)
  - [SQLAlchemy ORM with FastAPI](#sqlalchemy-orm-with-fastapi)
- [Chat](#chat)
- [User](#user)
- [Booking](#booking)
- [Stock](#stock)
- [Record](#record)

## Overview

Our FastAPI-based backend exposes a suite of RESTful API endpoints designed to handle business logic, data processing, and seamless integration with the database. These endpoints leverage [**SQLAlchemy**](https://www.sqlalchemy.org/), a powerful Object-Relational Mapping (ORM) framework, to perform secure, efficient, and maintainable database operations.

Key features of our API implementation include:

- **FastAPI Integration**: Provides a high-performance, easy-to-use framework for building scalable APIs.
- **SQLAlchemy ORM**: Simplifies database interactions, ensuring clean, readable code, and efficient data management.
- **Data Validation and Serialization**: Ensures incoming and outgoing data integrity with FastAPI's built-in Pydantic models.
- **Robust Error Handling**: Implements standardized error responses to simplify client-side development and debugging.

Refer to the sections below for detailed descriptions of each available endpoint, request/response formats, and example usage scenarios.

## Authentication <a id="authentication"></a>

TODO.

## Object-Relational Mapping (ORM) <a id="object-relational-mapping-orm"></a>

Object-Relational Mapping (ORM) is a technique for converting data between incompatible type systems using object-oriented programming languages. It abstracts database interactions by mapping database tables to objects within the application code.

### SQLAlchemy ORM with FastAPI <a id="sqlalchemy-orm-with-fastapi"></a>

SQLAlchemy is a popular Python ORM that provides a full suite of tools to interact seamlessly with databases. It simplifies complex database operations and improves security through parameterized queries.

In our FastAPI application, SQLAlchemy is used extensively to:

- Model database schemas and relationships clearly.
- Facilitate CRUD (Create, Read, Update, Delete) operations.
- Handle transaction management securely.
- Optimize queries for performance and readability.

FastAPI integrates effortlessly with SQLAlchemy, enabling asynchronous operations, dependency injections for database sessions, and easy integration with validation tools like Pydantic.

## User <a id="user"></a>

- `GET /users/{id}`: fetches user details by ID.
- `GET /users/records/{id}`: retrieves records associated with a specific user.
- `GET /users/recommend/{id}`: provides personalized recommendations for users

## Booking <a id="booking"></a>

- `GET /bookings/{id}`: fetches booking details.
- `GET /bookings/available/{vaccine_name}`: checks available booking slots for a specific vaccine.
- `POST /bookings/schedule`: schedules a new booking.
- `POST /bookings/cancel`: cancels a booking.

## Stock <a id="stock"></a>

- `GET /stock`: retrieves up-to-date vaccine stock information.

## Record <a id="record"></a>

- `GET /records/{id}`: retrieves medical or vaccination records using record ID.
