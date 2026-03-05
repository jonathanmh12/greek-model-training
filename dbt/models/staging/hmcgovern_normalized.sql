WITH base AS (
    SELECT 
        *,
        REGEXP_EXTRACT(reference, '^([^.]+)\.(\d+)\.(\d+)(?:[\[\{\(][^\]\}\)]+[\]\}\)])?\.(\d+)$', 1) AS book_raw,
        REGEXP_EXTRACT(reference, '^([^.]+)\.(\d+)\.(\d+)(?:[\[\{\(][^\]\}\)]+[\]\}\)])?\.(\d+)$', 2) AS chapter,
        REGEXP_EXTRACT(reference, '^([^.]+)\.(\d+)\.(\d+)(?:[\[\{\(][^\]\}\)]+[\]\}\)])?\.(\d+)$', 3) AS verse
    FROM {{ ref('hmcgovern_og_lang_raw') }}
),
normalized AS (
    SELECT 
        *,
        CASE LOWER(book_raw)
            WHEN 'mat' THEN 'matthew'
            WHEN 'mrk' THEN 'mark'
            WHEN 'luk' THEN 'luke'
            WHEN 'jhn' THEN 'john'
            WHEN 'act' THEN 'acts'
            WHEN 'rom' THEN 'romans'
            WHEN '1co' THEN '1 corinthians'
            WHEN '2co' THEN '2 corinthians'
            WHEN 'gal' THEN 'galatians'
            WHEN 'eph' THEN 'ephesians'
            WHEN 'php' THEN 'philippians'
            WHEN 'col' THEN 'colossians'
            WHEN '1th' THEN '1 thessalonians'
            WHEN '2th' THEN '2 thessalonians'
            WHEN '1ti' THEN '1 timothy'
            WHEN '2ti' THEN '2 timothy'
            WHEN 'tit' THEN 'titus'
            WHEN 'phm' THEN 'philemon'
            WHEN 'heb' THEN 'hebrews'
            WHEN 'jas' THEN 'james'
            WHEN '1pe' THEN '1 peter'
            WHEN '2pe' THEN '2 peter'
            WHEN '1jn' THEN '1 john'
            WHEN '2jn' THEN '2 john'
            WHEN '3jn' THEN '3 john'
            WHEN 'jud' THEN 'jude'
            WHEN 'rev' THEN 'revelation'
            ELSE 'nan'
        END AS full_book_name
    FROM base
)
SELECT 
    *,
    full_book_name || ' ' || chapter || ':' || verse AS normalized_ref,
    book_raw || '.' || chapter || '.' || verse AS bcv
FROM normalized