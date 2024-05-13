/***
  This query will show Inertial data for calibration session for the user = 4
 */

SELECT *
FROM infra_calibrationstepinertialdata
WHERE session_id =
      (SELECT id from infra_session WHERE user_id = 4 and type = 'CALIBRATION' ORDER BY started_at DESC LIMIT 1)