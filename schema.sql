DELIMITER //

DROP PROCEDURE IF EXISTS sp_generate_user_batch//

CREATE PROCEDURE sp_generate_user_batch()
BEGIN
    -- Tworzymy tymczasową tabelę na wygenerowaną paczkę, jeśli nie istnieje, 
    -- albo po prostu wrzucamy dane do tabeli wynikowej (lub zwracamy bezpośrednio SELECT-em)
    
    SELECT 
        CONCAT(n_first.name_value, ' ', n_last.name_value) AS name,
        LOWER(CONCAT(n_first.name_value, '.', n_last.name_value, '@', ed.domain_name)) AS email,
        l.country_name AS country
    FROM (
        SELECT locale_code FROM locales ORDER BY RAND() LIMIT 1
    ) chosen_locale
    JOIN locales l ON l.locale_code = chosen_locale.locale_code
    -- Losowanie imienia
    JOIN (
        SELECT locale_code, name_value 
        FROM names 
        WHERE name_type IN ('first_male', 'first_female') 
        ORDER BY RAND() LIMIT 1
    ) n_first ON n_first.locale_code = l.locale_code
    -- Losowanie nazwiska
    JOIN (
        SELECT locale_code, name_value 
        FROM names 
        WHERE name_type = 'last' 
        ORDER BY RAND() LIMIT 1
    ) n_last ON n_last.locale_code = l.locale_code
    -- Losowanie domeny email
    JOIN (
        SELECT locale_code, domain_name 
        FROM email_domains 
        ORDER BY RAND() LIMIT 1
    ) ed ON ed.locale_code = l.locale_code;

END //

DELIMITER ;