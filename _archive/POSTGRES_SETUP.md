# PostgreSQL Setup Guide

Your project is now configured to use **PostgreSQL**.

## 1. Deployment (Render)
Everything is automated! 
- When you push to Render, it will automatically provision a PostgreSQL database.
- It will set the `DATABASE_URL` environment variable for you.
- Your app will detect this and use Postgres instead of SQLite.

## 2. Local Development (Optional)
By default, you can continue using **SQLite** locally to keep things simple. 
- If `DATABASE_URL` is not set in your local `.env` file, the app falls back to `sqlite:///health_reports.db`.
- **Recommended:** Keep using SQLite locally for now.

### If you WANT to use Postgres locally:
1.  **Install PostgreSQL**: Download from [postgresql.org](https://www.postgresql.org/download/).
2.  **Create a Database**:
    ```sql
    CREATE DATABASE inbloodo;
    ```
3.  **Update `.env`**:
    Add this line to your `.env` file:
    ```
    DATABASE_URL=postgresql://postgres:password@localhost/inbloodo
    ```
    *(Replace `postgres:password` with your local credentials)*

## 3. Migration Note
> [!IMPORTANT]
> Switching databases means your existing data in `health_reports.db` (SQLite) will **NOT** be in the new PostgreSQL database.
> The new database will start empty, and the app will automatically create the tables and default users on the first run.
