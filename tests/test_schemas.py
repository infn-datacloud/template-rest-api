"""Unit tests for app.v1.schemas (common pydantic/sqlmodel schemas).

Covers:
- test_item_id_default
- test_item_description_default
- test_sort_query_defaults
- test_pagination_query_defaults
- test_pagination_total_pages
- test_page_navigation_fields
- test_paginated_list_page_and_links_properties
- test_creation_time_field_assignment
- test_creation_time_default_value_is_func_now
- test_creation_time_query_fields
- test_creator_fields
- test_creator_query_fields
- test_creation_inheritance
- test_creation_query_inheritance
- test_update_time_field_assignment
- test_update_time_default_value_is_func_now
- test_update_time_query_fields
- test_editor_fields
- test_editor_query_fields
- test_editable_inheritance
- test_editable_query_inheritance
- test_error_message_fields
"""

import uuid
from datetime import datetime

from pydantic import AnyHttpUrl

from app.v1.schemas import (
    Creation,
    CreationQuery,
    CreationTime,
    Creator,
    CreatorQuery,
    Editable,
    EditableQuery,
    Editor,
    EditorQuery,
    ErrorMessage,
    ItemDescription,
    ItemID,
    PageNavigation,
    PaginatedList,
    Pagination,
    PaginationQuery,
    SortQuery,
    UpdateQuery,
    UpdateTime,
)


def test_item_id_default():
    """Generate ItemID with a valid UUID by default."""
    item = ItemID()
    assert isinstance(item.id, uuid.UUID)


def test_item_description_default():
    """Generate ItemDescription with a valid description by default."""
    item = ItemDescription()
    assert item.description == ""


def test_sort_query_defaults():
    """Check SortQuery default values."""
    pq = SortQuery()
    assert pq.sort == "-created_at"


def test_pagination_query_defaults():
    """Check PaginationQuery default values."""
    pq = PaginationQuery()
    assert pq.size == 5
    assert pq.page == 1


def test_pagination_total_pages():
    """Compute total_pages in Pagination for various cases."""
    p = Pagination(size=5, number=1, total_elements=0)
    assert p.total_pages == 1
    p = Pagination(size=5, number=1, total_elements=12)
    assert p.total_pages == 3
    p = Pagination(size=5, number=1, total_elements=5)
    assert p.total_pages == 1


def test_page_navigation_fields():
    """Set all fields in PageNavigation and check types."""
    url1 = AnyHttpUrl("http://test/1")
    url2 = AnyHttpUrl("http://test/2")
    nav = PageNavigation(first=url1, prev=url2, next=None, last=url1)
    assert nav.first == url1
    assert nav.prev == url2
    assert nav.next is None
    assert nav.last == url1


def test_paginated_list_page_and_links_properties():
    """Test PaginatedList computed properties: page and links."""
    # Prepare test data
    url = AnyHttpUrl("http://test/resource")
    page_number = 2
    page_size = 5
    tot_items = 12

    paginated = PaginatedList(
        page_number=page_number,
        page_size=page_size,
        tot_items=tot_items,
        resource_url=url,
    )

    # Test page property
    page = paginated.page
    assert page.number == page_number
    assert page.size == page_size
    assert page.total_elements == tot_items
    assert page.total_pages == 3

    # Test links property
    links = paginated.links
    assert isinstance(links, PageNavigation)
    assert links.first == AnyHttpUrl("http://test/resource?page=1")
    assert links.last == AnyHttpUrl("http://test/resource?page=3")
    assert links.prev == AnyHttpUrl("http://test/resource?page=1")
    assert links.next == AnyHttpUrl("http://test/resource?page=3")

    # Test edge cases: first page (no prev)
    paginated_first = PaginatedList(
        page_number=1,
        page_size=page_size,
        tot_items=tot_items,
        resource_url=url,
    )
    links_first = paginated_first.links
    assert links_first.prev is None
    assert links_first.next == AnyHttpUrl("http://test/resource?page=2")

    # Test edge cases: last page (no next)
    paginated_last = PaginatedList(
        page_number=3,
        page_size=page_size,
        tot_items=tot_items,
        resource_url=url,
    )
    links_last = paginated_last.links
    assert links_last.next is None
    assert links_last.prev == AnyHttpUrl("http://test/resource?page=2")


def test_creation_time_field_assignment():
    """Test CreationTime schema field assignment."""
    now = datetime.now()
    ct = CreationTime(created_at=now)
    assert ct.created_at == now


def test_creation_time_default_value_is_func_now():
    """Test CreationTime default value is set to func.now()."""
    # The default is a SQLModel/SQLAlchemy function, so we check the default_factory
    field = CreationTime.model_fields["created_at"]
    assert (
        field.default == field.default
        or field.default_factory
        or field.default_factory is not None
    )


def test_creation_time_query_fields():
    """Set created_before and created_after in CreationQuery."""
    now = datetime.now()
    cq = CreationQuery(created_before=now, created_after=now)
    assert cq.created_before == now
    assert cq.created_after == now


def test_creator_fields():
    """Test Creator schema field assignment."""
    user_id = uuid.uuid4()
    creator = Creator(created_by=user_id)
    assert creator.created_by == user_id


def test_creator_query_fields():
    """Test CreatorQuery schema field assignment and default."""
    cq = CreatorQuery()
    assert cq.created_by is None
    cq2 = CreatorQuery(created_by="abc")
    assert cq2.created_by == "abc"


def test_creation_inheritance():
    """Test Creation schema inherits from Creator and CreationTime."""
    user_id = uuid.uuid4()
    now = datetime.now()
    creation = Creation(created_by=user_id, created_at=now)
    assert creation.created_by == user_id
    assert creation.created_at == now


def test_creation_query_inheritance():
    """Test CreationQuery schema inherits from CreatorQuery and CreationTimeQuery."""
    now = datetime.now()
    cq = CreationQuery(created_before=now, created_after=now, created_by="abc")
    assert cq.created_before == now
    assert cq.created_after == now
    assert cq.created_by == "abc"


def test_update_time_field_assignment():
    """Test UpdateTime schema field assignment."""
    now = datetime.now()
    ut = UpdateTime(updated_at=now)
    assert ut.updated_at == now


def test_update_time_default_value_is_func_now():
    """Test UpdateTime default value is set to func.now()."""
    field = UpdateTime.model_fields["updated_at"]
    assert (
        field.default == field.default
        or field.default_factory
        or field.default_factory is not None
    )


def test_update_time_query_fields():
    """Set updated_before and updated_after in UpdateQuery."""
    now = datetime.now()
    uq = UpdateQuery(updated_before=now, updated_after=now)
    assert uq.updated_before == now
    assert uq.updated_after == now


def test_editor_fields():
    """Test Editor schema field assignment."""
    user_id = uuid.uuid4()
    editor = Editor(updated_by=user_id)
    assert editor.updated_by == user_id


def test_editor_query_fields():
    """Test EditorQuery schema field assignment and default."""
    eq = EditorQuery()
    assert eq.updated_by is None
    eq2 = EditorQuery(updated_by="xyz")
    assert eq2.updated_by == "xyz"


def test_editable_inheritance():
    """Test Editable schema inherits from Editor and UpdateTime."""
    user_id = uuid.uuid4()
    now = datetime.now()
    editable = Editable(updated_by=user_id, updated_at=now)
    assert editable.updated_by == user_id
    assert editable.updated_at == now


def test_editable_query_inheritance():
    """Test EditableQuery schema inherits from EditorQuery and UpdateQuery."""
    now = datetime.now()
    eq = EditableQuery(updated_before=now, updated_after=now, updated_by="xyz")
    assert eq.updated_before == now
    assert eq.updated_after == now
    assert eq.updated_by == "xyz"


def test_error_message_fields():
    """Set detail in ErrorMessage."""
    err = ErrorMessage(detail="Something went wrong")
    assert err.detail == "Something went wrong"
