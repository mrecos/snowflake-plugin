"""Tests for SQL query validators."""
import pytest
from daemon.validators import (
    ReadOnlyValidator,
    DMLValidator,
    DDLValidator,
    WriteValidator,
    TransactionValidator
)


class TestReadOnlyValidator:
    """Tests for ReadOnlyValidator."""

    def test_allows_select(self):
        validator = ReadOnlyValidator()
        is_valid, error = validator.validate("SELECT * FROM table")
        assert is_valid is True
        assert error is None

    def test_allows_select_lowercase(self):
        validator = ReadOnlyValidator()
        is_valid, error = validator.validate("select * from table")
        assert is_valid is True
        assert error is None

    def test_allows_with_cte(self):
        validator = ReadOnlyValidator()
        is_valid, error = validator.validate("WITH cte AS (SELECT 1) SELECT * FROM cte")
        assert is_valid is True
        assert error is None

    def test_allows_show(self):
        validator = ReadOnlyValidator()
        is_valid, error = validator.validate("SHOW TABLES")
        assert is_valid is True
        assert error is None

    def test_allows_describe(self):
        validator = ReadOnlyValidator()
        is_valid, error = validator.validate("DESCRIBE TABLE my_table")
        assert is_valid is True
        assert error is None

    def test_allows_desc(self):
        validator = ReadOnlyValidator()
        is_valid, error = validator.validate("DESC TABLE my_table")
        assert is_valid is True
        assert error is None

    def test_allows_use_database(self):
        validator = ReadOnlyValidator()
        is_valid, error = validator.validate("USE DATABASE my_db")
        assert is_valid is True
        assert error is None

    def test_allows_use_schema(self):
        validator = ReadOnlyValidator()
        is_valid, error = validator.validate("USE SCHEMA my_schema")
        assert is_valid is True
        assert error is None

    def test_allows_list(self):
        validator = ReadOnlyValidator()
        is_valid, error = validator.validate("LIST @my_stage")
        assert is_valid is True
        assert error is None

    def test_rejects_insert(self):
        validator = ReadOnlyValidator()
        is_valid, error = validator.validate("INSERT INTO table VALUES (1)")
        assert is_valid is False
        assert "INSERT" in error
        assert "not permitted" in error

    def test_rejects_update(self):
        validator = ReadOnlyValidator()
        is_valid, error = validator.validate("UPDATE table SET col=1")
        assert is_valid is False
        assert "UPDATE" in error

    def test_rejects_delete(self):
        validator = ReadOnlyValidator()
        is_valid, error = validator.validate("DELETE FROM table")
        assert is_valid is False
        assert "DELETE" in error

    def test_rejects_create(self):
        validator = ReadOnlyValidator()
        is_valid, error = validator.validate("CREATE TABLE my_table (id INT)")
        assert is_valid is False
        assert "CREATE" in error

    def test_rejects_drop(self):
        validator = ReadOnlyValidator()
        is_valid, error = validator.validate("DROP TABLE my_table")
        assert is_valid is False
        assert "DROP" in error

    def test_rejects_empty_query(self):
        validator = ReadOnlyValidator()
        is_valid, error = validator.validate("")
        assert is_valid is False
        assert "Empty query" in error

    def test_rejects_whitespace_only(self):
        validator = ReadOnlyValidator()
        is_valid, error = validator.validate("   ")
        assert is_valid is False
        assert "Empty query" in error


class TestDMLValidator:
    """Tests for DMLValidator."""

    def test_allows_select(self):
        validator = DMLValidator()
        is_valid, error = validator.validate("SELECT * FROM table")
        assert is_valid is True
        assert error is None

    def test_allows_insert(self):
        validator = DMLValidator()
        is_valid, error = validator.validate("INSERT INTO table VALUES (1)")
        assert is_valid is True
        assert error is None

    def test_allows_update(self):
        validator = DMLValidator()
        is_valid, error = validator.validate("UPDATE table SET col=1")
        assert is_valid is True
        assert error is None

    def test_allows_delete(self):
        validator = DMLValidator()
        is_valid, error = validator.validate("DELETE FROM table WHERE id=1")
        assert is_valid is True
        assert error is None

    def test_allows_merge(self):
        validator = DMLValidator()
        is_valid, error = validator.validate("MERGE INTO target USING source ON target.id = source.id")
        assert is_valid is True
        assert error is None

    def test_allows_copy_into(self):
        validator = DMLValidator()
        is_valid, error = validator.validate("COPY INTO table FROM @stage")
        assert is_valid is True
        assert error is None

    def test_rejects_create(self):
        validator = DMLValidator()
        is_valid, error = validator.validate("CREATE TABLE my_table (id INT)")
        assert is_valid is False
        assert "CREATE" in error

    def test_rejects_drop(self):
        validator = DMLValidator()
        is_valid, error = validator.validate("DROP TABLE my_table")
        assert is_valid is False
        assert "DROP" in error

    def test_rejects_alter(self):
        validator = DMLValidator()
        is_valid, error = validator.validate("ALTER TABLE my_table ADD COLUMN name VARCHAR")
        assert is_valid is False
        assert "ALTER" in error


class TestDDLValidator:
    """Tests for DDLValidator."""

    def test_allows_select(self):
        validator = DDLValidator()
        is_valid, error = validator.validate("SELECT * FROM table")
        assert is_valid is True
        assert error is None

    def test_allows_create(self):
        validator = DDLValidator()
        is_valid, error = validator.validate("CREATE TABLE my_table (id INT)")
        assert is_valid is True
        assert error is None

    def test_allows_drop(self):
        validator = DDLValidator()
        is_valid, error = validator.validate("DROP TABLE my_table")
        assert is_valid is True
        assert error is None

    def test_allows_alter(self):
        validator = DDLValidator()
        is_valid, error = validator.validate("ALTER TABLE my_table ADD COLUMN name VARCHAR")
        assert is_valid is True
        assert error is None

    def test_allows_truncate(self):
        validator = DDLValidator()
        is_valid, error = validator.validate("TRUNCATE TABLE my_table")
        assert is_valid is True
        assert error is None

    def test_allows_rename(self):
        validator = DDLValidator()
        is_valid, error = validator.validate("RENAME TABLE old_name TO new_name")
        assert is_valid is True
        assert error is None

    def test_rejects_insert(self):
        validator = DDLValidator()
        is_valid, error = validator.validate("INSERT INTO table VALUES (1)")
        assert is_valid is False
        assert "INSERT" in error

    def test_rejects_update(self):
        validator = DDLValidator()
        is_valid, error = validator.validate("UPDATE table SET col=1")
        assert is_valid is False
        assert "UPDATE" in error

    def test_rejects_delete(self):
        validator = DDLValidator()
        is_valid, error = validator.validate("DELETE FROM table")
        assert is_valid is False
        assert "DELETE" in error


class TestWriteValidator:
    """Tests for WriteValidator (allows all operations)."""

    def test_allows_select(self):
        validator = WriteValidator()
        is_valid, error = validator.validate("SELECT * FROM table")
        assert is_valid is True
        assert error is None

    def test_allows_insert(self):
        validator = WriteValidator()
        is_valid, error = validator.validate("INSERT INTO table VALUES (1)")
        assert is_valid is True
        assert error is None

    def test_allows_update(self):
        validator = WriteValidator()
        is_valid, error = validator.validate("UPDATE table SET col=1")
        assert is_valid is True
        assert error is None

    def test_allows_delete(self):
        validator = WriteValidator()
        is_valid, error = validator.validate("DELETE FROM table WHERE id=1")
        assert is_valid is True
        assert error is None

    def test_allows_create(self):
        validator = WriteValidator()
        is_valid, error = validator.validate("CREATE TABLE my_table (id INT)")
        assert is_valid is True
        assert error is None

    def test_allows_drop(self):
        validator = WriteValidator()
        is_valid, error = validator.validate("DROP TABLE my_table")
        assert is_valid is True
        assert error is None

    def test_allows_alter(self):
        validator = WriteValidator()
        is_valid, error = validator.validate("ALTER TABLE my_table ADD COLUMN name VARCHAR")
        assert is_valid is True
        assert error is None

    def test_allows_truncate(self):
        validator = WriteValidator()
        is_valid, error = validator.validate("TRUNCATE TABLE my_table")
        assert is_valid is True
        assert error is None

    def test_allows_begin(self):
        validator = WriteValidator()
        is_valid, error = validator.validate("BEGIN")
        assert is_valid is True
        assert error is None

    def test_allows_commit(self):
        validator = WriteValidator()
        is_valid, error = validator.validate("COMMIT")
        assert is_valid is True
        assert error is None

    def test_allows_rollback(self):
        validator = WriteValidator()
        is_valid, error = validator.validate("ROLLBACK")
        assert is_valid is True
        assert error is None

    def test_allows_grant(self):
        validator = WriteValidator()
        is_valid, error = validator.validate("GRANT SELECT ON table TO role")
        assert is_valid is True
        assert error is None

    def test_allows_call(self):
        validator = WriteValidator()
        is_valid, error = validator.validate("CALL my_procedure()")
        assert is_valid is True
        assert error is None

    def test_rejects_unknown_command(self):
        validator = WriteValidator()
        is_valid, error = validator.validate("FOOBAR something")
        assert is_valid is False
        assert "FOOBAR" in error
        assert "not recognized" in error

    def test_rejects_empty_query(self):
        validator = WriteValidator()
        is_valid, error = validator.validate("")
        assert is_valid is False
        assert "Empty query" in error


class TestTransactionValidator:
    """Tests for TransactionValidator."""

    def test_allows_begin(self):
        validator = TransactionValidator()
        is_valid, error = validator.validate("BEGIN")
        assert is_valid is True
        assert error is None

    def test_allows_commit(self):
        validator = TransactionValidator()
        is_valid, error = validator.validate("COMMIT")
        assert is_valid is True
        assert error is None

    def test_allows_rollback(self):
        validator = TransactionValidator()
        is_valid, error = validator.validate("ROLLBACK")
        assert is_valid is True
        assert error is None

    def test_allows_start_transaction(self):
        validator = TransactionValidator()
        is_valid, error = validator.validate("START TRANSACTION")
        assert is_valid is True
        assert error is None

    def test_rejects_select(self):
        validator = TransactionValidator()
        is_valid, error = validator.validate("SELECT * FROM table")
        assert is_valid is False
        assert "SELECT" in error

    def test_rejects_insert(self):
        validator = TransactionValidator()
        is_valid, error = validator.validate("INSERT INTO table VALUES (1)")
        assert is_valid is False
        assert "INSERT" in error
