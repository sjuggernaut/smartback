/***
  This query will show SEMG data for treatment session for the user = 4
 */

SELECT *
FROM infra_treatmentsemgdata
WHERE session_id =
      (SELECT id from infra_session WHERE user_id = 4 and type = 'TREATMENT' ORDER BY started_at DESC LIMIT 1)