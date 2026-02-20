{{ config(materialized='table') }}

with xml_docs as (
    select
        'xml' as source_type,
        filename as source_file_path,
        regexp_extract(filename, '([^/]+)\\.xml$', 1) as source_file_name,
        regexp_extract(filename, '/data/([^/]+)/', 1) as author_id,
        content as raw_text
    from read_text(
        '{{ var("xml_corpus_glob") }}'
    )
),

additional_text as (
    select
        'additional' as source_type,
        filename as source_file_path,
        regexp_extract(filename, '([^/]+)\\.txt$', 1) as source_file_name,
        cast(null as varchar) as author_id,
        content as raw_text
    from read_text(
        '{{ var("additional_text_path") }}'
    )
),

combined_sources as (
    select * from xml_docs
    union all
    select * from additional_text
),

filtered_sources as (
    select
        source_type,
        source_file_path,
        source_file_name,
        author_id,
        raw_text
    from combined_sources
    where raw_text is not null
      and trim(raw_text) <> ''
)

select
    row_number() over () as row_id,
    source_type,
    source_file_path,
    source_file_name,
    author_id,
    raw_text
from filtered_sources
