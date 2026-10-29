DELIMITER //

DROP PROCEDURE IF EXISTS generate_fake_users//

CREATE PROCEDURE generate_fake_users()
BEGIN
    SELECT 
        CONCAT(n_first.name_value, ' ', n_last.name_value) AS name,
        LOWER(CONCAT(n_first.name_value, '.', n_last.name_value, '@', ed.domain_name)) AS email,
        l.country_name AS country
    FROM locales l
    JOIN names n_first ON n_first.locale_code = l.locale_code AND n_first.name_type IN ('first_male', 'first_female')
    JOIN names n_last ON n_last.locale_code = l.locale_code AND n_last.name_type = 'last'
    JOIN email_domains ed ON ed.locale_code = l.locale_code
    ORDER BY RAND()
    LIMIT 10;
END//

DELIMITER ;