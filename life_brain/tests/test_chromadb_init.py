"""
Unit tests for chromadb_init.py

Covers:
- ChromaDBManager initialization
- Collection initialization
- Metadata validation delegation
- Text self-contained validation
- Single field validation
- Schema info retrieval
- get_metadata_schema function
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from life_brain.db.chromadb_init import ChromaDBManager, get_metadata_schema
from life_brain.db.metadata_validator import MetadataValidationError


class TestChromaDBManagerInit:
    """Test ChromaDBManager initialization."""

    def test_init_default_path(self):
        """Test initialization with default path."""
        manager = ChromaDBManager()
        assert manager.client is None
        assert manager.collection is None
        assert manager.validator is not None

    def test_init_custom_path(self):
        """Test initialization with custom path."""
        manager = ChromaDBManager(path="/custom/path")
        assert manager.path == "/custom/path"

    def test_init_validator_created(self):
        """Test that validator is initialized."""
        manager = ChromaDBManager()
        assert manager.validator is not None


class TestInitCollection:
    """Test collection initialization."""

    @patch('life_brain.db.chromadb_init.chromadb.PersistentClient')
    def test_init_collection_success(self, mock_persistent):
        """Test successful collection initialization."""
        mock_client = Mock()
        mock_persistent.return_value = mock_client
        mock_collection = Mock()
        mock_client.get_or_create_collection.return_value = mock_collection

        manager = ChromaDBManager()
        result = manager.init_collection()

        assert result == mock_collection
        assert manager.client == mock_client
        assert manager.collection == mock_collection

    @patch('life_brain.db.chromadb_init.chromadb.PersistentClient')
    def test_init_collection_with_hnsw_space(self, mock_persistent):
        """Test collection initialized with HNSW space."""
        mock_client = Mock()
        mock_persistent.return_value = mock_client
        mock_client.get_or_create_collection.return_value = Mock()

        manager = ChromaDBManager()
        manager.init_collection()

        # Verify hnsw:space was set
        call_kwargs = mock_client.get_or_create_collection.call_args[1]
        assert "metadata" in call_kwargs
        assert "hnsw:space" in call_kwargs["metadata"]

    @patch('life_brain.db.chromadb_init.chromadb.PersistentClient')
    def test_init_collection_failure(self, mock_persistent):
        """Test collection initialization failure."""
        mock_persistent.side_effect = Exception("Connection failed")

        manager = ChromaDBManager()
        with pytest.raises(RuntimeError) as exc:
            manager.init_collection()

        assert "Failed to initialize" in str(exc.value)


class TestValidateRequiredFields:
    """Test metadata validation delegation."""

    @patch('life_brain.db.chromadb_init.MetadataValidator')
    def test_validate_valid_metadata(self, mock_validator_class):
        """Test validation of valid metadata."""
        mock_validator = Mock()
        mock_validator_class.return_value = mock_validator
        mock_validator.validate_metadata.return_value = None

        manager = ChromaDBManager()
        result = manager.validate_required_fields({"domain": "career"})

        assert result is True
        mock_validator.validate_metadata.assert_called_once()

    @patch('life_brain.db.chromadb_init.MetadataValidator')
    def test_validate_invalid_metadata(self, mock_validator_class):
        """Test validation of invalid metadata."""
        mock_validator = Mock()
        mock_validator_class.return_value = mock_validator
        mock_validator.validate_metadata.side_effect = MetadataValidationError("Missing field")

        manager = ChromaDBManager()
        with pytest.raises(ValueError):
            manager.validate_required_fields({})


class TestValidateTextSelfContained:
    """Test text self-contained validation."""

    def test_valid_text(self):
        """Test valid self-contained text."""
        manager = ChromaDBManager()
        text = "This is a comprehensive document with sufficient length for validation purposes and contains multiple sentences to demonstrate self-containedness."
        result = manager.validate_text_self_contained(text)
        assert result is True

    def test_text_too_short(self):
        """Test text that is too short."""
        manager = ChromaDBManager()
        with pytest.raises(ValueError) as exc:
            manager.validate_text_self_contained("Short")
        assert "100" in str(exc.value)

    def test_text_empty(self):
        """Test empty text."""
        manager = ChromaDBManager()
        with pytest.raises(ValueError):
            manager.validate_text_self_contained("")

    def test_text_none(self):
        """Test None text."""
        manager = ChromaDBManager()
        with pytest.raises((ValueError, TypeError)):
            manager.validate_text_self_contained(None)

    def test_text_qa_format_valid(self):
        """Test valid Q&A format text."""
        manager = ChromaDBManager()
        text = "Q: What is machine learning and how does it relate to artificial intelligence? I want to understand the fundamental concepts and differences between these two fields.\nA: Machine learning is a subset of artificial intelligence that enables systems to learn from data and improve performance without being explicitly programmed."
        result = manager.validate_text_self_contained(text)
        assert result is True

    def test_text_qa_format_insufficient_question(self):
        """Test Q&A format with insufficient question."""
        manager = ChromaDBManager()
        text = "Q: ML?\nA: This is a very detailed answer about machine learning and how it works in systems."
        with pytest.raises(ValueError):
            manager.validate_text_self_contained(text)


class TestValidateField:
    """Test single field validation."""

    @patch('life_brain.db.chromadb_init.MetadataValidator')
    def test_validate_field_valid(self, mock_validator_class):
        """Test validating valid field."""
        mock_validator = Mock()
        mock_validator_class.return_value = mock_validator
        mock_validator.validate_field.return_value = (True, "")

        manager = ChromaDBManager()
        result = manager.validate_field("domain", "career")

        assert result is True

    @patch('life_brain.db.chromadb_init.MetadataValidator')
    def test_validate_field_invalid(self, mock_validator_class):
        """Test validating invalid field."""
        mock_validator = Mock()
        mock_validator_class.return_value = mock_validator
        mock_validator.validate_field.return_value = (False, "Invalid value")

        manager = ChromaDBManager()
        with pytest.raises(ValueError):
            manager.validate_field("domain", "invalid")


class TestGetSchemaInfo:
    """Test schema information retrieval."""

    @patch('life_brain.db.chromadb_init.MetadataValidator')
    def test_get_schema_info(self, mock_validator_class):
        """Test getting schema information."""
        mock_validator = Mock()
        mock_validator_class.return_value = mock_validator
        mock_validator.get_schema_info.return_value = {"fields": 47}

        manager = ChromaDBManager()
        result = manager.get_schema_info()

        assert result == {"fields": 47}


class TestGetMetadataSchema:
    """Test get_metadata_schema function."""

    def test_get_metadata_schema(self):
        """Test retrieving metadata schema."""
        schema = get_metadata_schema()

        assert schema is not None
        assert isinstance(schema, dict)
        assert "tier_1" in schema
        assert "tier_2" in schema
        assert "required" in schema

    def test_schema_has_required_fields(self):
        """Test schema contains required fields."""
        schema = get_metadata_schema()
        assert len(schema["required"]) > 0

    def test_schema_tier_fields_exist(self):
        """Test schema contains tier fields."""
        schema = get_metadata_schema()
        assert len(schema["tier_1"]) > 0
        assert len(schema["tier_2"]) > 0


class TestIntegrationChromaDB:
    """Integration tests."""

    @patch('life_brain.db.chromadb_init.chromadb.PersistentClient')
    @patch('life_brain.db.chromadb_init.MetadataValidator')
    def test_full_workflow_init_validate(self, mock_validator_class, mock_persistent):
        """Test full workflow: init and validate."""
        mock_validator = Mock()
        mock_validator_class.return_value = mock_validator
        mock_validator.validate_metadata.return_value = None

        mock_client = Mock()
        mock_persistent.return_value = mock_client
        mock_client.get_or_create_collection.return_value = Mock()

        manager = ChromaDBManager()
        manager.init_collection()
        manager.validate_required_fields({"domain": "career"})

        assert manager.collection is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
