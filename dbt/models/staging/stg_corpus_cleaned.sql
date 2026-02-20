{{ config(materialized='table') }}

with cleaned as (
    select
        row_id,
        source_type,
        source_file_path,
        source_file_name,
        regexp_replace(source_file_name, '_', ' ') as source_label,
        author_id,
        trim(
            regexp_replace(
                regexp_replace(
                    regexp_replace(
                        regexp_replace(
                            coalesce(
                                regexp_extract(raw_text, '(?is)<body[^>]*>(.*?)</body>', 1),
                                raw_text
                            ),
                            '\\\\[nrt]',
                            ' ',
                            'g'
                        ),
                        '(?is)&lt;[^&]*&gt;',
                        ' ',
                        'g'
                    ),
                    '(?is)<[^>]+>',
                    ' ',
                    'g'
                ),
                '\\s+',
                ' ',
                'g'
            )
        ) as cleaned_text
    from {{ ref('raw_corpus') }}
)

select
    row_id,
    source_type,
    source_file_path,
    source_file_name,
    source_label,
    author_id,
    cleaned_text
from cleaned
where cleaned_text is not null
  and cleaned_text <> ''
