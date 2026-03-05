WITH parsed AS (
    SELECT
        *,
        TRY_CAST(REGEXP_EXTRACT(reference, '^([^.]+)\.(\d+)\.(\d+)(?:[\[\{\(][^\]\}\)]+[\]\}\)])?\.(\d+)$', 4) AS INT) AS word_order
    FROM {{ ref('hmcgovern_normalized') }}
    WHERE book_raw IS NOT NULL
      AND chapter IS NOT NULL
      AND verse IS NOT NULL
)

SELECT
    bcv                   AS verse_ref,
    normalized_ref,
    STRING_AGG(text, ' ' ORDER BY word_order)        AS text,
    STRING_AGG(translation, ' ' ORDER BY word_order)  AS translation
FROM parsed
WHERE word_order IS NOT NULL
GROUP BY bcv, normalized_ref