{{ config(materialized='table') }}

{% set author_whitelist = var('author_whitelist') %}

with sentence_candidates as (
    select
        source_type,
        source_file_name as source_file,
        source_label,
        source_file_path,
        author_id,
        unnest(regexp_extract_all(cleaned_text, '[^.;·?]+[.;·?]')) as verse_text
    from {{ ref('stg_corpus_cleaned') }}
),

trimmed as (
    select
        source_type,
        source_file,
        source_label,
        source_file_path,
        author_id,
        trim(verse_text) as verse_text
    from sentence_candidates
),

filtered as (
    select
        source_type,
        source_file,
        source_label,
        source_file_path,
        author_id,
        verse_text
    from trimmed
    where length(verse_text) > 5
      and (
          source_type = 'additional'
          or author_id in (
            {% for author_id in author_whitelist %}
                '{{ author_id }}'{% if not loop.last %}, {% endif %}
            {% endfor %}
          )
      )
)

select
    row_number() over (order by source_file_path, verse_text) as verse_id,
    source_type,
    author_id,
    source_file,
    source_label,
    source_file_path,
    verse_text,
    length(verse_text) as char_count
from filtered
