-- Создание таблицы users (она создастся через SQLAlchemy, но можно добавить расширения)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Можно добавить дополнительные настройки базы
ALTER DATABASE cattell_db SET TIMEZONE TO 'UTC';
