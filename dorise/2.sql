INSERT INTO t_statistics_info_min_device_202504 
SELECT
	CONCAT( device_no, DATE_FORMAT( biz_time, '%Y-%m-%d %H:00:00' ) ) AS id,
	device_no AS deviceNo,
	direction,
	SUM( vehicle_nums ) AS vehicleNums,
	DATE_FORMAT( biz_time, '%Y-%m-%d %H:00:00' ) AS bizTime 
FROM
	`t_statistics_info_min_202504` 
WHERE
	biz_time >= "2025-04-11 08:00:00" 
	AND biz_time < "2025-04-11 09:59:59" 
GROUP BY
	bizTime,
	deviceNo,
	direction


